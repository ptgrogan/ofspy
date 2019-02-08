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
Game class.
"""

import logging
import re

from .context import Context
from .context.location import Surface, Orbit
from .context.event import Demand, Disturbance, ValueSchedule
from .player import Federation, Federate
from .player.operations import Operations
from .player.operations.dynamic import DynamicOperations
from .player.operations.fixed_cost import FixedCostDynamicOperations

from .player.module import Defense, Storage, Sensor, SpaceGroundLink, InterSatelliteLink
from .player.element import GroundStation, Satellite

class Game(object):
    """
    A L{Game} contains the complete game specification.
    """

    def __init__(self, numPlayers, initialCash,
                 altitudes=['LEO','MEO','GEO'], numSectors=6):
        """
        @param numPlayers: the number of players (federates)
        @type numPlayers: L{int}
        @param initialCash: the initial cash of each player
        @type initialCash: L{float}
        @param altitudes: the list of orbit altitudes
        @type altitudes: L{list}
        @param numSectors: the number of sectors
        @type numSectors: L{int}
        """
        self.numSectors = numSectors
        self.altitudes = altitudes
        self.numPlayers = numPlayers
        self.initialCash = initialCash
        self.eventTypes = [
            (8, 'demand', {'type':'SAR1', 'phenomenon':'SAR', 'size':1,
                           'valueSchedule':ValueSchedule([(1,500),(4,400)], -50)}),
            (12, 'demand', {'type':'SAR2', 'phenomenon':'SAR', 'size':1,
                           'valueSchedule':ValueSchedule([(2,450),(5,350)], -100)}),
            (23, 'demand', {'type':'SAR3', 'phenomenon':'SAR', 'size':1,
                           'valueSchedule':ValueSchedule([(3,400),(6,300)], -150)}),
            (8, 'demand', {'type':'VIS1', 'phenomenon':'VIS', 'size':1,
                           'valueSchedule':ValueSchedule([(1,600),(4,500)], -50)}),
            (17, 'demand', {'type':'VIS2', 'phenomenon':'VIS', 'size':1,
                           'valueSchedule':ValueSchedule([(2,500),(5,400)], -100)}),
            (8, 'demand', {'type':'VIS3', 'phenomenon':'VIS', 'size':1,
                           'valueSchedule':ValueSchedule([(3,450),(6,350)], -150)}),
            (0, 'disturb', {'type':'Debris', 'hitChance':1./6, 'maxHits':1})
        ]
        self.satelliteTypes = [
            {'type':'SmallSat', 'cost':200, 'capacity':2},
            {'type':'MediumSat', 'cost':300, 'capacity':4},
            {'type':'LargeSat', 'cost':400, 'capacity':6}
        ]
        self.stationTypes = [
            {'type':'GroundSta', 'cost':500, 'capacity':4}
        ]
        self.sglTypes = [
            {'type':'pSGL', 'protocol':'pSGL', 'cost':50, 'size':1,
             'capacity':1, 'maxTransmitted':1, 'maxReceived':1},
            {'type':'oSGL', 'protocol':'oSGL', 'cost':100, 'size':1,
             'capacity':1, 'maxTransmitted':1, 'maxReceived':1}
        ]
        self.islTypes = [
            {'type':'pISL', 'protocol':'pISL', 'cost':50, 'size':1,
             'capacity':1, 'maxTransmitted':1, 'maxReceived':1},
            {'type':'oISL', 'protocol':'oISL', 'cost':100, 'size':1,
             'capacity':1, 'maxTransmitted':1, 'maxReceived':1}
        ]
        self.sensorTypes = [
            {'type':'SAR', 'phenomenon':'SAR', 'cost':200, 'size':1,
             'capacity':1, 'maxSensed':1},
            {'type':'VIS', 'phenomenon':'VIS', 'cost':250, 'size':1,
             'capacity':1, 'maxSensed':1}
        ]
        self.storageTypes = [
            {'type':'DAT', 'cost':50, 'size':1, 'capacity':1}
        ]
        self.defenseTypes = [
            {'type':'DEF', 'cost':100, 'size':1}
        ]

    def generateElement(self, eType, pId=None, eId=None, mTypes=[]):
        """
        Generates an element.
        @param eType: the element type
        @type eType: L{str}
        @param pId: the player id
        @type pId: L{int}
        @param eId: the element id
        @type eId: L{int}
        @param mTypes: the module types
        @type mTypes: L{list}
        @return: L{Element}
        """
        modules = []
        # generate and append modules
        for mId, mType in enumerate(mTypes):
            module = self.generateModule(mType, pId, eId, mId)
            if module is not None:
                modules.append(module)

        # parse and instantiate element based on type
        if any(t['type'] == eType for t in self.stationTypes):
            spec = next(t for t in self.stationTypes
                        if t['type'] == eType)
            return GroundStation(cost=spec['cost'],
                                 capacity=spec['capacity'],
                                 modules=modules,
                                 name='{0}_{1}.{2}'.format(
                                    spec['type'], pId+1, eId+1)
                                 if pId is not None
                                 and eId is not None
                                 else None)
        elif any(t['type'] == eType for t in self.satelliteTypes):
            spec = next(t for t in self.satelliteTypes
                        if t['type'] == eType)
            return Satellite(cost=spec['cost'],
                             capacity=spec['capacity'],
                             modules=modules,
                             name='{0}_{1}.{2}'.format(
                                spec['type'], pId+1, eId+1)
                             if pId is not None
                             and eId is not None
                             else None)
        return None

    def generateModule(self, mType, pId=None, eId=None, mId=None):
        """
        Generates a module.
        @param mType: the module type
        @type mType: L{str}
        @param pId: the player id
        @type pId: L{int}
        @param eId: the element id
        @type eId: L{int}
        @param mId: the module id
        @type mId: L{int}
        @return: L{Module}
        """
        # parse and instantiate module based on type
        if any(t['type'] == mType for t in self.sglTypes):
            spec = next(t for t in self.sglTypes
                        if t['type'] == mType)
            return SpaceGroundLink(
                protocol=spec['protocol'],
                cost=spec['cost'],
                size=spec['size'],
                capacity=spec['capacity'],
                maxTransmitted=spec['maxTransmitted'],
                maxReceived=spec['maxReceived'],
                name='{0}_{1}.{2}.{3}'.format(
                    spec['type'], pId+1, eId+1, mId+1)
                if pId is not None
                and eId is not None
                and mId is not None
                else None)
        elif any(t['type'] == mType for t in self.islTypes):
            spec = next(t for t in self.islTypes
                        if t['type'] == mType)
            return InterSatelliteLink(
                protocol=spec['protocol'],
                cost=spec['cost'],
                size=spec['size'],
                capacity=spec['capacity'],
                maxTransmitted=spec['maxTransmitted'],
                maxReceived=spec['maxReceived'],
                name='{0}_{1}.{2}.{3}'.format(
                    spec['type'], pId+1, eId+1, mId+1)
                if pId is not None
                and eId is not None
                and mId is not None
                else None)
        elif any(t['type'] == mType for t in self.sensorTypes):
            spec = next(t for t in self.sensorTypes
                        if t['type'] == mType)
            return Sensor(
                phenomenon=spec['phenomenon'],
                cost=spec['cost'],
                size=spec['size'],
                capacity=spec['capacity'],
                maxSensed=spec['maxSensed'],
                name='{0}_{1}.{2}.{3}'.format(
                    spec['type'], pId+1, eId+1, mId+1)
                if pId is not None
                and eId is not None
                and mId is not None
                else None)
        elif any(t['type'] == mType for t in self.storageTypes):
            spec = next(t for t in self.storageTypes
                        if t['type'] == mType)
            return Storage(
                cost=spec['cost'],
                size=spec['size'],
                capacity=spec['capacity'],
                name='{0}_{1}.{2}.{3}'.format(
                    spec['type'], pId+1, eId+1, mId+1)
                if pId is not None
                and eId is not None
                and mId is not None
                else None)
        elif any(t['type'] == mType for t in self.defenseTypes):
            spec = next(t for t in self.defenseTypes
                        if t['type'] == mType)
            return Defense(
                cost=spec['cost'],
                size=spec['size'],
                name='{0}_{1}.{2}.{3}'.format(
                    spec['type'], pId+1, eId+1, mId+1)
                if pId is not None
                and eId is not None
                and mId is not None
                else None)
        return None

    def generateContext(self, seed=0, ops='', fops=''):
        """
        Generates the context for this game.
        @param seed: the seed
        @type seed: L{int}
        @param ops: the federate operations specification
        @type ops: L{str}
        @param fops: the federation oeprations specification
        @type fops: L{str}
        @return: L{Context}
        """
        # generate locations based on number of sectors
        locations = []
        for i in range(self.numSectors):
            locations.append(Surface(i, name='SUR{0}'.format(i+1)))
            for altitude in self.altitudes:
                locations.append(Orbit(i, altitude, name='{0}{1}'.format(altitude, i+1)))

        # generate events based on known types
        events = []
        for eType in self.eventTypes:
            for i in range(eType[0]):
                if eType[1] == 'demand':
                    events.append(Demand(sector=None,
                                         phenomenon=eType[2]['phenomenon'],
                                         size=eType[2]['size'],
                                         valueSchedule=eType[2]['valueSchedule'],
                                         name='{0}.{1}'.format(eType[2]['type'], i+1)))
                elif eType[1] == 'disturb':
                    events.append(Disturbance(sector=None,
                                              hitChance=eType[2]['hitChance'],
                                              maxHits=eType[2]['maxHits'],
                                              name='{0}.{1}'.format(eType[2]['type'], i+1)))
                else:
                    logging.warning('Cannot interpret event type {0}'.format(eType))

        # generate federates based on number of players
        federates = []
        for i in range(self.numPlayers):
            # parse federate operations strategy
            operations = None
            if re.match('d', ops):
                # independent operations strategy
                planningHorizon = 6
                storagePenalty = -100
                islPenalty = -10
                if re.match('d(\d+,(?:a|\d+),\d+)', ops):
                    # case dH,s,i:  planning horizon H,
                    #               storage opportunity cost s,
                    #               isl opportunity cost i
                    args = re.search('(\d+,(?:a|\d+),\d+)',
                                     ops).group(0).split(',')
                    planningHorizon = int(args[0])
                    if args[1]== 'a':
                        storagePenalty = None
                    else:
                        storagePenalty = -1*int(args[1])
                    islPenalty = -1*int(args[2])
                elif re.match('(\d)', ops):
                    # case dH:  planning horizon H
                    planningHorizon = int(re.search(
                        '(\d+)', ops).group(0))
                operations = DynamicOperations(
                    planningHorizon=planningHorizon,
                    storagePenalty=storagePenalty,
                    islPenalty=islPenalty)
            else:
                # no operations strategy (default)
                operations = Operations()
            federates.append(Federate(name='P{0}'.format(i+1),
                                    initialCash=self.initialCash,
                                    operations=operations,
                                    elements=[]))
        # parse federation operations strategy
        foperations = None
        if re.match('d', fops):
            # parse centralized operations strategy
            planningHorizon = 6
            storagePenalty = -100
            islPenalty = -10
            if re.match('d\d+,(?:a|\d+),\d+', fops):
                # case dH,s,i:  planning horizon H,
                #               storage opportunity cost s,
                #               isl opportunity cost i
                args = re.search('(\d+,(?:a|\d+),\d+)',
                                 fops).group(0).split(',')
                planningHorizon = int(args[0])
                if args[1]== 'a':
                    storagePenalty = None
                else:
                    storagePenalty = -1*int(args[1])
                islPenalty = -1*int(args[2])
            elif re.match('(\d)', fops):
                # case dH:  planning horizon H
                planningHorizon = int(re.search(
                    '(\d+)', fops).group(0))
            foperations = DynamicOperations(
                planningHorizon=planningHorizon,
                storagePenalty=storagePenalty,
                islPenalty=islPenalty)
        elif re.match('x', fops):
            # parse federated operations strategy
            planningHorizon = 6
            storagePenalty = -100
            islPenalty = -10
            priceSGL = 50
            priceISL = 20
            if re.match('x\d+,\d+,\d+,(?:a|\d+),\d+',fops) is not None:
                # case xG,I,H,s,i:  SGL fixed cost G,
                #                   ISL fixed cost I,
                #                   planning horizon H,
                #                   storage opportunity cost s,
                #                   isl opportunity cost i
                args = re.search('(\d+,\d+,\d+,(?:a|\d+),\d+)',
                                 fops).group(0).split(',')
                priceSGL = int(args[0])
                priceISL = int(args[1])
                planningHorizon = int(args[2])
                if args[3]== 'a':
                    storagePenalty = None
                else:
                    storagePenalty = -1*int(args[3])
                islPenalty = -1*int(args[4])
            elif re.match('x\d+,(?:a|\d+),\d+', fops):
                # case xH,s,i:  planning horizon H,
                #               storage opportunity cost s,
                #               isl opportunity cost i
                args = re.search('(\d+,(?:a|\d+),\d+)',
                                 fops).group(0).split(',')
                planningHorizon = int(args[0])
                if args[1]== 'a':
                    storagePenalty = None
                else:
                    storagePenalty = -1*int(args[1])
                islPenalty = -1*int(args[2])
            elif re.match('x\d+,\d+,\d+', fops):
                # case xG,I,H:  SGL fixed cost G,
                #               ISL fixed cost I,
                #               planning horizon H
                # FIXME: this case is not currently possible
                args = re.search('(\d+,\d+,\d+)',
                                 fops).group(0).split(',')
                priceSGL = int(args[0])
                priceISL = int(args[1])
                planningHorizon = int(args[2])
            foperations = FixedCostDynamicOperations(
                planningHorizon=planningHorizon,
                storagePenalty=storagePenalty,
                islPenalty=islPenalty)
            for federate in federates:
                federate.priceSGL = priceSGL
                federate.priceISL = priceISL
        else:
            foperations = Operations()
        federation = Federation(name='FSS',
                                federates=federates,
                                operations=foperations)

        return Context(locations=locations, events=events,
                       federations=[federation], seed=seed)
