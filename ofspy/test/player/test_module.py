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
Test cases for L{ofspy.player.module} package.
"""

import unittest

from ...context import Context
from ...player import Data, Contract
from ...context.event import Demand
from ...context.location import Surface, Orbit
from ...simulation import Simulator
from ...player.module import Module, Defense, Storage, Sensor, Link, SpaceGroundLink, InterSatelliteLink

"""
Test cases for L{ofspy.module.Module} class.
"""

class ModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.testData = [Data('SAR',1), Data('SAR',1), Data('VIS',1), Data('VIS',1),
                         Data('SAR',2), Data('SAR',2), Data('VIS',2), Data('VIS',2)]
        self.cap1 = Module(cost=0, size=1, capacity=1)
        self.cap2 = Module(cost=0, size=1, capacity=2)

    def tearDown(self):
        self.testData = None
        self.cap1 = None
        self.cap2 = None

    def test_getContentsSize(self):
        self.assertEqual(self.cap1.getContentsSize(), 0)
        self.assertEqual(self.cap2.getContentsSize(), 0)

        self.cap1.transferIn(self.testData[0])
        self.assertEqual(self.cap1.getContentsSize(), self.testData[0].size)
        self.cap1.transferOut(self.testData[0])

        self.cap2.transferIn(self.testData[0])
        self.assertEqual(self.cap2.getContentsSize(), self.testData[0].size)
        self.cap2.transferIn(self.testData[1])
        self.assertEqual(self.cap2.getContentsSize(),
                         self.testData[0].size + self.testData[1].size)
        self.cap2.transferOut(self.testData[0])
        self.cap2.transferOut(self.testData[1])

        self.cap2.transferIn(self.testData[4])
        self.assertEqual(self.cap2.getContentsSize(), self.testData[4].size)
        self.cap2.transferOut(self.testData[4])

    def test_couldTransferIn(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.couldTransferIn(data))
            self.assertTrue(self.cap2.couldTransferIn(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.couldTransferIn(data))
            self.assertTrue(self.cap2.couldTransferIn(data))

    def test_canTransferIn(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.canTransferIn(data))
            self.assertTrue(self.cap2.canTransferIn(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.canTransferIn(data))
            self.assertTrue(self.cap2.canTransferIn(data))

        self.assertTrue(self.cap1.transferIn(self.testData[0]))
        self.assertTrue(self.testData[0] in self.cap1.data)
        self.assertTrue(self.cap2.transferIn(self.testData[0]))
        self.assertTrue(self.testData[0] in self.cap2.data)

        for data in self.testData[1:4]:
            self.assertFalse(self.cap1.canTransferIn(data))
            self.assertTrue(self.cap2.canTransferIn(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.canTransferIn(data))
            self.assertFalse(self.cap2.canTransferIn(data))

        self.cap1.transferOut(self.testData[0])
        self.cap2.transferOut(self.testData[0])
        self.cap2.transferIn(self.testData[4])

        for data in self.testData[0:4]:
            self.assertFalse(self.cap2.canTransferIn(data))
        for data in self.testData[5:8]:
            self.assertFalse(self.cap2.canTransferIn(data))

        self.cap2.transferOut(self.testData[4])

    def test_transferIn(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.transferIn(data))
            self.cap1.transferOut(data)
            self.assertTrue(self.cap2.transferIn(data))
            self.cap2.transferOut(data)
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.transferIn(data))
            self.assertTrue(self.cap2.transferIn(data))
            self.cap2.transferOut(data)

        self.cap1.transferIn(self.testData[0])
        self.assertTrue(self.testData[0] in self.cap1.data)
        self.cap2.transferIn(self.testData[0])
        self.assertTrue(self.testData[0] in self.cap2.data)

        for data in self.testData[1:4]:
            self.assertFalse(self.cap1.transferIn(data))
            self.assertTrue(self.cap2.transferIn(data))
            self.cap2.transferOut(data)
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.transferIn(data))
            self.assertFalse(self.cap2.transferIn(data))

        self.cap1.transferOut(self.testData[0])
        self.cap2.transferOut(self.testData[0])
        self.cap2.transferIn(self.testData[4])
        self.assertTrue(self.testData[4] in self.cap2.data)

        for data in self.testData[0:4]:
            self.assertFalse(self.cap2.transferIn(data))
        for data in self.testData[5:8]:
            self.assertFalse(self.cap2.transferIn(data))

        self.cap2.transferOut(self.testData[4])

    def test_transferOut(self):
        self.cap1.transferIn(self.testData[0])
        self.cap1.transferOut(self.testData[0])
        self.assertTrue(self.testData[0] not in self.cap1.data)

        self.cap2.transferIn(self.testData[0])
        self.cap2.transferOut(self.testData[0])
        self.assertTrue(self.testData[0] not in self.cap2.data)

        self.cap2.transferIn(self.testData[4])
        self.cap2.transferOut(self.testData[4])
        self.assertTrue(self.testData[4] not in self.cap2.data)

    def test_canExchange(self):
        self.cap1.transferIn(self.testData[0])
        self.cap2.transferIn(self.testData[1])
        self.assertTrue(self.cap1.canExchange(self.testData[0], self.cap2))
        self.assertTrue(self.cap2.canExchange(self.testData[1], self.cap1))

        self.cap2.transferOut(self.testData[1])
        self.cap2.transferIn(self.testData[4])
        self.assertFalse(self.cap1.canExchange(self.testData[0], self.cap2))
        self.assertFalse(self.cap2.canExchange(self.testData[4], self.cap1))

    def test_exchange(self):
        self.cap1.transferIn(self.testData[0])
        self.cap2.transferIn(self.testData[1])
        self.assertTrue(self.cap1.exchange(self.testData[0], self.cap2))
        self.assertTrue(self.testData[1] in self.cap1.data)
        self.assertTrue(self.testData[0] in self.cap2.data)
        self.assertTrue(self.cap2.exchange(self.testData[0], self.cap1))
        self.assertTrue(self.testData[0] in self.cap1.data)
        self.assertTrue(self.testData[1] in self.cap2.data)

        self.cap2.transferOut(self.testData[1])
        self.cap2.transferIn(self.testData[4])
        self.assertFalse(self.cap2.exchange(self.testData[4], self.cap1))
        self.assertTrue(self.testData[0] in self.cap1.data)
        self.assertTrue(self.testData[4] in self.cap2.data)

"""
Test cases for L{ofspy.module.Defense} class.
"""

class DefenseTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Defense()

    def tearDown(self):
        self.default = None

    def test_isDefense(self):
        self.assertTrue(self.default.isDefense())

"""
Test cases for L{ofspy.module.Storage} class.
"""

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self.testData = [Data('SAR',1), Data('SAR',1), Data('VIS',1), Data('VIS',1),
                         Data('SAR',2), Data('SAR',2), Data('VIS',2), Data('VIS',2)]
        self.cap1 = Storage(capacity=1)
        self.cap2 = Storage(capacity=2)

    def tearDown(self):
        self.testData = None
        self.cap1 = None
        self.cap2 = None

    def test_couldStore(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.couldStore(data))
            self.assertTrue(self.cap2.couldStore(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.couldStore(data))
            self.assertTrue(self.cap2.couldStore(data))

    def test_canStore(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.canStore(data))
            self.assertTrue(self.cap2.canStore(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.canStore(data))
            self.assertTrue(self.cap2.canStore(data))

        self.cap1.transferIn(self.testData[0])
        self.cap2.transferIn(self.testData[0])

        for data in self.testData[1:4]:
            self.assertFalse(self.cap1.canStore(data))
            self.assertTrue(self.cap2.canStore(data))
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.canStore(data))
            self.assertFalse(self.cap2.canStore(data))

        self.cap1.transferOut(self.testData[0])
        self.cap2.transferOut(self.testData[0])
        self.cap2.transferIn(self.testData[4])

        for data in self.testData[0:4]:
            self.assertFalse(self.cap2.canStore(data))
        for data in self.testData[5:8]:
            self.assertFalse(self.cap2.canStore(data))

        self.cap2.transferOut(self.testData[4])

    def test_store(self):
        for data in self.testData[0:4]:
            self.assertTrue(self.cap1.store(data))
            self.assertEqual(self.cap1.data, [data])
            self.assertTrue(data in self.cap1.data)
            self.cap1.transferOut(data)
            self.assertTrue(self.cap2.store(data))
            self.assertTrue(data in self.cap2.data)
            self.cap2.transferOut(data)
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.store(data))
            self.assertTrue(self.cap2.store(data))
            self.cap2.transferOut(data)

        self.cap1.store(self.testData[0])
        self.assertTrue(self.testData[0] in self.cap1.data)
        self.cap2.store(self.testData[0])
        self.assertTrue(self.testData[0] in self.cap2.data)

        for data in self.testData[1:4]:
            self.assertFalse(self.cap1.store(data))
            self.assertTrue(self.cap2.store(data))
            self.cap2.transferOut(data)
        for data in self.testData[4:8]:
            self.assertFalse(self.cap1.store(data))
            self.assertFalse(self.cap2.store(data))

        self.cap1.transferOut(self.testData[0])
        self.cap2.transferOut(self.testData[0])
        self.cap2.transferIn(self.testData[4])
        self.assertTrue(self.testData[4] in self.cap2.data)

        for data in self.testData[0:4]:
            self.assertFalse(self.cap2.store(data))
        for data in self.testData[5:8]:
            self.assertFalse(self.cap2.store(data))

        self.cap2.transferOut(self.testData[4])

"""
Test cases for L{ofspy.module.Sensor} class.
"""

class SensorTestCase(unittest.TestCase):
    def setUp(self):
        self.sensors = [Sensor(capacity=1, phenomenon='SAR', maxSensed=1),
                        Sensor(capacity=1, phenomenon='VIS', maxSensed=1),
                        Sensor(capacity=2, phenomenon='SAR', maxSensed=2),
                        Sensor(capacity=2, phenomenon='VIS', maxSensed=2)]
        self.sim = Simulator(entities=self.sensors,
                             initTime=0, timeStep=1, maxTime=3)

    def tearDown(self):
        self.sensors = None
        self.sim = None

    def test_couldSense(self):
        self.assertTrue(self.sensors[0].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[0].couldSense(Data('SAR',2)))
        self.assertFalse(self.sensors[0].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[0].couldSense(Data('VIS',2)))

        self.assertFalse(self.sensors[1].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[1].couldSense(Data('SAR',2)))
        self.assertTrue(self.sensors[1].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[1].couldSense(Data('VIS',2)))

        self.assertTrue(self.sensors[2].couldSense(Data('SAR',1)))
        self.assertTrue(self.sensors[2].couldSense(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[2].couldSense(Data('VIS',2)))

        self.assertFalse(self.sensors[3].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[3].couldSense(Data('SAR',2)))
        self.assertTrue(self.sensors[3].couldSense(Data('VIS',1)))
        self.assertTrue(self.sensors[3].couldSense(Data('VIS',2)))

    def test_canSense(self):
        self.assertTrue(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[0].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Surface(0), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))

        self.assertTrue(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertTrue(self.sensors[1].canSense(
            Orbit(0,'MEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'GEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Surface(0), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))

        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Surface(0), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Surface(0), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))

        self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))

    def test_senseAndStore(self):
        self.assertTrue(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.assertFalse(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[0].data[:]:
            self.sensors[0].transferOut(d)
        self.assertFalse(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.sensors[0].tick(self.sim)
        self.sensors[0].tock()
        self.assertTrue(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))

        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[2].data[:]:
            self.sensors[2].transferOut(d)
        self.assertFalse(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.sensors[2].tick(self.sim)
        self.sensors[2].tock()
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[2].data[:]:
            self.sensors[2].transferOut(d)
        self.sensors[2].tick(self.sim)
        self.sensors[2].tock()
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',2))))

        self.sensors[1].transferIn(Data('VIS',1))
        self.assertFalse(self.sensors[1].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'VIS',1))))
        for d in self.sensors[1].data[:]:
            self.sensors[1].transferOut(d)
        self.assertTrue(self.sensors[1].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'VIS',1))))

    def test_couldTransferIn(self):
        self.assertTrue(self.sensors[0].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('VIS',1)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('VIS',2)))

        self.assertFalse(self.sensors[1].couldTransferIn(Data('SAR',1)))
        self.assertTrue(self.sensors[1].couldTransferIn(Data('VIS',1)))
        self.assertFalse(self.sensors[1].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[1].couldTransferIn(Data('VIS',2)))

        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',1)))
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',2)))

        self.sensors[2].transferIn(Data('SAR', 1))

        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',1)))
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',2)))

    def test_isSensor(self):
        for sensor in self.sensors:
            self.assertTrue(sensor.isSensor())

    def test_init(self):
        self.sensors[0].init(self.sim)
        self.assertEqual(self.sensors[0].sensed, self.sensors[0]._initSensed)

        self.sensors[0]._initSensed = 1
        self.sensors[0].init(self.sim)
        self.assertEqual(self.sensors[0].sensed, 1)

    def test_tock(self):
        self.sensors[0].init(self.sim)
        self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1)))
        self.sensors[0].tick(self.sim)
        self.sensors[0].tock()
        self.assertEqual(self.sensors[0].sensed, 0)

"""
Test cases for L{ofspy.module.Link} class.
"""

class LinkTestCase(unittest.TestCase):
    def setUp(self):
        self.Links = [Link(capacity=1, maxTransmitted=1, maxReceived=1),
                        Link(capacity=1, maxTransmitted=1, maxReceived=1),
                        Link(capacity=2, maxTransmitted=2, maxReceived=2),
                        Link(capacity=2, maxTransmitted=2, maxReceived=2)]
        self.testData = [Data('SAR',1), Data('SAR',1), Data('VIS',1), Data('VIS',1),
                         Data('SAR',2), Data('SAR',2), Data('VIS',2), Data('VIS',2)]
        self.sim = Simulator(entities=self.Links,
                             initTime=0, timeStep=1, maxTime=3)

    def tearDown(self):
        self.Links = None
        self.testData = None
        self.sim = None

    def test_couldTransmit(self):
        self.assertTrue(self.Links[0].couldTransmit(
            self.testData[0], self.Links[1]))
        self.assertTrue(self.Links[0].couldTransmit(
            self.testData[2], self.Links[1]))
        self.assertFalse(self.Links[0].couldTransmit(
            self.testData[4], self.Links[1]))
        self.assertFalse(self.Links[0].couldTransmit(
            self.testData[6], self.Links[1]))

        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[0], self.Links[3]))
        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[2], self.Links[3]))
        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[4], self.Links[3]))
        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[6], self.Links[3]))

        self.assertTrue(self.Links[0].couldTransmit(
            self.testData[0], self.Links[0]))
        self.assertFalse(self.Links[0].couldTransmit(
            self.testData[4], self.Links[0]))
        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[0], self.Links[2]))
        self.assertTrue(self.Links[2].couldTransmit(
            self.testData[4], self.Links[2]))

    def test_canTransmit(self):
        self.assertTrue(self.Links[0].canTransmit(
            self.testData[0], self.Links[1])) # no transfer out check
        self.assertTrue(self.Links[0].canTransmit(
            self.testData[2], self.Links[1])) # no transfer out check
        self.assertFalse(self.Links[0].canTransmit(
            self.testData[4], self.Links[1]))
        self.assertFalse(self.Links[0].canTransmit(
            self.testData[6], self.Links[1]))

        self.Links[0].transferIn(self.testData[0])
        self.assertTrue(self.Links[0].canTransmit(
            self.testData[0], self.Links[1]))
        self.Links[0].transmit(self.testData[0], self.Links[1])
        self.Links[0].transferIn(self.testData[2])
        self.assertFalse(self.Links[0].canTransmit(
            self.testData[2], self.Links[1]))

        self.assertTrue(self.Links[2].canTransmit(
            self.testData[0], self.Links[3])) # no transfer out check
        self.assertTrue(self.Links[2].canTransmit(
            self.testData[2], self.Links[3])) # no transfer out check
        self.assertTrue(self.Links[2].canTransmit(
            self.testData[4], self.Links[3])) # no transfer out check

        self.Links[2].transferIn(self.testData[0])
        self.assertTrue(self.Links[2].canTransmit(
            self.testData[0], self.Links[3]))
        self.Links[2].transmit(self.testData[0], self.Links[3])
        self.Links[2].transferIn(self.testData[1])
        self.assertTrue(self.Links[2].canTransmit(
            self.testData[1], self.Links[3]))
        self.Links[2].transmit(self.testData[1], self.Links[3])
        self.Links[2].transferIn(self.testData[2])
        self.assertFalse(self.Links[2].canTransmit(
            self.testData[2], self.Links[3]))
        self.Links[2].transferOut(self.testData[2])

        self.Links[2].tick(self.sim)
        self.Links[2].tock()

        self.Links[2].transferIn(self.testData[4])
        self.assertTrue(self.Links[2].canTransmit(
            self.testData[4], self.Links[3]))
        self.Links[2].transmit(self.testData[4], self.Links[3])
        self.Links[2].transferIn(self.testData[5])
        self.assertFalse(self.Links[2].canTransmit(
            self.testData[5], self.Links[3]))

    def test_transmit(self):
        self.Links[0].transferIn(self.testData[0])
        self.assertTrue(self.Links[0].transmit(
            self.testData[0], self.Links[1]))
        self.assertTrue(self.testData[0] not in self.Links[0].data)

        self.assertFalse(self.Links[0].transmit(
            self.testData[1], self.Links[1]))

        self.Links[2].transferIn(self.testData[2])
        self.assertTrue(self.Links[2].transmit(
            self.testData[2], self.Links[3]))
        self.assertTrue(self.testData[2] not in self.Links[2].data)
        self.Links[2].transferIn(self.testData[3])
        self.assertTrue(self.Links[2].transmit(
            self.testData[3], self.Links[3]))
        self.assertTrue(self.testData[3] not in self.Links[2].data)

        self.Links[2].tick(self.sim)
        self.Links[2].tock()

        self.Links[2].transferIn(self.testData[2])
        self.assertTrue(self.Links[2].transmit(
            self.testData[2], self.Links[3]))
        self.assertTrue(self.testData[2] not in self.Links[2].data)
        self.Links[2].transferIn(self.testData[6])
        self.assertFalse(self.Links[2].transmit(
            self.testData[6], self.Links[3]))
        self.assertTrue(self.testData[6] in self.Links[2].data)
        self.Links[2].transferOut(self.testData[6])

        self.Links[2].tick(self.sim)
        self.Links[2].tock()

        self.Links[2].transferIn(self.testData[4])
        self.assertTrue(self.Links[2].transmit(
            self.testData[4], self.Links[3]))
        self.assertTrue(self.testData[4] not in self.Links[2].data)
        self.Links[2].transferIn(self.testData[1])
        self.assertFalse(self.Links[0].transmit(
            self.testData[1], self.Links[1]))
        self.assertTrue(self.testData[1] in self.Links[2].data)

    def test_couldReceive(self):
        self.assertTrue(self.Links[0].couldReceive(
            self.testData[0], self.Links[1]))
        self.assertTrue(self.Links[0].couldReceive(
            self.testData[2], self.Links[1]))
        self.assertFalse(self.Links[0].couldReceive(
            self.testData[4], self.Links[1]))
        self.assertFalse(self.Links[0].couldReceive(
            self.testData[6], self.Links[1]))

        self.assertTrue(self.Links[2].couldReceive(
            self.testData[0], self.Links[3]))
        self.assertTrue(self.Links[2].couldReceive(
            self.testData[2], self.Links[3]))
        self.assertTrue(self.Links[2].couldReceive(
            self.testData[4], self.Links[3]))
        self.assertTrue(self.Links[2].couldReceive(
            self.testData[6], self.Links[3]))

        self.assertTrue(self.Links[0].couldReceive(
            self.testData[0], self.Links[0]))
        self.assertFalse(self.Links[0].couldReceive(
            self.testData[4], self.Links[0]))
        self.assertTrue(self.Links[2].couldReceive(
            self.testData[0], self.Links[2]))
        self.assertTrue(self.Links[2].couldReceive(
            self.testData[4], self.Links[2]))

    def test_canReceive(self):
        self.assertTrue(self.Links[0].canReceive(
            self.testData[0], self.Links[1]))
        self.assertTrue(self.Links[0].canReceive(
            self.testData[2], self.Links[1]))
        self.assertFalse(self.Links[0].canReceive(
            self.testData[4], self.Links[1]))
        self.assertFalse(self.Links[0].canReceive(
            self.testData[6], self.Links[1]))

        self.Links[0].receive(self.testData[0], self.Links[1])
        self.assertFalse(self.Links[0].canReceive(
            self.testData[1], self.Links[1]))
        self.Links[0].transferOut(self.testData[0])
        self.assertFalse(self.Links[0].canReceive(
            self.testData[1], self.Links[1]))

        self.assertTrue(self.Links[2].canReceive(
            self.testData[0], self.Links[3]))
        self.assertTrue(self.Links[2].canReceive(
            self.testData[2], self.Links[3]))
        self.assertTrue(self.Links[2].canReceive(
            self.testData[4], self.Links[3]))

        self.Links[2].receive(self.testData[0], self.Links[3])
        self.assertTrue(self.Links[2].canReceive(
            self.testData[1], self.Links[3]))
        self.Links[2].receive(self.testData[1], self.Links[3])
        self.assertFalse(self.Links[2].canReceive(
            self.testData[2], self.Links[3]))
        self.Links[2].transferOut(self.testData[0])
        self.Links[2].transferOut(self.testData[1])
        self.assertFalse(self.Links[2].canReceive(
            self.testData[2], self.Links[3]))

        self.Links[2].tick(self.sim)
        self.Links[2].tock()

        self.assertTrue(self.Links[2].canReceive(
            self.testData[4], self.Links[3]))
        self.Links[2].receive(self.testData[4], self.Links[3])
        self.Links[2].transferOut(self.testData[4])
        self.assertFalse(self.Links[2].canReceive(
            self.testData[0], self.Links[3]))

    def test_receive(self):
        self.assertTrue(self.Links[0].receive(
            self.testData[0], self.Links[1]))
        self.assertTrue(self.testData[0] in self.Links[0].data)
        self.assertFalse(self.Links[0].receive(
            self.testData[1], self.Links[1]))
        self.Links[0].transferOut(self.testData[0])

        self.assertTrue(self.Links[2].receive(
            self.testData[0], self.Links[3]))
        self.assertTrue(self.testData[0] in self.Links[2].data)
        self.assertTrue(self.Links[2].receive(
            self.testData[1], self.Links[3]))
        self.assertTrue(self.testData[1] in self.Links[2].data)
        self.assertFalse(self.Links[2].receive(
            self.testData[2], self.Links[3]))
        self.Links[2].transferOut(self.testData[0])
        self.Links[2].transferOut(self.testData[1])
        self.assertFalse(self.Links[2].receive(
            self.testData[2], self.Links[3]))

        self.Links[2].tick(self.sim)
        self.Links[2].tock()

        self.assertTrue(self.Links[2].receive(
            self.testData[4], self.Links[3]))
        self.assertTrue(self.testData[4] in self.Links[2].data)
        self.Links[2].transferOut(self.testData[4])
        self.assertFalse(self.Links[2].receive(
            self.testData[0], self.Links[3]))

    def test_isLink(self):
        for Link in self.Links:
            self.assertTrue(Link.isLink())

    def test_init(self):
        self.Links[0].init(self.sim)
        self.assertEqual(self.Links[0].transmitted,
                      self.Links[0]._initTransmitted)
        self.assertEqual(self.Links[0].received,
                      self.Links[0]._initReceived)

        self.Links[0]._initTransmitted = 1
        self.Links[0]._initReceived = 1
        self.Links[0].init(self.sim)
        self.assertEqual(self.Links[0].transmitted, 1)
        self.assertEqual(self.Links[0].received, 1)

    def test_tock(self):
        self.Links[0].init(self.sim)
        self.Links[1].init(self.sim)
        self.Links[0].transmit(Data('SAR',1), self.Links[1])
        self.Links[0].tick(self.sim)
        self.Links[1].tick(self.sim)
        self.Links[0].tock()
        self.Links[1].tock()
        self.assertEqual(self.Links[0].transmitted, 0)
        self.assertEqual(self.Links[1].received, 0)

"""
Test cases for L{ofspy.module.SpaceGroundLink} class.
"""

class SpaceGroundLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.sgls = [SpaceGroundLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        SpaceGroundLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        SpaceGroundLink(capacity=2, maxTransmitted=2, maxReceived=2),
                        SpaceGroundLink(capacity=2, maxTransmitted=2, maxReceived=2)]
        self.testData = [Data('SAR',1), Data('VIS',2)]
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO')]
        self.sim = Simulator(entities=self.sgls,
                             initTime=0, timeStep=1, maxTime=3)

    def tearDown(self):
        self.sgls = None
        self.testData = None
        self.testLocs = None
        self.sim = None

    def test_couldTransmit(self):
        self.assertFalse(self.sgls[0].couldTransmit(
            self.testData[0], self.sgls[1],
            self.testLocs[0], self.testLocs[0]))
        self.assertFalse(self.sgls[0].couldTransmit(
            self.testData[0], self.sgls[1],
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.sgls[0].couldTransmit(
            self.testData[1], self.sgls[2],
            self.testLocs[1], self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[0].couldTransmit(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[0].couldTransmit(
                self.testData[0], self.sgls[2],
                o, self.testLocs[0]))
        for o in self.testLocs[5:8]:
            self.assertFalse(self.sgls[0].couldTransmit(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.sgls[0].couldTransmit(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[2].couldTransmit(
                self.testData[1], self.sgls[3],
                o, self.testLocs[0]))

    def test_couldReceive(self):
        self.assertFalse(self.sgls[0].couldReceive(
            self.testData[0], self.sgls[1],
            self.testLocs[0], self.testLocs[0]))
        self.assertFalse(self.sgls[0].couldReceive(
            self.testData[0], self.sgls[1],
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.sgls[0].couldReceive(
            self.testData[1], self.sgls[2],
            self.testLocs[1], self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[0].couldReceive(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[0].couldReceive(
                self.testData[0], self.sgls[2],
                o, self.testLocs[0]))
        for o in self.testLocs[5:8]:
            self.assertFalse(self.sgls[0].couldReceive(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.sgls[0].couldReceive(
                self.testData[0], self.sgls[1],
                o, self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.sgls[2].couldReceive(
                self.testData[1], self.sgls[3],
                o, self.testLocs[0]))

    def test_isSGL(self):
        for sgl in self.sgls:
            self.assertTrue(sgl.isSGL())

"""
Test cases for L{ofspy.module.InterSatelliteLink} class.
"""

class InterSatelliteLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.isls = [InterSatelliteLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        InterSatelliteLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        InterSatelliteLink(capacity=2, maxTransmitted=2, maxReceived=2),
                        InterSatelliteLink(capacity=2, maxTransmitted=2, maxReceived=2)]
        self.testData = [Data('SAR',1), Data('VIS',1)]
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO'),
                         Surface(3), Orbit(3,'LEO'), Orbit(3,'MEO'), Orbit(3,'GEO'),
                         Surface(4), Orbit(4,'LEO'), Orbit(4,'MEO'), Orbit(4,'GEO'),
                         Surface(5), Orbit(5,'LEO'), Orbit(5,'MEO'), Orbit(5,'GEO')]
        self.sim = Simulator(entities=self.isls,
                             initTime=0, timeStep=1, maxTime=3)
        self.context = Context(locations=self.testLocs)

    def tearDown(self):
        self.isls = None
        self.testData = None
        self.testLocs = None
        self.sim = None

    def test_couldTransmit(self):
        self.assertFalse(self.isls[0].couldTransmit(
            self.testData[0], self.isls[1],
            self.testLocs[0], self.testLocs[0], self.context))
        self.assertFalse(self.isls[0].couldTransmit(
            self.testData[1], self.isls[2],
            self.testLocs[1], self.testLocs[0], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[2],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[5:8]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[9:12]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[5], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[2].couldTransmit(
                self.testData[1], self.isls[3],
                o, self.testLocs[1], self.context))

    def test_couldReceive(self):
        self.assertFalse(self.isls[0].couldReceive(
            self.testData[0], self.isls[1],
            self.testLocs[0], self.testLocs[0], self.context))
        self.assertFalse(self.isls[0].couldReceive(
            self.testData[1], self.isls[2],
            self.testLocs[1], self.testLocs[0], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[2],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[5:8]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1], self.context))
        for o in self.testLocs[9:12]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[5], self.context))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[2].couldReceive(
                self.testData[1], self.isls[3],
                o, self.testLocs[1], self.context))

    def test_isSGL(self):
        for isl in self.isls:
            self.assertTrue(isl.isISL())
