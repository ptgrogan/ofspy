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
Module class.
"""

from .entity import Entity

class Module(Entity):
    def __init__(self, name=None, cost=0, size=1, capacity=0):
        """
        @param cost: the cost of this module
        @type cost: L{float}
        @param size: the size of this module
        @type size: L{float}
        @param capacity: the data capacity of this module
        @type capacity: L{int}
        """
        if name is not None:
            Entity.__init__(self, name=name)
        else:
            Entity.__init__(self)
        self.cost = cost
        self.size = size
        self.capacity = capacity
        self.data = []
    
    def getContentsSize(self):
        """
        Gets the total size of data in this module.
        @return: L{int}
        """
        return sum(d.size for d in self.data)
    
    def couldExchange(self, data, module):
        """
        Checks if this module can exchange data with another module (state-independent).
        @param data: the data to exchange
        @type data: L{Data}
        @param module: the module with which to exchange
        @type module: L{Subsystem}
        @return: L{bool}
        """
        return self.couldTransferOut(data) \
                and module.couldTransferIn(data) \
                and any(module.couldTransferOut(d)
                        and self.couldTransferIn(d)
                        for d in module.data)
    
    def canExchange(self, data, module):
        """
        Checks if this module can exchange data with another module.
        @param data: the data to exchange
        @type data: L{Data}
        @param module: the module with which to exchange
        @type module: L{Subsystem}
        @return: L{bool}
        """
        return self.canTransferOut(data) \
                and module.couldTransferIn(data) \
                and any(module.canTransferOut(d)
                        and self.couldTransferIn(d)
                        for d in module.data)
    
    def exchange(self, data, module):
        """
        Exchanges data with another module.
        @param data: the data to exchange
        @type data: L{Data}
        @param module: the module with which to exchange
        @type module: L{Subsystem}
        @return: L{bool}
        """
        if self.canExchange(data, module):
            otherData = next(d for d in module.data
                             if module.canTransferOut(d) \
                                    and self.couldTransferIn(d))
            if self.transferOut(data) \
                    and module.transferOut(otherData) \
                    and self.transferIn(otherData) \
                    and module.transferIn(data):
                return True
        return False
    
    def couldTransferIn(self, data):
        """
        Checks if this module could transfer in data (state-independent).
        @param data: the data to transfer in
        @type data: L{Data}
        @return: L{bool}
        """
        return self.capacity >= data.size
    
    def canTransferIn(self, data):
        """
        Checks if this module can transfer in data (state-dependent).
        @param data: the data to transfer in
        @type data: L{Data}
        @return: L{bool}
        """
        return self.couldTransferIn(data) \
                and self.capacity >= data.size \
                        + sum(d.size for d in self.data)
    
    def transferIn(self, data):
        """
        Transfers data in to this module.
        @param data: the data to transfer in
        @type data: L{Data}
        @return: L{bool}
        """
        if self.canTransferIn(data):
            self.data.append(data)
            return True
        return False
    
    def couldTransferOut(self, data):
        """
        Checks if this module could transfer out data (state-independent).
        @param data: the data to transfer out
        @type data: L{Data}
        @return: L{bool}
        """
        return True
    
    def canTransferOut(self, data):
        """
        Checks if this module can transfer out data (state-dependent).
        @param data: the data to transfer out
        @type data: L{Data}
        @return: L{bool}
        """
        return data in self.data
            
    def transferOut(self, data):
        """
        Transfers data out of this module.
        @param data: the data to transfer out
        @type data: L{Data}
        @return: L{bool}
        """
        if self.canTransferOut(data):
            self.data.remove(data)
            return True
        return False
    
    def isStorage(self):
        """
        Checks if this module can store data.
        @return: L{bool}
        """
        return False
    
    def isSensor(self):
        """
        Checks if this module can sense data.
        @return: L{bool}
        """
        return False
    
    def isTransceiver(self):
        """
        Checks if this module can transmit/receive data.
        @return: L{bool}
        """
        return False
    
    def isDefense(self):
        """
        Checks if this is a defense module.
        @return: L{bool}
        """
        return False
    
    def isISL(self):
        """
        Checks if this module is an inter-satellite link.
        @return: L{bool}
        """
        return False
    
    def isSGL(self):
        """
        Checks if this module is a space-to-ground link.
        @return: L{bool}
        """
        return False
    
    def tock(self):
        """
        Tocks this module in a simulation.
        """
        super(Module, self).tock()
        if not self.isStorage():
            del self.data[:]