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
InterSatelliteLink class.
"""

from .transceiver import Transceiver

class InterSatelliteLink(Transceiver):
    def __init__(self, cost=0, size=1, capacity=1, protocol=None, maxTransmitted=1, maxReceived=1):
        """
        @param cost: the cost of this inter-satellite link
        @type cost: L{float}
        @param size: the size of this inter-satellite link
        @type size: L{float}
        @param capacity: the data capacity of this inter-satellite link
        @type capacity: L{int}
        @param protocol: the protocol of this inter-satellite link
        @type protocol: L{string}
        @param maxTransmitted: the max data transmitted by this inter-satellite link each turn
        @type maxTransmitted: L{int}
        @param maxReceived: the max data received by this inter-satellite link each turn
        @type maxReceived: L{int}
        """
        Transceiver.__init__(self, cost, size, capacity, protocol, maxTransmitted, maxReceived)
    
    def couldTransmit(self, data, receiver, txLocation, rxLocation):
        """
        Checks if this inter-satellite link could transmit data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Transceiver}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return super(InterSatelliteLink, self).couldTransmit(data, receiver) \
                and txLocation.isOrbit() \
                and rxLocation.isOrbit() \
                and max(txLocation.sector, rxLocation.sector) \
                    - min(txLocation.sector, rxLocation.sector) <= 1
        
    def couldReceive(self, data, transmitter, txLocation, rxLocation):
        """
        Checks if this inter-satellite link could receive data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type transmitter: L{Transceiver}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @return: L{bool}
        """
        return super(InterSatelliteLink, self).couldReceive(data, transmitter) \
                and txLocation.isOrbit() \
                and rxLocation.isOrbit() \
                and max(txLocation.sector, rxLocation.sector) \
                    - min(txLocation.sector, rxLocation.sector) <= 1
        
    def isISL(self):
        """
        Checks if this is an inter-satellite link.
        @return: L{bool}
        """
        return True