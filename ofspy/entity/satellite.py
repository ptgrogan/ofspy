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
Satellite class.
"""

from .element import Element

class Satellite(Element):
    def __init__(self, cost=0, capacity=0, modules=[]):
        """
        @param location: the location of this satellite
        @type location: L{Location}
        @param cost: the cost of this satellite
        @type cost: L{float}
        @param capacity: the capacity for modules
        @type capacity: L{int}
        @param modules: the set of modules
        @type modules: L{set}
        """
        Element.__init__(self, cost, capacity, modules)
    
    def canCommission(self, location):
        """
        Checks if this satellite can be commissioned at a location.
        @param location: the location at which to commission
        @type location: L{Location}
        @return: L{bool}
        """
        return super(Satellite, self).canCommission(location) \
                and location.isOrbit()
        
    def getCommissionCost(self, location):
        """
        Gets the commission cost for this satellite.
        @return: L{float}
        """
        if self.canCommission(location):
            if location.altitude is "LEO":
                return 0
            elif location.altitude is "MEO":
                return 0.5*self.cost
            elif location.altitude is "GEO":
                return 1.0*self.cost
        return 0
    
    def getDecommissionValue(self):
        """
        Gets the decommission value of this satellite.
        @return: L{float}
        """
        if not self.isCommissioned():
            return 0.5*self.getDesignCost()
        elif self.location.altitude is "LEO":
            return 0.5*self.getDesignCost()
        elif self.location.altitude is "MEO":
            return 0.5*self.getDesignCost()
        elif self.location.altitude is "GEO":
            return 0.5*self.getDesignCost()
        return 0
    
    def isSpace(self):
        """
        Checks if this is a space element.
        @return: L{bool}
        """
        return True