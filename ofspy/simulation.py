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
Simulation package.
"""

import uuid

class Observable(object):
    """
    An L{Observable} object conforms to an observer pattern and fires events.
    """
    def __init__(self):
        self._handlers = {}

    def trigger(self, events, *args):
        for event in events.split(' '):
            if event in self._handlers:
                for handler in self._handlers[event]:
                    handler(*args)

    def on(self, events, handler):
        for event in events.split(' '):
            if event not in self._handlers:
                self._handlers[event] = []
            self._handlers[event].append(handler)

    def off(self, events, handler):
        for event in events.split(' '):
            if event in self.handler:
                self._handlers[event].remove(handler)

class Entity(Observable):
    """
    An L{Entity} object is the fundamental unit of simulation.
    """
    def __init__(self, name=None):
        """
        @param name: the name of this entity
        @type sim: L{str}
        """
        Observable.__init__(self)
        if name is None:
            self.name = uuid.uuid4
        else:
            self.name = name

    def init(self, sim):
        """
        Initializes this entity in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        pass

    def tick(self, sim):
        """
        Ticks this entity in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        pass

    def tock(self):
        """
        Tocks this entity in a simulation.
        """
        pass

    def __str__(self):
        """
        Gets the string representation of this entity.
        """
        return self.name

class Simulator(Observable):
    """
    A L{Simulator} executes a time-evoked simulation.
    """
    def __init__(self, entities=None, initTime=0, timeStep=1, maxTime=10):
        """
        @param entities: the set of entities
        @type entities: L{list}
        @param initTime: the initial simulation time
        @type initTime: L{float}
        @param timeStep: the simulation time step
        @type timeStep: L{float}
        @param maxTime: the maximum simulation time
        @type maxTime: L{float}
        """
        Observable.__init__(self)
        if entities is None:
            self.entities = []
        else:
            self.entities = entities
        self.timeStep = timeStep
        self.initTime = initTime
        self.maxTime = maxTime

    def entity(self, name):
        return next((e for e in self.entities if e.name == name), None)

    def init(self):
        self.time = self.initTime
        for entity in self.entities:
            entity.init(self)
        self.trigger('init', self.time)

    def advance(self):
        if not self.isComplete():
            for entity in self.entities:
                entity.tick(self)
            for entity in self.entities:
                entity.tock()
            self.time += self.timeStep
            self.trigger('advance', self.time)
            if self.isComplete():
                self.trigger('complete', self.time)

    def execute(self):
        self.init()
        while not self.isComplete():
            self.advance()

    def isComplete(self):
        return (self.time >= self.maxTime
                if self.maxTime is not None else False)
