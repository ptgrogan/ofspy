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
Element class.
"""

import logging

from .entity import Entity

class Element(Entity):
    def __init__(self, name=None, cost=0, capacity=0, modules=None):
        """
        @param name: the name of this element
        @type name: L{str}
        @param location: the location of this element
        @type location: L{Location}
        @param cost: the cost of this element
        @type cost: L{float}
        @param capacity: the capacity for modules
        @type capacity: L{int}
        @param modules: the set of modules
        @type modules: L{list}
        """
        Entity.__init__(self, name=name)
        self._initLocation = None
        self.location = self._initLocation
        self._nextLocation = None
        self.cost = cost
        self.capacity = capacity
        if modules is None:
            self._initModules = []
        else:
            self._initModules = modules[:]
        self.modules = self._initModules
    
    def getContentsSize(self):
        """
        Gets the total size of modules in this element.
        @return: L{float}
        """
        return sum(m.size for m in self.modules)
    
    def isCommissioned(self):
        """
        Checks if this element is commissioned.
        @return: L{bool}
        """
        return self.location is not None
    
    def canCommission(self, location, context):
        """
        Checks if this element can be commissioned at a location.
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return True
    
    def commission(self, location, context):
        """
        Commissions this element at a location.
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if self.canCommission(location, context):
            self.location = location
            return True
        return False
    
    def getDesignCost(self):
        """
        Gets the total design cost for this element.
        @return: L{float}
        """
        return self.cost + sum(m.cost for m in self.modules)
    
    def getCommissionCost(self, location, context):
        """
        Gets the commission cost for this element.
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{float}
        """
        return 0
    
    def getDecommissionValue(self):
        """
        Gets the decommission value of this element.
        @return: L{float}
        """
        return 0
    
    def isGround(self):
        """
        Checks if this is a ground element.
        @return: L{bool}
        """
        return False
    
    def isSpace(self):
        """
        Checks if this is a space element.
        @return: L{bool}
        """
        return False
    
    def couldTransmit(self, protocol, data, rxElement, txLocation, rxLocation):
        """
        Checks if this element could transmit data (state-independent).
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @param txLocation: the transmitting location
        @type txLocation: L{Location}
        @param rxLocation: the receiving location
        @type rxLocation: L{Location}
        @return: L{bool}
        """        
        return any(t.isTransceiver()
                   and t.protocol == protocol
                   and any(r.isTransceiver()
                           and r.protocol == protocol
                           and t.couldTransmit(data, r, txLocation, rxLocation)
                           for r in rxElement.modules)
                   for t in self.modules)
    
    def canTransmit(self, protocol, data, rxElement):
        """
        Checks if this element can transmit data (state-dependent).
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @return: L{bool}
        """
        txLocation = self.location
        rxLocation = rxElement.location
        if  self.isCommissioned() \
                and rxElement.isCommissioned() \
                and self.couldTransmit(protocol, data, rxElement, txLocation, rxLocation):
            container = next((m for m in self.modules if data in m.data), None)
            return container is not None \
                    and any(t.isTransceiver()
                            and t.protocol == protocol
                            and self.canTransfer(data, container, t)
                            and any(r.isTransceiver()
                                    and r.protocol == protocol
                                    and t.canTransmit(data, r, txLocation, rxLocation)
                                    for r in rxElement.modules)
                            for t in self.modules)
        return False
    
    def transmit(self, protocol, data, rxElement):
        """
        Transmits data from this element
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @return: L{bool}
        """
        txLocation = self.location
        rxLocation = rxElement.location
        if self.canTransmit(protocol, data, rxElement):
            container = next((m for m in self.modules if data in m.data), None)
            if container is not None \
                    and any(t.isTransceiver()
                            and t.protocol == protocol
                            and self.canTransfer(data, container, t)
                            and any(r.isTransceiver()
                                    and r.protocol == protocol
                                    and t.canTransmit(data, r, txLocation, rxLocation)
                                    and self.transfer(data, container, t)
                                    and t.transmit(data, r, txLocation, rxLocation)
                                    for r in rxElement.modules)
                            for t in self.modules):
                logging.debug(
                    '{0} transmitted {1} to {2} via {3}'
                    .format(self.name, str(data), rxElement.name, protocol))
                self.trigger('transmit', self, protocol, data, rxElement)
                return True
        logging.warning('{0} could not transmit {1} to {2} via {3}'
                        .format(self.name, str(data), rxElement.name, protocol))
        return False
    
    def couldReceive(self, protocol, data, txElement, txLocation, rxLocation):
        """
        Checks if this element could receive data (state-independent).
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @param txLocation: the transmitting location
        @type txLocation: L{Location}
        @param rxLocation: the receiving location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return any(r.isTransceiver()
                   and r.protocol == protocol
                   and any(t.isTransceiver()
                           and t.protocol == protocol
                           and r.couldReceive(data, r, txLocation, rxLocation)
                           for t in txElement.modules)
                   for r in self.modules)
    
    def canReceive(self, protocol, data, txElement):
        """
        Checks if this element could receive data (state-dependent).
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @return: L{bool}
        """
        rxLocation = self.location
        txLocation = txElement.location
        if self.isCommissioned() \
                and txElement.isCommissioned() \
                and self.couldReceive(protocol, data, txElement, txLocation, rxLocation):
            return any(r.isTransceiver()
                       and r.protocol == protocol
                       and any(t.isTransceiver()
                               and t.protocol == protocol
                               and r.canReceive(data, t, txLocation, rxLocation)
                               for t in txElement.modules)
                       for r in self.modules)
        return False
    
    def receive(self, protocol, data, txElement):
        """
        Receives data with this element.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transmit
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @return: L{bool}
        """
        rxLocation = self.location
        txLocation = txElement.location
        if self.canReceive(protocol, data, txElement):
            if any(r.isTransceiver()
                    and r.protocol == protocol
                    and any(t.isTransceiver()
                            and t.protocol == protocol
                            and r.receive(data, t, txLocation, rxLocation)
                            for t in txElement.modules)
                    for r in self.modules):
                logging.debug(
                    '{0} received {1} from {2} via {3}'
                    .format(self.name, str(data), txElement.name, protocol))
                self.trigger('receive', self, protocol, data, txElement)
                return True
        logging.warning('{0} could not receive {1} from {2} via {3}'
                        .format(self.name, str(data), txElement.name, protocol))
        return False
    
    def couldTransfer(self, data, origin, destination):
        """
        Checks if this element could transfer data between modules (state-independent).
        @param data: the data to transfer
        @type data: L{Data}
        @param origin: the origin module
        @type origin: L{Module}
        @param destination: the receiving module
        @type destination: L{Module}
        @return: L{bool}
        """
        return (origin in self.modules
                and destination in self.modules
                and (origin is destination
                     or (origin.couldTransferOut(data)
                         and destination.couldTransferIn(data))
                     or origin.couldExchange(data, destination)))
            
    def canTransfer(self, data, origin, destination):
        """
        Checks if this element can transfer data between modules (state-dependent).
        @param data: the data to transfer
        @type data: L{Data}
        @param origin: the origin module
        @type origin: L{Module}
        @param destination: the receiving module
        @type destination: L{Module}
        @return: L{bool}
        """
        return (self.isCommissioned()
                and self.couldTransfer(data, origin, destination)
                and (origin is destination
                     or (origin.canTransferOut(data)
                         and destination.canTransferIn(data))
                     or origin.canExchange(data, destination)))
                
    def transfer(self, data, origin, destination):
        """
        Transfers data between two modules in this element.
        @param data: the data to transfer
        @type data: L{Data}
        @param origin: the origin module
        @type origin: L{Module}
        @param destination: the receiving module
        @type destination: L{Module}
        @return: L{bool}
        """
        if self.canTransfer(data, origin, destination):
            if origin is destination:
                return True
            elif origin.canTransferOut(data) \
                    and destination.canTransferIn(data) \
                    and origin.transferOut(data) \
                    and destination.transferIn(data):
                logging.debug(
                    '{0} transferred {1} between modules'
                    .format(self.name, str(data)))
                self.trigger('transfer', self, data, origin, destination)
                return True
            elif origin.canExchange(data, destination) \
                    and origin.exchange(data, destination):
                logging.debug(
                    '{0} exchanged {1} between modules'
                    .format(self.name, str(data)))
                self.trigger('transfer', self, data, origin, destination)
                return True
        logging.warning('{0} could not transfer {1} between modules'
                        .format(self.name, str(data)))
        return False
        
    def couldStore(self, data):
        """
        Checks if this element could store data (state-independent).
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        return any(m.isStorage() and m.couldStore(data) for m in self.modules)
    
    def canStore(self, data):
        """
        Checks if this element can store data (state-dependent).
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        if self.isCommissioned() \
                and self.couldStore(data):
            container = next((m for m in self.modules
                              if data in m.data), None)
            return ((container is not None
                     and container.isStorage())
                or ((container is None
                     or container.canTransferOut(data))
                    and any(m.isStorage()
                            and m.canStore(data)
                            for m in self.modules)))
        return False
    
    def store(self, data):
        """
        Stores data in this element.
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        if self.canStore(data):
            container = next((m for m in self.modules
                              if data in m.data), None)
            if container is None:
                if any(m.isStorage()
                        and not m.isSensor()
                        and m.canStore(data)
                        and m.store(data)
                        for m in self.modules):
                    logging.debug(
                        '{0} stored new {1} in a storage module'
                        .format(self.name, str(data)))
                    self.trigger('store', self, data)
                    return True
                elif any(m.isStorage()
                        and m.isSensor()
                        and m.canStore(data)
                        and m.store(data)
                        for m in self.modules):
                    logging.debug(
                        '{0} stored new {1} in a sensor module'
                        .format(self.name, str(data)))
                    self.trigger('store', self, data)
                    return True
            else:
                if (container.isStorage()
                      and container.isSensor()):
                    logging.debug(
                        '{0} already stored {1} in a sensor module'
                        .format(self.name, str(data)))
                    return True
                elif (any(m.isStorage()
                          and m.isSensor()
                          and m.canStore(data)
                          and container.transferOut(data)
                          and m.store(data)
                          for m in self.modules)):
                    logging.debug(
                        '{0} stored {1} in a sensor module'
                        .format(self.name, str(data)))
                    self.trigger('store', self, data)
                    return True
                elif (container.isStorage()
                      and not container.isSensor()):
                    logging.debug(
                        '{0} already stored {1} in a storage module'
                        .format(self.name, str(data)))
                    return True
                elif (any(m.isStorage()
                          and not m.isSensor()
                          and m.canStore(data)
                          and container.transferOut(data)
                          and m.store(data)
                          for m in self.modules)):
                    logging.debug(
                        '{0} stored {1} in a storage module'
                        .format(self.name, str(data)))
                    self.trigger('store', self, data)
                    return True
        else:
            # cannot directly store data: try to exchange
            container = next((m for m in self.modules
                              if data in m.data), None)
            if (container is not None
                and any(module.isStorage()
                        and module.isSensor()
                        and self.canTransfer(data, container, module)
                        and self.transfer(data, container, module)
                        for module in self.modules)):
                logging.info('{0} stored {1} in a sensor module via exchange'
                             .format(self.name, str(data)))
                return True
            elif (container is not None
                and any(module.isStorage()
                        and not module.isSensor()
                        and self.canTransfer(data, container, module)
                        and self.transfer(data, container, module)
                        for module in self.modules)):
                logging.info('{0} stored {1} in a storage module via exchange'
                             .format(self.name, str(data)))
                return True
        logging.warning('{0} could not store {1}'
                        .format(self.name, str(data)))
        return False
    
    def couldSense(self, data):
        """
        Checks if this element could sense data (state-independent).
        @param data: the data to sense
        @type data: L{Data}
        @return: L{bool}
        """
        return self.couldStore(data) and \
                any(m.isSensor()
                    and m.couldSense(data)
                    for m in self.modules)
    
    def canSense(self, demand):
        """
        Checks if this element could sense data (state-dependent).
        @param demand: the demand for which to sense data
        @type demand: L{Demand}
        @return: L{bool}
        """
        data = demand.generateData()
        if self.isCommissioned() \
                and self.couldSense(data):
            return (any(m.isSensor()
                       and m.canSense(self.location, demand)
                       for m in self.modules)
                    and self.canStore(data))
        return False
        
    def senseAndStore(self, contract):
        """
        Senses and stores data for a contract.
        @param contract: the contract for which to sense data
        @type contract: L{Contract}
        @return: L{bool}
        """
        data = contract.demand.generateData()
        if self.canSense(contract.demand):
            if any(m.isSensor()
                    and m.canSense(self.location, contract.demand)
                    and (m.canStore(data)
                         or any(any(s is not m
                                    and s.isStorage()
                                    and s.canStore(d)
                                    and self.canTransfer(d, m, s)
                                    and self.transfer(d, m, s)
                                    for s in self.modules)
                                for d in m.data))
                    and m.senseAndStore(self.location, contract)
                    for m in self.modules):
                self.trigger('sense', self, contract)
                return True
        logging.warning('{0} could not sense and store {1}'
                        .format(self.name, contract.name))
        return False
    
    def getMaxSensed(self, phenomenon=None):
        """
        Gets the maximum amount of data sensed by this element.
        @param phenomenon: the data phenomenon
        @type phenomenon: L{str}
        @return: L{int}
        """
        return sum(m.maxSensed
                   for m in self.modules
                   if m.isSensor()
                   and (m.phenomenon == phenomenon
                        or phenomenon is None))
    
    def getSensed(self, phenomenon=None):
        """
        Gets the amount of data currently sensed by this element.
        @param phenomenon: the data phenomenon
        @type phenomenon: L{str}
        @return: L{int}
        """
        return sum(m.sensed
                   for m in self.modules
                   if m.isSensor()
                   and (m.phenomenon == phenomenon
                        or phenomenon is None))
    
    def getMaxStored(self, phenomenon=None):
        """
        Gets the maximum amount of data stored in this element.
        @param phenomenon: the data phenomenon
        @type phenomenon: L{str}
        @return: L{int}
        """
        return sum(m.capacity
                   for m in self.modules
                   if (m.isStorage()
                       and not m.isSensor())
                   or (m.isSensor()
                       and (m.phenomenon == phenomenon
                            or phenomenon is None)))
    
    def getStored(self, phenomenon=None):
        """
        Gets the amount of data currently stored in this element.
        @param phenomenon: the data phenomenon
        @type phenomenon: L{str}
        @return: L{int}
        """
        return sum(m.getContentsSize()
                   for m in self.modules
                   if (m.isStorage()
                       and not m.isSensor())
                   or (m.isSensor()
                       and (m.phenomenon == phenomenon
                            or phenomenon is None)))
    
    def getTransmitted(self, protocol):
        """
        Gets the maximum amount of data transmitted by this element.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @return: L{int}
        """
        return sum(m.transmitted
                   for m in self.modules
                   if m.isTransceiver()
                   and m.protocol == protocol)
        
    def getMaxTransmitted(self, protocol):
        """
        Gets the amount of data currently transmitted by this element.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @return: L{int}
        """
        return sum(m.maxTransmitted
                   for m in self.modules
                   if m.isTransceiver()
                   and m.protocol == protocol)
        
    def getReceived(self, protocol):
        """
        Gets the maximum amount of data received by this element.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @return: L{int}
        """
        return sum(m.received
                   for m in self.modules
                   if m.isTransceiver()
                   and m.protocol == protocol)
        
    def getMaxReceived(self, protocol):
        """
        Gets the amount of data currently received by this element.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @return: L{int}
        """
        return sum(m.maxReceived
                   for m in self.modules
                   if m.isTransceiver()
                   and m.protocol == protocol)
    
    def init(self, sim):
        """
        Initializes this element in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Element, self).init(sim)
        self.location = self._initLocation
        self.modules = self._initModules[:]
        for module in self.modules:
            module.init(sim)
    
    def tick(self, sim):
        """
        Ticks this element in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Element, self).tick(sim)
        if sim.entity('context') is not None:
            self._nextLocation = sim.entity('context').propagate(
                self.location, sim.timeStep)
        for module in self.modules:
            module.tick(sim)
    
    def tock(self):
        """
        Tocks this element in a simulation.
        """
        super(Element, self).tock()
        self.location = self._nextLocation
        for module in self.modules:
            module.tock()