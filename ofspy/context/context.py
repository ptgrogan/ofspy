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

from ofspy.sim.entity import Entity

class Context(Entity):
    """
    A L{Context} contains the complete simulation state.
    """
    
    def __init__(self, locations, events, federations, seed=0):
        """
        TODO
        """
        Entity.__init__(self, 'context')
        self.locations = locations
        self.events = events
        self.currentEvents = []
        self.futureEvents = []
        self.pastEvents = []
        self.federations = federations
        self.seed = seed
        
        self.sectors = frozenset(map(l.sector for l in self.locations))
        self.initTime = 0
        self.maxTime = 0
        self.time = 0
    
    def propagate(self, location, duration):
        if location.isOrbit():
            if location.altitude is "LEO":
                return self.propagateImpl(location, 1*duration)
            elif location.altitude is "MEO":
                return self.propagateImpl(location, 2*duration)
            elif location.altitude is "GEO":
                return self.propagateImpl(location, 0*duration)
        return location
    
    def propagateImpl(self, location, distance):
        path = [l for l in self.locations
                if l.altitude is location.altitude]
        return next((p for p in path
                    if p.sector is ((location.sector - 1 + distance)
                        % (len(path) + 1))), None)
    
    def init(self, sim):
        super(Context, self).init(sim)
        self.masterStream = random.Random(self.seed)
        self.shuffleStream = random.Random(self.masterStream.random())
        self.orderStream = random.Random(self.masterStream.random())
        self.rollStreams = map(random.Random(self.masterStream.random()),
                               [federate for federation.federates in self.federations for federate in federation.federates])
        
    def tick(self, sim):
        super(Context, self).tick(sim)
    
    def tock(self):
        super(Context, self).tock()