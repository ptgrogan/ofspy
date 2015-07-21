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
    def __init__(self, name=None, cost=0, capacity=0, modules=[]):
        """
        @param name: the name of this satellite
        @type name: L{str}
        @param location: the location of this satellite
        @type location: L{Location}
        @param cost: the cost of this satellite
        @type cost: L{float}
        @param capacity: the capacity for modules
        @type capacity: L{int}
        @param modules: the set of modules
        @type modules: L{set}
        """
        if name is not None:
            Element.__init__(self, name=name, cost=cost,
                             capacity=capacity, modules=modules)
        else:
            Element.__init__(self, cost=cost,
                             capacity=capacity, modules=modules)
    
    def canCommission(self, location, context):
        """
        Checks if this satellite can be commissioned at a location.
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return super(Satellite, self).canCommission(location, context) \
                and location.isOrbit()
        
    def getCommissionCost(self, location, context):
        """
        Gets the commission cost for this satellite.
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{float}
        """
        if self.canCommission(location, context):
            if location.altitude == "LEO":
                return 0
            elif location.altitude == "MEO":
                return 0.5*self.cost
            elif location.altitude == "GEO":
                return 1.0*self.cost
        return 0
    
    def getDecommissionValue(self):
        """
        Gets the decommission value of this satellite.
        @return: L{float}
        """
        if not self.isCommissioned():
            return 0.5*self.getDesignCost()
        elif self.location.altitude == "LEO":
            return 0.5*self.getDesignCost()
        elif self.location.altitude == "MEO":
            return 0.5*self.getDesignCost()
        elif self.location.altitude == "GEO":
            return 0.5*self.getDesignCost()
        return 0
    
    def isSpace(self):
        """
        Checks if this is a space element.
        @return: L{bool}
        """
        return True