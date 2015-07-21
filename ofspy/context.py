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
Context class.
"""

import random
import logging

from .entity import Entity

class Context(Entity):
    """
    A L{Context} contains the complete simulation state.
    """
    
    def __init__(self, locations=[], events=[], federations=[], seed=0):
        """
        @param locations: the locations in this context
        @type locations: L{list}
        @param events: the events in this context
        @type events: L{list}
        @param federations: the federations in this context
        @type federations: L{list}
        @param seed: the seed for stochastic events
        @type seed: L{int}
        """
        Entity.__init__(self, 'context')
        self.locations = locations
        self.events = events
        self.currentEvents = []
        self.futureEvents = []
        self.pastEvents = []
        self.federations = federations
        self.seed = seed
        
        self.sectors = frozenset(l.sector for l in self.locations)
        self.initTime = 0
        self.maxTime = 0
        self.time = 0
        self._nextTime = 0
    
    def propagate(self, location, duration):
        if location is not None and location.isOrbit():
            if location.altitude == "LEO":
                return self.propagateImpl(location, 2*duration)
            elif location.altitude == "MEO":
                return self.propagateImpl(location, 1*duration)
            elif location.altitude == "GEO":
                return self.propagateImpl(location, 0*duration)
        return location
    
    def propagateImpl(self, location, distance):
        path = [l for l in self.locations
                if l.isOrbit()
                and l.altitude == location.altitude]
        return next((p for p in path
                    if p.sector == (location.sector + distance) % len(path)), None)
    
    def init(self, sim):
        super(Context, self).init(sim)
        self.masterStream = random.Random(self.seed)
        self.shuffleStream = random.Random(self.masterStream.random())
        self.orderStream = random.Random(self.masterStream.random())
        self.rollStreams = {}
        for federate in [federate for federation in self.federations
                         for federate in federation.federates]:
            self.rollStreams[federate.name] = random.Random(self.masterStream.random())
        self.currentEvents = []
        self.pastEvents = []
        self.futureEvents = self.events[:]
        random.shuffle(self.futureEvents, random=self.shuffleStream.random)
        self.time = sim.initTime
        self.initTime = sim.initTime
        self.maxTime = sim.maxTime
        for federation in self.federations:
            federation.init(sim)
        
    def tick(self, sim):
        super(Context, self).tick(sim)
        for federation in self.federations:
            federation.tick(sim)
        self._nextTime = self.time + sim.timeStep
    
    def tock(self):
        super(Context, self).tock()
        for federation in self.federations:
            federation.tock()
            
        for federate in [federate for federation in self.federations
                         for federate in federation.federates]:
            # default any failed contracts
            for contract in federate.contracts[:]:
                if contract.isDefaulted(federate.getDataLocation(contract)):
                    logging.warning('Auto-defaulting {0} for {1}'
                                .format(contract.name, federate.name))
                    federate.default(contract, self)
            # liquidate bankrupt federates
            if federate.cash < 0:
                federate.liquidate(self)
        
        # debug log for spatial state
        for location in self.locations:
            if any(element for federation in self.federations
                   for federate in federation.federates
                   for element in federate.elements
                   if element.location is location):
             logging.debug('{0}'.format(location.name))
             for element in [element for federation in self.federations
                             for federate in federation.federates
                             for element in federate.elements
                             if element.location is location]:
                 logging.debug('-{0}'.format(element.name))
                 for module in element.modules:
                     logging.debug(' -{0}'.format(module.name))
                     for d in module.data:
                         logging.debug('  -{0} {1}'.format(data.phenomenon,
                                                           data.contract))
        
        # reveal and resolve new events in each sector
        while len(self.currentEvents) > 0:
            self.pastEvents.append(self.currentEvents.pop())
        for sector in self.sectors:
            event = self.futureEvents.pop()
            event.sector = sector
            self.currentEvents.append(event)
            if any(element for federation in self.federations
                   for federate in federation.federates
                   for element in federate.elements
                   if element.isSpace()
                   and element.location is not None
                   and element.location.sector == sector):
                logging.debug('Sector {0} event: {1}'
                              .format(sector+1, event.name))
                
            # shuffle past events if there are no more future events
            if len(self.futureEvents) < 1:
                logging.info('Shuffling events...')
                random.shuffle(self.pastEvents, self.shuffleStream.random)
                while len(self.pastEvents) > 0:
                    self.futureEvents.append(self.pastEvents.pop())
            # resolve disturbances
            if event.isDisturbance():
                for federate in [federate for federation in self.federations
                                 for federate in federation.federates]:
                    rollStream = self.rollStreams[federate.name]
                    for element in federation.elements:
                        if (element.isSpace()
                            and element.location is not None
                            and element.location.sector == event.sector):
                                if any(module.isDefense() for module in element.modules):
                                    logging.info('{0} is protected from {1}'
                                                .format(element.name, event.name))
                                else:
                                    numHits = 0
                                    modules = element.modules[:]
                                    random.shuffle(modules, random=rollStream.random)
                                    for module in modules:
                                        if (numHits < event.maxHits
                                            and rollStream.random() < event.hitChance):
                                            element.modules.remove(module)
                                            numHits += 1
                                            logging.info('{0} was hit and lost {1}'
                                                        .format(element.name, module.name))
        self.time = self._nextTime
        logging.info('Commence operations for time {0}'.format(self.time))
        federations = self.federations[:]
        random.shuffle(federations, random=self.shuffleStream.random)
        for federation in federations:
            federates = federation.federates[:]
            random.shuffle(federates, random=self.shuffleStream.random)
            for federate in federates:
                federate.operations.execute(federate, self)
            federation.operations.execute(federation, self)
        
        for federate in [federate for federation in self.federations
                         for federate in federation.federates]:
            logging.info('{0} has {1} cash at time {2}'
                        .format(federate.name, federate.cash, self.time))