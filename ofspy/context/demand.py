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
Demand class.
"""

from .event import Event
from .valueSchedule import ValueSchedule
from .data import Data

class Demand(Event):
    """
    A L{Demand} defines a demand for data collection and down-link.
    """
    
    def __init__(self, sector, phenomenon, size, 
                 valueSchedule=ValueSchedule()):
        """
        @param sector: the associated spatial sector
        @type sector: L{int}
        @param phenomenon: the phenomenon demanded
        @type phenomenon: L{string}
        @param size: the size of data demanded
        @type size: L{int}
        @param valueSchedule: the value schedule for completing this demand
        @type valueSchedule: L{ValueSchedule}
        """
        Event.__init__(self, sector)
        self.phenomenon = phenomenon
        self.size = size
        self.valueSchedule = valueSchedule
    
    def getValueAt(self, time):
        """
        Gets the value of this demand at an elapsed time.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        return self.valueSchedule.getValueAt(time)
    
    def getDefaultTime(self):
        """
        Gets the time when this demand is defaulted.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        return self.valueSchedule.getDefaultTime()
    
    def generateData(self, contract=None):
        """
        Generates data for this demand.
        @return: L{Data}
        """
        return Data(self.phenomenon, self.size, contract)
        
    def isDemand(self):
        """
        Checks if this is a demand event.
        
        @return: L{bool}
        """
        return True