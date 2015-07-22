"""
Copyright 2015 Paul T. Grogan, Massachusetts Institute of Technology

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Operations class.
"""

import logging
import math

from .lp_solve import LinearProgram
from .lp_solve import Row

class Operations(object):
    def __init__(self):
        pass
    
    def execute(self, controller, context):
        """
        Executes this operations model.
        @param controller: the controller for this operations model
        @type controller: L{Entity}
        @param context: the context of operations
        @type context: L{Context}
        """
        pass
    
    def getStoragePenalty(self, element, context):
        demands = [e for e in context.events
                   if e.isDemand()
                   and element.couldSense(e.generateData())]
        values = [0]
        values.extend(map(lambda d: d.getValueAt(0), demands))
        values = list(set(values))
        values.sort()
        counts = map(lambda v: len([d for d in demands
                                    if d.getValueAt(0) == v]), values)
        counts[0] += len(context.events) - len(demands)
        expValMax = reduce(lambda e, v:
                           e + v*(math.pow(sum(counts[0:values.index(v)+1]), 1)
                                  - math.pow(sum(counts[0:values.index(v)]), 1))
                           / math.pow(sum(counts),1), values)
        return -1*expValMax

class DynamicOperations(Operations):
    def __init__(self, planningHorizon=6, storagePenalty=-10, islPenalty=-10):
        super(DynamicOperations, self).__init__()
        self.planningHorizon = planningHorizon
        self.storagePenalty = storagePenalty
        self.islPenalty = islPenalty
    
    def execute(self, controller, context):
        """
        Executes this operations model.
        @param controller: the controller for this operations model
        @type controller: L{Entity}
        @param context: the context of operations
        @type context: L{Context}
        """
        minTime = context.time
        maxTime = min(context.maxTime, context.time + self.planningHorizon)
        
        with LinearProgram(name='OFS LP for {}'.format(controller.name)) as lp:
            # columns
            S = []      # S[i][j]: spacecraft i senses demand j
            E_d = []    # E_d[t][i][j]: at time t spacecraft i holds data for demand j
            E_c0 = []   # E_c0[i][j]: spacecraft i initially holds data for contract j
            E_c = []    # E_c[t][i][j]: at time t spacecraft i holds data for contract j
            T_d = []    # T_d[t][i][j][k][l]: at time t transmit data from spacecraft i to ground station j using protocol k for demand l
            T_c = []    # T_c[t][i][j][k][l]: at time t transmit data from spacecraft i to ground station j using protocol k for contract l
            L_d = []    # L_d[t][i][j][k][l]: at time t transmit data from isl spacecraft i to isl spacecraft j using protocol k for demand l
            L_c = []    # L_c[t][i][j][k][l]: at time t transmit data from isl spacecraft i to isl spacecraft j using protocol k for contract l
            R_d = []    # R_d[t][i][j]: at time t resolve data in system i for demand j
            R_c = []    # R_c[t][i][j]: at time t resolve data in system i for contract j
            
            C = []      # constraints
            J = Row()   # objective function
            
            demands = [e for e in context.currentEvents if e.isDemand()]
            elements = self.getElements(controller)
            federates = self.getFederates(controller)
            satellites = [e for e in elements if e.isSpace()]
            satellitesISL = [e for e in satellites
                             if any(m for m in e.modules
                                    if m.isTransceiver() and m.isISL())]
            stations = [e for e in elements if e.isGround()]
            contracts = self.getContracts(controller)
            
            protocolsSGL = list(set([m.protocol for e in elements for m in e.modules
                                     if m.isTransceiver() and m.isSGL()]))
            protocolsISL = list(set([m.protocol for e in elements for m in e.modules
                                     if m.isTransceiver() and m.isISL()]))
            phenomena = ['VIS','SAR',None]
            
            for i, satellite in enumerate(satellites):
                S.insert(i, [])
                for j, demand in enumerate(demands):
                    # satellite i senses data for demand j
                    S[i].insert(j, lp.addColumn('{}-S-{}'.format(
                        satellite.name, demand.name), True))
                    # constrain sensing per spacecraft
                    lp.addConstraint(Row().add(S[i][j], 1), 'LE',
                                     1 if satellite.canSense(demand) else 0,
                                     '{} can sense {}'.format(satellite.name,
                                                              demand.name))
                for phenomenon in phenomena:
                    r = Row()
                    for j, demand in enumerate(demands):
                        if phenomenon is None or demand.phenomenon == phenomenon:
                            r.add(S[i][j], demand.size)
                    # constrain maximum data sensed by satellite
                    lp.addConstraint(r, 'LE',
                                     min(satellite.getMaxSensed(phenomenon)
                                         - satellite.getSensed(phenomenon),
                                         satellite.getMaxStored(phenomenon)
                                         - satellite.getStored(phenomenon)),
                                     '{} max sense {}'.format(satellite.name,
                                                              phenomenon))
                # set initial data stored
                E_c0.insert(i, [])
                for j, contract in enumerate(contracts):
                    E_c0[i].insert(j, 1 if any(d.contract is contract
                                               for m in satellite.modules
                                               for d in m.data) else 0)
            
            for j, demand in enumerate(demands):
                r = Row()
                for i, satellite in enumerate(satellites):
                    r.add(S[i][j], 1)
                lp.addConstraint(r, 'LE', 1, '{} max sensed'.format(demand.name))
            
            for t, time in enumerate(range(minTime, maxTime+1)):
                E_d.insert(t, [])
                E_c.insert(t, [])
                for i, satellite in enumerate(satellites):
                    E_d[t].insert(i, [])
                    E_c[t].insert(i, [])
                    for j, demand in enumerate(demands):
                        # satellite i stores data for new contract j
                        E_d[t][i].insert(j, lp.addColumn('{}-E-{}@{}'.format(
                            satellite.name, demand.name, time), True))
                        # penalty for opportunity cost
                        J.add(E_d[t][i][j], demand.size*(self.storagePenalty
                              if self.storagePenalty is not None
                              else self.getStoragePenalty(satellite, context)))
                    for j, contract in enumerate(contracts):
                        # satellite i stores data for contract j
                        E_c[t][i].insert(j, lp.addColumn('{}-E-{}@{}'.format(
                            satellite.name, contract.name, time), True))
                        # penalty for opportunity cost
                        J.add(E_c[t][i][j], contract.demand.size*(self.storagePenalty
                              if self.storagePenalty is not None
                              else self.getStoragePenalty(satellite, context)))
                    for phenomenon in phenomena:
                        r = Row()
                        for j, demand in enumerate(demands):
                            if phenomenon is None or demand.phenomenon == phenomenon:
                                r.add(E_d[t][i][j], demand.size)
                        for j, contract in enumerate(contracts):
                            if phenomenon is None or demand.phenomenon == phenomenon:
                                r.add(E_c[t][i][j], contract.demand.size)
                        # constrain data stored in satellite
                        lp.addConstraint(r, 'LE', satellite.getMaxStored(phenomenon),
                                         '{} max store {} at {}'.format(
                                            satellite.name, phenomenon, time))
                T_d.insert(t, [])
                T_c.insert(t, [])
                for i, satellite in enumerate(satellites):
                    T_d[t].insert(i, [])
                    T_c[t].insert(i, [])
                    txLocation = context.propagate(satellite.location, time-context.time)
                    for j, station in enumerate(stations):
                        T_d[t][i].insert(j, [])
                        T_c[t][i].insert(j, [])
                        rxLocation = context.propagate(station.location, time-context.time)
                        for k, protocol in enumerate(protocolsSGL):
                            T_d[t][i][j].insert(k, [])
                            T_c[t][i][j].insert(k, [])
                            r = Row()
                            maxSize = 0
                            for l, demand in enumerate(demands):
                                T_d[t][i][j][k].insert(l, lp.addColumn(
                                    '{}-T({}/{})-{}@{})'.format(
                                        satellite.name, demand.name,
                                        protocol, station.name, time), True))
                                r.add(T_d[t][i][j][k][l], demand.size)
                                maxSize = max(maxSize, demand.size
                                              if satellite.couldTransmit(
                                                protocol, demand.generateData(),
                                                station, txLocation, rxLocation)
                                              and station.couldReceive(
                                                protocol, demand.generateData(),
                                                satellite, txLocation, rxLocation)
                                              else 0)
                            for l, contract in enumerate(contracts):
                                T_c[t][i][j][k].insert(l, lp.addColumn(
                                    '{}-T({}/{})-{}@{})'.format(
                                        satellite.name, contract.name,
                                        protocol, station.name, time), True))
                                r.add(T_c[t][i][j][k][l])
                                maxSize = max(maxSize, demand.size
                                              if satellite.couldTransmit(
                                                protocol, contract.demand.generateData(),
                                                station, txLocation, rxLocation)
                                              and station.couldReceive(
                                                protocol, contract.demand.generateData(),
                                                satellite, txLocation, rxLocation)
                                              else 0)
                            # constrain transmission by visibility
                            lp.addConstraint(r, 'LE', maxSize, '{}-{} ({}) visibility at {}'
                                             .format(satellite.name, station.name, protocol, time))
                for i, satellite in enumerate(satellites):
                    for k, protocol in enumerate(protocolsSGL):
                        r = Row()
                        for j, station in enumerate(stations):
                            for l, demand in enumerate(demands):
                                r.add(T_d[t][i][j][k][l], demand.size)
                            for l, contract in enumerate(contracts):
                                r.add(T_c[t][i][j][k][l], contract.demand.size)
                        # constrain data transmitted by satellite
                        lp.addConstraint(r, 'LE', satellite.getMaxTransmitted(protocol)
                                         - (satellite.getTransmitted(protocol)
                                            if time == minTime else 0),
                                         '{} max transmit {} at {}'
                                         .format(satellite.name, protocol, time))
                for j, station in enumerate(stations):
                    for k, protocol in enumerate(protocolsSGL):
                        r = Row()
                        for i, satellite in enumerate(satellites):
                            for l, demand in enumerate(demands):
                                r.add(T_d[t][i][j][k][l], demand.size)
                            for l, contract in enumerate(contracts):
                                r.add(T_c[t][i][j][k][l], contract.demand.size)
                        # constrain data received by station
                        lp.addConstraint(r, 'LE', station.getMaxReceived(protocol)
                                         - (station.getReceived(protocol)
                                            if time == minTime else 0),
                                         '{} max receive {} at {}'
                                         .format(station.name, protocol, time))
                L_d.insert(t, [])
                L_c.insert(t, [])
                for i, txSatellite in enumerate(satellitesISL):
                    L_d[t].insert(i, [])
                    L_c[t].insert(i, [])
                    txLocation = context.propagate(txSatellite.location, time-context.time)
                    for j, rxSatellite in enumerate(satellitesISL):
                        L_d[t][i].insert(j, [])
                        L_c[t][i].insert(j, [])
                        rxLocation = context.propagate(rxSatellite.location, time-context.time)
                        for k, protocol in enumerate(protocolsISL):
                            L_d[t][i][j].insert(k, [])
                            L_c[t][i][j].insert(k, [])
                            r = Row()
                            maxSize = 0
                            for l, demand in enumerate(demands):
                                L_d[t][i][j][k].insert(l, lp.addColumn(
                                    '{}-T({}/{})-{}@{})'.format(
                                        txSatellite.name, demand.name,
                                        protocol, rxSatellite.name, time), True))
                                # small penalty for opportunity cost
                                J.add(L_d[t][i][j][k][l], self.islPenalty*demand.size)
                                r.add(L_d[t][i][j][k][l], demand.size)
                                maxSize = max(maxSize, demand.size
                                              if txSatellite.couldTransmit(
                                                protocol, demand.generateData(),
                                                rxSatellite, txLocation, rxLocation)
                                              and rxSatellite.couldReceive(
                                                protocol, demand.generateData(),
                                                txSatellite, txLocation, rxLocation)
                                              else 0)
                            for l, contract in enumerate(contracts):
                                L_c[t][i][j][k].insert(l, lp.addColumn(
                                    '{}-T({}/{})-{}@{})'.format(
                                        txSatellite.name, contract.name,
                                        protocol, rxSatellite.name, time), True))
                                # small penalty for opportunity cost
                                J.add(L_c[t][i][j][k][l], self.islPenalty*contract.demand.size)
                                r.add(L_c[t][i][j][k][l])
                                maxSize = max(maxSize, demand.size
                                              if txSatellite.couldTransmit(
                                                protocol, contract.demand.generateData(),
                                                rxSatellite, txLocation, rxLocation)
                                              and rxSatellite.couldReceive(
                                                protocol, contract.demand.generateData(),
                                                txSatellite, txLocation, rxLocation)
                                              else 0)
                            # constrain transmission by visibility
                            lp.addConstraint(r, 'LE', maxSize, '{}-{} ({}) visibility at {}'
                                             .format(txSatellite.name, rxSatellite.name,
                                                     protocol, time))
                for i, txSatellite in enumerate(satellitesISL):
                    for k, protocol in enumerate(protocolsISL):
                        r = Row()
                        for j, rxSatellite in enumerate(satellitesISL):
                            for l, demand in enumerate(demands):
                                r.add(L_d[t][i][j][k][l], demand.size)
                            for l, contract in enumerate(contracts):
                                r.add(L_c[t][i][j][k][l], contract.demand.size)
                        # constrain data transmitted by satellite
                        lp.addConstraint(r, 'LE', txSatellite.getMaxTransmitted(protocol)
                                         - (txSatellite.getTransmitted(protocol)
                                            if time == minTime else 0),
                                         '{} max transmit {} at {}'
                                         .format(txSatellite.name, protocol, time))
                for j, rxSatellite in enumerate(satellitesISL):
                    for k, protocol in enumerate(protocolsISL):
                        r = Row()
                        for i, txSatellite in enumerate(satellitesISL):
                            for l, demand in enumerate(demands):
                                r.add(L_d[t][i][j][k][l], demand.size)
                            for l, contract in enumerate(contracts):
                                r.add(L_c[t][i][j][k][l], contract.demand.size)
                        # constrain data received by station
                        lp.addConstraint(r, 'LE', rxSatellite.getMaxReceived(protocol)
                                         - (rxSatellite.getReceived(protocol)
                                            if time == minTime else 0),
                                         '{} max receive {} at {}'
                                         .format(rxSatellite.name, protocol, time))
                R_d.insert(t, [])
                R_c.insert(t, [])
                for i, element in enumerate(elements):
                    R_d[t].insert(i, [])
                    R_c[t].insert(i, [])
                    for j, demand in enumerate(demands):
                        R_d[t][i].insert(j, lp.addColumn('{}-R-{}@{}'.format(
                            element.name, demand.name, time), True))
                        # high penalty for defaulting on new contract
                        J.add(R_d[t][i][j], demand.getValueAt(time-context.time)
                              if element.isGround() else -1e9)
                    for j, contract in enumerate(contracts):
                        R_c[t][i].insert(j, lp.addColumn('{}-R-{}@{}'.format(
                            element.name, contract.name, time), True))
                        if element.isGround():
                            J.add(R_c[t][i][j], contract.demand.getValueAt(
                                contract.elapsedTime + time-context.time))
                        else:
                            # high penalty for bankruptcy
                            J.add(R_c[t][i][j], contract.demand.getDefaultValue()
                                  if self.getContractOwner(contract, controller).cash
                                  + contract.demand.getDefaultValue() > 0
                                  else -1e9)
                for i, satellite in enumerate(satellites):
                    R_i = elements.index(satellite)
                    for j, demand in enumerate(demands):
                        r = Row()
                        if time==minTime:
                            r.add(S[i][j], 1)
                        else:
                            r.add(E_d[t-1][i][j],1)
                        r.add(E_d[t][i][j],-1)
                        r.add(R_d[t][R_i][j],-1)
                        for k, station in enumerate(stations):
                            for l, protocol in enumerate(protocolsSGL):
                                r.add(T_d[t][i][k][l][j],-1)
                        if satellite in satellitesISL:
                            isl_i = satellitesISL.index(satellite)
                            for k, rxSatellite in enumerate(satellitesISL):
                                for l, protocol in enumerate(protocolsISL):
                                    r.add(L_d[t][isl_i][k][l][j],-1)
                                    r.add(L_d[t][k][isl_i][l][j],1)
                        # constrain net flow of new contracts at each satellite
                        lp.addConstraint(r, 'EQ', 0, '{} net flow {} at {}'
                                         .format(satellite.name, demand.name, time))
                    for j, contract in enumerate(contracts):
                        r = Row()
                        if time==minTime:
                            # existing contracts are initial conditions
                            pass
                        else:
                            r.add(E_c[t-1][i][j],1)
                        r.add(E_c[t][i][j],-1)
                        r.add(R_c[t][R_i][j],-1)
                        for k, station in enumerate(stations):
                            for l, protocol in enumerate(protocolsSGL):
                                r.add(T_c[t][i][k][l][j],-1)
                        if satellite in satellitesISL:
                            isl_i = satellitesISL.index(satellite)
                            for k, rxSatellite in enumerate(satellitesISL):
                                for l, protocol in enumerate(protocolsISL):
                                    r.add(L_c[t][isl_i][k][l][j],-1)
                                    r.add(L_c[t][k][isl_i][l][j],1)
                        # constrain net flow of contracts at each satellite
                        lp.addConstraint(r, 'EQ', -1*(E_c0[i][j] if time == minTime else 0),
                                         '{} net flow {} at {}'
                                         .format(satellite.name, contract.name, time))
                if time+1 > maxTime and self.planningHorizon > 0:
                    for i, satellite in enumerate(satellites):
                        r = Row()
                        for j, demand in enumerate(demands):
                            r.add(E_d[t][i][j],1)
                        for j, contract in enumerate(contracts):
                            r.add(E_c[t][i][j],1)
                        # constrain boundary flow of each satellite
                        lp.addConstraint(r, 'EQ', 0, '{} boundary flow'
                                         .format(satellite.name))
                for k, station in enumerate(stations):
                    R_k = elements.index(station)
                    for j, demand in enumerate(demands):
                        r = Row()
                        r.add(R_d[t][R_k][j],-1)
                        for i, satellite in enumerate(satellites):
                            for l, protocol in enumerate(protocolsSGL):
                                r.add(T_d[t][i][k][l][j],1)
                        # constrain net flow of new contracts at each station
                        lp.addConstraint(r, 'EQ', 0, '{} net flow {} at {}'
                                         .format(station.name, demand.name, time))
                    for j, contract in enumerate(contracts):
                        r = Row()
                        r.add(R_c[t][R_k][j],-1)
                        for k, station in enumerate(stations):
                            for l, protocol in enumerate(protocolsSGL):
                                r.add(T_c[t][i][k][l][j],1)
                        # constrain net flow of contracts at each station
                        lp.addConstraint(r, 'EQ', 0, '{} net flow {} at {}'
                                         .format(station.name, contract.name, time))
            for federate in federates:
                r = Row()
                for j, demand in enumerate(demands):
                    for i, element in enumerate(elements):
                        r.add(R_d[0][i][j], (demand.getValueAt(0)
                                             if element.isGround()
                                             else demand.getDefaultValue()))
                for j, contract in enumerate(contracts):
                    for i, element in enumerate(elements):
                        r.add(R_c[0][i][j], (contract.demand.getValueAt(contract.elapsedTime)
                                             if element.isGround()
                                             else contract.demand.getDefaultValue()))
                lp.addConstraint(r, 'GE', -1 - federate.cash,
                                 '{} net cash must be positive'
                                 .format(federate.name))
                        
            lp.setObjective(J, False)
            code, description = lp.solve()
            if code > 1:
                logging.error(description)
                with open('lp_debug.txt', 'w+') as f:
                    f.write(lp.dumpProgram())
            else:
                def _transportContract(operations, satellite, contract, context):
                    fed1 = operations.getSystemOwner(satellite, controller)
                    fed2 = operations.getContractOwner(contract, controller)
                    i = satellites.index(satellite)
                    R_i = elements.index(satellite)
                    j = contracts.index(contract)
                    data = fed1.getData(contract)
                    if data is not None:
                        if lp.get(R_c[0][R_i][j]) > 0:
                            fed2.default(contract, context)
                        elif lp.get(E_c[0][i][j]) > 0:
                            satellite.store(data)
                        elif any(any(lp.get(T_c[0][i][k][l][j])
                                     for k, station in enumerate(stations))
                                 for l, protocol in enumerate(protocolsSGL)):
                            for k, station in enumerate(stations):
                                for l, protocol in enumerate(protocolsSGL):
                                    if(lp.get(T_c[0][i][k][l][j])):
                                        fed1.transport(protocol, data,
                                                       satellite, station)
                                        fed2.resolve(contract, context)
                        elif satellite in satellitesISL:
                            isl_i = satellitesISL.index(satellite)
                            for k, rxSatellite in enumerate(satellitesISL):
                                for l, protocol in enumerate(protocolsISL):
                                    if(lp.get(L_c[0][i][k][l][j])):
                                        fed1.transport(protocol, data,
                                                       satellite, rxSatellite)
                                        _transportContract(operations, rxSatellite,
                                                                contract, context)
                def _transportDemand(operations, satellite, demand, context):
                    fed1 = operations.getSystemOwner(satellite, controller)
                    fed2 = operations.getDemandOwner(demand, controller)
                    i = satellites.index(satellite)
                    R_i = elements.index(satellite)
                    j = demands.index(demand)
                    contract = fed2.getContract(demand)
                    data = fed1.getData(contract)
                    if contract is not None and data is not None:
                        if lp.get(R_d[0][R_i][j]) > 0:
                            fed2.default(contract, context)
                        elif lp.get(E_d[0][i][j]) > 0:
                            satellite.store(data)
                        elif any(any(lp.get(T_d[0][i][k][l][j])
                                     for k, station in enumerate(stations))
                                 for l, protocol in enumerate(protocolsSGL)):
                            for k, station in enumerate(stations):
                                for l, protocol in enumerate(protocolsSGL):
                                    if(lp.get(T_d[0][i][k][l][j])):
                                        fed1.transport(protocol, data,
                                                       satellite, station)
                                        fed2.resolve(contract, context)
                        elif satellite in satellitesISL:
                            isl_i = satellitesISL.index(satellite)
                            for k, rxSatellite in enumerate(satellitesISL):
                                for l, protocol in enumerate(protocolsISL):
                                    if(lp.get(L_d[0][i][k][l][j])):
                                        fed1.transport(protocol, data,
                                                       satellite, rxSatellite)
                                        _transportDemand(operations, rxSatellite,
                                                              demand, context)
                
                # first, transport contracts to resolution
                for j, contract in enumerate(contracts):
                    if any(lp.get(R_c[0][i][j]) > 0
                           for i, element in enumerate(elements)):
                        logging.debug('Transporting contract {} for resolution...'
                                      .format(contract.name))
                        satellite = next(e for e in satellites
                                         if any(any(d.contract is contract
                                                    for d in m.data)
                                                for m in e.modules))
                        _transportContract(self, satellite, contract, context)
                    
                # second, sense and transport demands to resolution
                for j, demand in enumerate(demands):
                    if any(lp.get(R_d[0][i][j]) > 0
                           for i, element in enumerate(elements)):
                        logging.debug('Sensing and transporting demand {} for resolution...'
                                      .format(demand.name))
                        satellite = next(e for i, e in enumerate(satellites)
                                         if lp.get(S[i][j]) > 0)
                        federate = self.getSystemOwner(satellite, controller)
                        contract = federate.contract(demand, context)
                        federate.senseAndStore(contract, satellite, context)
                        _transportDemand(self, satellite, demand, context)
                
                # third, sense all demands to be stored
                for j, demand in enumerate(demands):
                    if (all(lp.get(R_d[0][i][j]) < 1
                            for i, element in enumerate(elements))
                        and any(lp.get(S[i][j]) > 0
                                 for i, element in enumerate(satellites))):
                        logging.debug('Sensing demand {} for storage...'
                                      .format(demand.name))
                        satellite = next(e for i, e in enumerate(satellites)
                                         if lp.get(S[i][j]) > 0)
                        federate = self.getSystemOwner(satellite, controller)
                        contract = federate.contract(demand, context)
                        federate.senseAndStore(contract, satellite, context)
                        
                # fourth, transport demands to storage
                for j, demand in enumerate(demands):
                    if (all(lp.get(R_d[0][i][j]) < 1
                            for i, element in enumerate(elements))
                        and any(lp.get(S[i][j]) > 0
                                 for i, element in enumerate(satellites))):
                        logging.debug('Transporting demand {} for storage...'
                                      .format(demand.name))
                        satellite = next(e for i, e in enumerate(satellites)
                                         if lp.get(S[i][j]) > 0)
                        _transportDemand(self, satellite, demand, context)
                
                # finally, transport contracts to storage
                for j, contract in enumerate(contracts):
                    if all(lp.get(R_c[0][i][j]) < 1
                           for i, element in enumerate(elements)):
                        logging.debug('Transporting contract {} for storage...'
                                      .format(contract.name))
                        satellite = next(e for e in satellites
                                         if any(any(d.contract is contract
                                                    for d in m.data)
                                                for m in e.modules))
                        _transportContract(self, satellite, contract, context)
    
    def getElements(self, controller):
        return controller.elements[:] # FIXME
    
    def getFederates(self, controller):
        return [controller] # FIXME
    
    def getContracts(self, controller):
        return controller.contracts[:] # FIXME
    
    def getSystemOwner(self, system, controller):
        return controller # FIXME
    
    def getContractOwner(self, contract, controller):
        return controller # FIXME
    
    def getDemandOwner(self, demand, controller):
        return controller # FIXME