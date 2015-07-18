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
Event class.
"""

class Event(object):
    """
    An L{Event} defines an uncertain occurrance.
    """
    
    def __init__(self, sector):
        """
        @param sector: the spatial sector where this event occurs
        @type sector: L{int}
        """
        self.sector = sector
        
    def isDemand(self):
        """
        Checks if this is a demand event.
        
        @return: L{bool}
        """
        return False
    
    def isDisturbance(self):
        """
        Checks if this is a disturbance event.
        
        @return: L{bool}
        """
        return False