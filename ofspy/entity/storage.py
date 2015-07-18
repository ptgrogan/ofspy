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
Storage class.
"""

from .module import Module

class Storage(Module):
    def __init__(self, cost=0, size=1, capacity=1):
        """
        @param cost: the cost of this storage module
        @type cost: L{float}
        @param size: the size of this storage module
        @type size: L{float}
        @param capacity: the data capacity of this storage module
        @type capacity: L{int}
        """
        Module.__init__(self, cost, size, capacity)
    
    def couldStore(self, data):
        """
        Checks if this module could store data (state-independent).
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        return self.couldTransferIn(data)
    
    def canStore(self, data):
        """
        Checks if this module can store data (state-dependent).
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        return self.canTransferIn(data)
    
    def store(self, data):
        """
        Stores data in this module.
        @param data: the data to store
        @type data: L{Data}
        @return: L{bool}
        """
        if self.canStore(data):
            self.transferIn(data)
            return True
        return False
    
    def isStorage(self):
        """
        Checks if this module can store data.
        @return: L{bool}
        """
        return True