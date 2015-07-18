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
Transceiver class.
"""

from .module import Module

class Transceiver(Module):
    def __init__(self, cost=0, size=1, capacity=1, protocol=None, maxTransmitted=1, maxReceived=1):
        """
        @param cost: the cost of this transceiver
        @type cost: L{float}
        @param size: the size of this transceiver
        @type size: L{float}
        @param capacity: the data capacity of this transceiver
        @type capacity: L{int}
        @param protocol: the protocol of this transceiver
        @type protocol: L{string}
        @param maxTransmitted: the max data transmitted by this transceiver each turn
        @type maxTransmitted: L{int}
        @param maxReceived: the max data received by this transceiver each turn
        @type maxReceived: L{int}
        """
        Module.__init__(self, cost, size, capacity)
        self.protocol = protocol
        self.maxTransmitted = maxTransmitted
        self.maxReceived = maxReceived
        self._initTransmitted = 0
        self.transmitted = self._initTransmitted
        self._initReceived = 0
        self.received = self._initReceived
    
    def couldTransmit(self, data, receiver, txLocation=None, rxLocation=None):
        """
        Checks if this transceiver could transmit data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return self.maxTransmitted >= data.size \
                and self.protocol is receiver.protocol
        # TODO check for proprietary protocol compatibility
    
    def canTransmit(self, data, receiver, txLocation=None, rxLocation=None):
        """
        Checks if this transceiver can transmit data (state-dependent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return self.couldTransmit(data, receiver, txLocation, rxLocation) \
                and self.maxTransmitted >= data.size + self.transmitted
                # and self.canTransferOut(data)
        
    def transmit(self, data, receiver, txLocation=None, rxLocation=None):
        """
        Transmits data from this tranceiver.
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        if self.canTransmit(data, receiver, txLocation, rxLocation) \
                and self.canTransferOut(data) \
                and self.transferOut(data):
            self.transmitted += data.size
            return True
        return False
    
    def couldReceive(self, data, transmitter, txLocation=None, rxLocation=None):
        """
        Checks if this transceiver could receive data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return self.maxReceived >= data.size \
                and self.protocol is transmitter.protocol
        # TODO check for proprietary protocol compatibility
        
    def canReceive(self, data, transmitter, txLocation=None, rxLocation=None):
        """
        Checks if this transceiver can receive data (state-dependent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return self.couldReceive(data, transmitter, txLocation, rxLocation) \
                and self.maxReceived >= data.size + self.received \
                and self.canTransferIn(data)
    
    def receive(self, data, transmitter, txLocation=None, rxLocation=None):
        """
        Receives data with this tranceiver.
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Transceiver}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        if self.canReceive(data, transmitter, txLocation, rxLocation) \
                and self.transferIn(data):
            self.received += data.size
            return True
        return False
    
    def isTransceiver(self):
        """
        Checks if this module can transmit and receive data.
        @return: L{bool}
        """
        return True
    
    def init(self, sim):
        """
        Initializes this transceiver in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Transceiver, self).init(sim)
        self.transmitted = self._initTransmitted
        self.received = self._initReceived
    
    def tock(self):
        """
        Tocks this transceiver in a simulation.
        """
        super(Transceiver, self).tock()
        self.transmitted = 0
        self.received = 0