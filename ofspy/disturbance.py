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
Disturbance class.
"""

from .event import Event

class Disturbance(Event):
    """
    A L{Disturbance} defines a potentially-damaging event.
    """
    
    def __init__(self, sector, hitChance=0, maxHits=0, name=None):
        """
        @param sector: the associated spatial sector
        @type sector: L{int}
        @param hitChance: the chance this disturbance hits a subsystem
        @type hitChance: L{float}
        @param maxHits: the maximum number of hits per system
        @type maxHits: L{int}
        @param name: the name of this disturbance
        @type name: L{str}
        """
        if name is not None:
            Event.__init__(self, sector, name=name)
        else:
            Event.__init__(self, sector)
        self.hitChance = hitChance
        self.maxHits = maxHits
        
    def isDisturbance(self):
        """
        Checks if this is a disturbance event.
        
        @return: L{bool}
        """
        return True