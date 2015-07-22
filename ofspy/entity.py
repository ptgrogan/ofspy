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
Entity class.
"""

import uuid

class Entity(object):
    def __init__(self, name=uuid.uuid4):
        """
        @param name: the name of this entity
        @type sim: L{str}
        """
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