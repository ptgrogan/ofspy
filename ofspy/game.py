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

from .context import Context
from .surface import Surface
from .orbit import Orbit
from .demand import Demand
from .disturbance import Disturbance
from .valueSchedule import ValueSchedule
from .federation import Federation
from .federate import Federate
from .operations import Operations

from .groundStation import GroundStation
from .satellite import Satellite

from .storage import Storage
from .sensor import Sensor
from .defense import Defense
from .interSatelliteLink import InterSatelliteLink
from .spaceGroundLink import SpaceGroundLink

class Game(object):
    """
    A L{Game} contains the complete game specification.
    """
    
    def __init__(self, numPlayers=1, initialCash=1200,
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
            (0, 'disturb', {'type':'Debris', 'hitChance':1/6, 'maxHits':1})
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
        for mId, mType in enumerate(mTypes):
            module = self.generateModule(mType, pId, eId, mId)
            if module is not None:
                modules.append(module)
                
        if any(t['type'] == eType for t in self.stationTypes):
            spec = next(t for t in self.stationTypes
                        if t['type'] == eType)
            return GroundStation(cost=spec['cost'],
                                 capacity=spec['capacity'],
                                 modules=modules,
                                 name='{0}-{1}.{2}'.format(
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
                             name='{0}-{1}.{2}'.format(
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
                name='{0}-{1}.{2}.{3}'.format(
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
                name='{0}-{1}.{2}.{3}'.format(
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
                name='{0}-{1}.{2}.{3}'.format(
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
                name='{0}-{1}.{2}.{3}'.format(
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
                name='{0}-{1}.{2}.{3}'.format(
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
        locations = []
        for i in range(self.numSectors):
            locations.append(Surface(i, name='SUR{0}'.format(i+1)))
            for altitude in self.altitudes:
                locations.append(Orbit(i, altitude, name='{0}{1}'.format(altitude, i+1)))
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
        federates = []
        for i in range(self.numPlayers):
            operations = Operations()
            # TODO configure operations
            federates.append(Federate(name='P{0}'.format(i+1),
                                    initialCash=self.initialCash,
                                    operations=operations,
                                    elements=[]))
        fedOps = Operations()
        # TODO configure operations
        federation = Federation(name='FSS', federates=federates, operations=fedOps)
        
        return Context(locations=locations, events=events,
                       federations=[federation], seed=seed)