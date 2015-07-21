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
Contract class.
"""

from .entity import Entity

class Contract(Entity):
    def __init__(self, demand):
        """
        @param demand: the demand for this contract
        @type demand: L{Demand}
        """
        Entity.__init__(self, name='C-{0}'.format(demand.name))
        self.demand = demand
        self.elapsedTime = 0
        self._initElapsedTime = 0
        self._nextElapsedTime = 0
        
    def getValue(self):
        """
        Gets the current value of this contract.
        @return: L{float}
        """
        return self.demand.getValueAt(self.elapsedTime)
    
    def isDefaulted(self, dataLocation):
        """
        Checks if this contract is defaulted.
        @param dataLocation: the location of contracted data
        @type dataLocation: L{Location}
        @return: L{bool}
        """
        return self.elapsedTime > self.demand.getDefaultTime() \
                or dataLocation is None
    
    def isCompleted(self, dataLocation):
        """
        Checks if this contract is completed.
        @param dataLocation: the location of contracted data
        @type dataLocation: L{Location}
        @return: L{bool}
        """
        return not self.isDefaulted(dataLocation) \
                and dataLocation.isSurface()
        
    def init(self, sim):
        """
        Initializes this contract in a simulation.
        @param sim: the simulator
        @type sim: L{Simulation}
        """
        super(Contract, self).init(sim)
        self.elapsedTime = self._initElapsedTime
        
    def tick(self, sim):
        """
        Ticks this contract in a simulation.
        @param sim: the simulator
        @type sim: L{Simulation}
        """
        super(Contract, self).tick(sim)
        self._nextElapsedTime += sim.timeStep
    
    def tock(self):
        """
        Tocks this contract in a simulation.
        """
        super(Contract, self).tock()
        self.elapsedTime = self._nextElapsedTime    