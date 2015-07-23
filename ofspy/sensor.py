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
Sensor class.
"""

from .storage import Storage

class Sensor(Storage):
    def __init__(self, name=None, cost=0, size=1, capacity=1,
                 phenomenon=None, maxSensed=1):
        """
        @param name: the name of this sensor
        @type name: L{str}
        @param cost: the cost of this sensor
        @type cost: L{float}
        @param size: the size of this sensor
        @type size: L{float}
        @param capacity: the data capacity of this sensor
        @type capacity: L{int}
        @param phenomenon: the phenomenon sensed by this sensor
        @type phenomenon: L{str}
        @param maxSensed: the max data sensed by this sensor each turn
        @type maxSensed: L{int}
        """
        Storage.__init__(self, name=name, cost=cost,
                         size=size, capacity=capacity)
        self.phenomenon = phenomenon
        self.maxSensed = maxSensed
        self._initSensed = 0
        self.sensed = self._initSensed
    
    def couldSense(self, data):
        """
        Checks if this sensor could sense data (state-independent).
        @param data: the data to sense
        @type data: L{Data}
        @return: L{bool}
        """
        return self.couldStore(data) \
                and self.maxSensed >= data.size
    
    def canSense(self, location, demand):
        """
        Checks if this sensor can sense data (state-dependent).
        @param location: the location
        @type location: L{Location}
        @param demand: the demand for which to sense
        @type demand: L{Demand}
        @return: L{bool}
        """
        data = demand.generateData()
        return self.couldSense(data) \
                and self.maxSensed >= self.sensed + data.size \
                and location.isOrbit() \
                and location.altitude != "GEO" \
                and demand.sector == location.sector
    
    def senseAndStore(self, location, contract):
        """
        Senses and stores data for a contract with this sensor.
        @param location: the location
        @type location: L{Location}
        @param contract: the contract for which to sense
        @type contract: L{Contract}
        @return: L{bool}
        """
        data = contract.demand.generateData(contract)
        if self.canSense(location, contract.demand) \
                and self.canStore(data):
            self.store(data)
            self.sensed += data.size
            return True
        return False
    
    def couldTransferIn(self, data):
        """
        Checks if this sensor could transfer in data (state-independent).
        @param data: the data to transfer in
        @type data: L{Data}
        @return: L{bool}
        """
        return super(Sensor, self).couldTransferIn(data) \
                and self.phenomenon == data.phenomenon
    
    def isSensor(self):
        """
        Checks if this subsystem can sense data.
        @return: L{bool}
        """
        return True
    
    def init(self, sim):
        """
        Initializes this sensor in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Sensor, self).init(sim)
        self.sensed = self._initSensed
    
    def tock(self):
        """
        Tocks this sensor in a simulation.
        """
        super(Sensor, self).tock()
        self.sensed = 0