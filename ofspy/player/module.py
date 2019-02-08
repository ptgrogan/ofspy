"""
Copyright 2015 Paul T. Grogan, Massachusetts Institute of Technology
Copyright 2017 Paul T. Grogan, Stevens Institute of Technology

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
The L{ofspy.player.module} package contains classes related to
player-controlled modules.
"""

from ..simulation import Entity

class Module(Entity):
    """
    A L{Module} represents a functional subsystem within an element.
    """
    def __init__(self, name=None, cost=0, size=1, capacity=0):
        """
        @param cost: the cost of this module
        @type cost: L{float}
        @param size: the size of this module
        @type size: L{float}
        @param capacity: the data capacity of this module
        @type capacity: L{int}
        """
        Entity.__init__(self, name=name)
        self.cost = cost
        self.size = size
        self.capacity = capacity
        self._initData = []
        self.data = self._initData[:]

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
                             if module.canTransferOut(d)
                             and self.couldTransferIn(d))
            if self.transferOut(data) \
                    and module.transferOut(otherData) \
                    and self.transferIn(otherData) \
                    and module.transferIn(data):
                self.trigger('exchange', self, data, module)
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
            self.trigger('transferIn', self, data)
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
            self.trigger('transferOut', self, data)
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

    def isLink(self):
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

    def init(self, sim):
        """
        Initializes this module in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Module, self).init(sim)
        self.data = self._initData[:]

    def tock(self):
        """
        Tocks this module in a simulation.
        """
        super(Module, self).tock()
        if not self.isStorage():
            del self.data[:]

class Defense(Module):
    """
    A L{Defense} module provides resilience to disturbances.
    """
    def __init__(self, name=None, cost=0, size=1):
        """
        @param name: the name of this defense module
        @type name: L{str}
        @param cost: the cost of this defense module
        @type cost: L{float}
        @param size: the size of this defense module
        @type size: L{float}
        @param capacity: the data capacity of this defense module
        @type capacity: L{int}
        """
        Module.__init__(self, name=name, cost=cost, size=size, capacity=0)

    def isDefense(self):
        """
        Checks if this is a defense module.
        @return: L{bool}
        """
        return True

class Storage(Module):
    """
    A L{Storage} module stores data.
    """
    def __init__(self, name=None, cost=0, size=1, capacity=1):
        """
        @param name: the name of this storage module
        @type name: L{str}
        @param cost: the cost of this storage module
        @type cost: L{float}
        @param size: the size of this storage module
        @type size: L{float}
        @param capacity: the data capacity of this storage module
        @type capacity: L{int}
        """
        Module.__init__(self, name=name, cost=cost,
                        size=size, capacity=capacity)

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
            self.trigger('store', self, data)
            return True
        return False

    def isStorage(self):
        """
        Checks if this module can store data.
        @return: L{bool}
        """
        return True

class Sensor(Storage):
    """
    An L{Sensor} senses a phenomenon and stores resulting data.
    """
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
            self.sensed += data.size
            self.trigger('sense', self, contract)
            self.store(data)
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

class Link(Module):
    """
    An L{Link} transports data between two elements.
    """
    def __init__(self, name=None, cost=0, size=1, capacity=1,
                 protocol=None, maxTransmitted=1, maxReceived=1):
        """
        @param name: the name of this Link
        @type name: L{str}
        @param cost: the cost of this Link
        @type cost: L{float}
        @param size: the size of this Link
        @type size: L{float}
        @param capacity: the data capacity of this Link
        @type capacity: L{int}
        @param protocol: the protocol of this Link
        @type protocol: L{str}
        @param maxTransmitted: the max data transmitted by this Link each turn
        @type maxTransmitted: L{int}
        @param maxReceived: the max data received by this Link each turn
        @type maxReceived: L{int}
        """
        Module.__init__(self, name=name, cost=cost,
                        size=size, capacity=capacity)
        self.protocol = protocol
        self.maxTransmitted = maxTransmitted
        self.maxReceived = maxReceived
        self._initTransmitted = 0
        self.transmitted = self._initTransmitted
        self._initReceived = 0
        self.received = self._initReceived

    def couldTransmit(self, data, receiver, txLocation=None, rxLocation=None, context=None):
        """
        Checks if this Link could transmit data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return self.maxTransmitted >= data.size \
                and self.protocol == receiver.protocol

    def canTransmit(self, data, receiver, txLocation=None, rxLocation=None, context=None):
        """
        Checks if this Link can transmit data (state-dependent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return self.couldTransmit(data, receiver, txLocation, rxLocation, context) \
                and self.maxTransmitted >= data.size + self.transmitted
                # and self.canTransferOut(data)

    def transmit(self, data, receiver, txLocation=None, rxLocation=None, context=None):
        """
        Transmits data from this tranceiver.
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if self.canTransmit(data, receiver, txLocation, rxLocation, context) \
                and self.canTransferOut(data) \
                and self.transferOut(data):
            self.transmitted += data.size
            self.trigger('transmit', self, data, receiver)
            return True
        return False

    def couldReceive(self, data, transmitter, txLocation=None, rxLocation=None, context=None):
        """
        Checks if this Link could receive data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return self.maxReceived >= data.size \
                and self.protocol == transmitter.protocol

    def canReceive(self, data, transmitter, txLocation=None, rxLocation=None, context=None):
        """
        Checks if this Link can receive data (state-dependent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return self.couldReceive(data, transmitter, txLocation, rxLocation, context) \
                and self.maxReceived >= data.size + self.received \
                and self.canTransferIn(data)

    def receive(self, data, transmitter, txLocation=None, rxLocation=None, context=None):
        """
        Receives data with this tranceiver.
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type receiver: L{Link}
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if self.canReceive(data, transmitter, txLocation, rxLocation, context) \
                and self.transferIn(data):
            self.received += data.size
            self.trigger('receive', self, data, transmitter)
            return True
        return False

    def isLink(self):
        """
        Checks if this module can transmit and receive data.
        @return: L{bool}
        """
        return True

    def init(self, sim):
        """
        Initializes this Link in a simulation.
        @param sim: the simulator
        @type sim: L{Simulator}
        """
        super(Link, self).init(sim)
        self.transmitted = self._initTransmitted
        self.received = self._initReceived

    def tock(self):
        """
        Tocks this Link in a simulation.
        """
        super(Link, self).tock()
        self.transmitted = 0
        self.received = 0

class SpaceGroundLink(Link):
    """
    An L{SpaceGroundLink} transports data from a satellite to a ground station.
    """
    def __init__(self, name=None, cost=0, size=1, capacity=1,
                 protocol=None, maxTransmitted=1, maxReceived=1):
        """
        @param name: the name of this space-to-ground link
        @type name: L{str}
        @param cost: the cost of this space-to-ground link
        @type cost: L{float}
        @param size: the size of this storage module
        @type size: L{float}
        @param capacity: the data capacity of this space-to-ground link
        @type capacity: L{int}
        @param protocol: the protocol of this space-to-ground link
        @type protocol: L{str}
        @param maxTransmitted: the max data transmitted by this space-to-ground link each turn
        @type maxTransmitted: L{int}
        @param maxReceived: the max data received by this space-to-ground link each turn
        @type maxReceived: L{int}
        """
        Link.__init__(self, name=name, cost=cost,
                             size=size, capacity=capacity,
                             protocol=protocol,
                             maxTransmitted=maxTransmitted,
                             maxReceived=maxReceived)

    def couldTransmit(self, data, receiver, txLocation, rxLocation, context=None):
        """
        Checks if this space-to-ground link could transmit data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Link}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return super(SpaceGroundLink, self).couldTransmit(data, receiver) \
                and txLocation.isOrbit() \
                and rxLocation.isSurface() \
                and txLocation.sector == rxLocation.sector

    def couldReceive(self, data, transmitter, txLocation, rxLocation, context=None):
        """
        Checks if this space-to-ground link could receive data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type transmitter: L{Link}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return super(SpaceGroundLink, self).couldReceive(data, transmitter) \
                and txLocation.isOrbit() \
                and rxLocation.isSurface() \
                and txLocation.sector == rxLocation.sector

    def isSGL(self):
        """
        Checks if this is a space-to-ground link.
        @return: L{bool}
        """
        return True

class InterSatelliteLink(Link):
    """
    An L{InterSatelliteLink} transports data between two satellites.
    """
    def __init__(self, name=None, cost=0, size=1, capacity=1,
                 protocol=None, maxTransmitted=1, maxReceived=1):
        """
        @param name: the name of this Link
        @type name: L{str}
        @param cost: the cost of this inter-satellite link
        @type cost: L{float}
        @param size: the size of this inter-satellite link
        @type size: L{float}
        @param capacity: the data capacity of this inter-satellite link
        @type capacity: L{int}
        @param protocol: the protocol of this inter-satellite link
        @type protocol: L{str}
        @param maxTransmitted: the max data transmitted by this inter-satellite link each turn
        @type maxTransmitted: L{int}
        @param maxReceived: the max data received by this inter-satellite link each turn
        @type maxReceived: L{int}
        """
        Link.__init__(self, name=name, cost=cost,
                             size=size, capacity=capacity,
                             protocol=protocol,
                             maxTransmitted=maxTransmitted,
                             maxReceived=maxReceived)

    def couldTransmit(self, data, receiver, txLocation, rxLocation, context):
        """
        Checks if this inter-satellite link could transmit data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param receiver: the receiver receiving the data
        @type receiver: L{Link}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return super(InterSatelliteLink, self).couldTransmit(data, receiver) \
                and txLocation.isOrbit() \
                and rxLocation.isOrbit() \
                and (abs(txLocation.sector - rxLocation.sector) <= 1
                     or abs(txLocation.sector - rxLocation.sector)
                     >= context.getNumSectors() - 1)

    def couldReceive(self, data, transmitter, txLocation, rxLocation, context):
        """
        Checks if this inter-satellite link could receive data (state-independent).
        @param data: the data to transmit
        @type data: L{Data}
        @param transmitter: the transmitter transmitting the data
        @type transmitter: L{Link}
        @param txLocation: the transmitter location
        @type txLocation: L{Location}
        @param rxLocation: the receiver location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return super(InterSatelliteLink, self).couldReceive(data, transmitter) \
                and txLocation.isOrbit() \
                and rxLocation.isOrbit() \
                and (abs(txLocation.sector - rxLocation.sector) <= 1
                     or abs(txLocation.sector - rxLocation.sector)
                     >= context.getNumSectors() - 1)

    def isISL(self):
        """
        Checks if this is an inter-satellite link.
        @return: L{bool}
        """
        return True
