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
Test cases for L{ofspy.entity.element}.
"""

import unittest

from ofspy.context.demand import Demand
from ofspy.context.data import Data
from ofspy.context.orbit import Orbit
from ofspy.context.surface import Surface
from ofspy.sim.simulator import Simulator

from ..element import Element
from ..contract import Contract
from ..storage import Storage
from ..sensor import Sensor
from ..defense import Defense
from ..interSatelliteLink import InterSatelliteLink
from ..spaceGroundLink import SpaceGroundLink

class ElementTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Element()
        self.test0 = Element(cost=500, capacity=3,
                             modules=[SpaceGroundLink(cost=50,protocol='pSGL')])
        self.test1 = Element(cost=200, capacity=2,
                             modules=[Sensor(cost=250,phenomenon='SAR'),
                                      SpaceGroundLink(cost=50,protocol='pSGL')])
        self.test2 = Element(cost=200, capacity=3,
                             modules=[Sensor(cost=250,phenomenon='SAR'),
                                      InterSatelliteLink(cost=50,protocol='pISL'),
                                      InterSatelliteLink(cost=50,protocol='pISL')])
        self.test3 = Element(cost=200, capacity=4,
                             modules=[Sensor(cost=250,phenomenon='VIS'),
                                      InterSatelliteLink(cost=50,protocol='pISL'),
                                      InterSatelliteLink(cost=50,protocol='pISL'),
                                      SpaceGroundLink(cost=50,protocol='pSGL')])
        self.test4 = Element(cost=200, capacity=4,
                             modules=[Sensor(cost=250,phenomenon='VIS'),
                                      Sensor(cost=250,phenomenon='SAR'),
                                      Storage(cost=50),
                                      SpaceGroundLink(cost=50,protocol='pSGL')])
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO')]
        self.testData = [Data('SAR',1), Data('SAR',1), Data('VIS',1), Data('VIS',1),
                         Data('SAR',2), Data('SAR',2), Data('VIS',2), Data('VIS',2)]
        self.testContracts = [Contract(Demand(0,'SAR',1)),
                              Contract(Demand(0,'VIS',1)),
                              Contract(Demand(1,'SAR',1)),
                              Contract(Demand(1,'VIS',1)),
                              Contract(Demand(0,'SAR',2)),
                              Contract(Demand(0,'VIS',2))]
        self.sim = Simulator(entities=[self.default, self.test0,
                                       self.test1, self.test2,
                                       self.test3, self.test4],
                             initTime=0, timeStep=1, maxTime=3)
        
    def tearDown(self):
        self.default = None
        self.test0 = None
        self.test1 = None
        self.test2 = None
        self.test3 = None
        self.testLocs = None
        self.testData = None
        self.sim = None
        
    def test_getContentsSize(self):
        self.assertEqual(self.default.getContentsSize(), 0)
        self.assertEqual(self.test1.getContentsSize(), 2)
        self.assertEqual(self.test2.getContentsSize(), 3)
        self.assertEqual(self.test3.getContentsSize(), 4)
    
    def test_isCommissioned(self):
        self.assertFalse(self.default.isCommissioned())
        self.default.commission(self.testLocs[1])
        self.assertTrue(self.default.isCommissioned())
    
    def test_canCommission(self):
        for l in self.testLocs:
            self.assertTrue(self.default.canCommission(l))
    
    def test_commission(self):
        self.assertTrue(self.default.commission(self.testLocs[1]))
        self.assertIs(self.default.location, self.testLocs[1])
    
    def test_getDesignCost(self):
        self.assertEqual(self.default.getDesignCost(), 0)
        self.assertEqual(self.test1.getDesignCost(), 200+250+50)
    
    def test_getCommissionCost(self):
        self.assertEqual(self.default.getCommissionCost(self.testLocs[0]), 0)
        self.assertEqual(self.default.getCommissionCost(self.testLocs[1]), 0)
        self.assertEqual(self.default.getCommissionCost(self.testLocs[2]), 0)
        self.assertEqual(self.default.getCommissionCost(self.testLocs[3]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[0]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[1]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[2]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[3]), 0)
    
    def test_getDecommissionValue(self):
        self.assertEqual(self.default.getDecommissionValue(), 0)
        self.assertEqual(self.test1.getDecommissionValue(), 0)
    
    def test_isGround(self):
        self.assertFalse(self.default.getDecommissionValue())
        self.assertFalse(self.test1.getDecommissionValue())
    
    def test_isSpace(self):
        self.assertFalse(self.default.getDecommissionValue())
        self.assertFalse(self.test1.getDecommissionValue())
    
    def test_couldTransmit(self):
        self.assertTrue(self.test1.couldTransmit(
            'pSGL', self.testData[0], self.test0,
            self.testLocs[1], self.testLocs[0]))
        self.assertFalse(self.test1.couldTransmit(
            None, self.testData[0], self.test0,
            self.testLocs[1], self.testLocs[0]))
        self.assertFalse(self.test1.couldTransmit(
            'pSGL', self.testData[4], self.test0,
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.test1.couldTransmit(
            'pSGL', self.testData[4], self.test2,
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.test2.couldTransmit(
            'pSGL', self.testData[4], self.test1,
            self.testLocs[1], self.testLocs[1]))
        
        self.assertTrue(self.test2.couldTransmit(
            'pISL', self.testData[0], self.test3,
            self.testLocs[1], self.testLocs[1]))
        self.assertTrue(self.test2.couldTransmit(
            'pISL', self.testData[0], self.test3,
            self.testLocs[1], self.testLocs[5]))
        self.assertFalse(self.test2.couldTransmit(
            'pISL', self.testData[4], self.test3,
            self.testLocs[1], self.testLocs[5]))
        
    def test_canTransmit(self):
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.assertFalse(self.test1.canTransmit(
            'pSGL', self.testData[0], self.test0))
        self.test1.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test1.canTransmit(
            'pSGL', self.testData[0], self.test0))
        
        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.assertFalse(self.test2.canTransmit(
            'pISL', self.testData[0], self.test3))
        self.test2.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test2.canTransmit(
            'pISL', self.testData[0], self.test3))
        
    def test_transmit(self):
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.test1.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test1.transmit(
            'pSGL', self.testData[0], self.test0))
        self.assertTrue(not any(self.testData[0] in m.data
                            for m in self.test1.modules))
        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.test2.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test2.transmit(
            'pISL', self.testData[0], self.test3))
        self.assertTrue(not any(self.testData[0] in m.data
                            for m in self.test2.modules))
    
    def test_couldReceive(self):
        self.assertTrue(self.test0.couldReceive(
            'pSGL', self.testData[0], self.test1,
            self.testLocs[1], self.testLocs[0]))
        self.assertFalse(self.test0.couldReceive(
            None, self.testData[0], self.test1,
            self.testLocs[1], self.testLocs[0]))
        self.assertFalse(self.test0.couldReceive(
            'pSGL', self.testData[4], self.test1,
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.test2.couldReceive(
            'pSGL', self.testData[4], self.test1,
            self.testLocs[1], self.testLocs[1]))
        self.assertFalse(self.test1.couldReceive(
            'pSGL', self.testData[4], self.test2,
            self.testLocs[1], self.testLocs[1]))
        
        self.assertTrue(self.test3.couldReceive(
            'pISL', self.testData[0], self.test2,
            self.testLocs[1], self.testLocs[1]))
        self.assertTrue(self.test3.couldReceive(
            'pISL', self.testData[0], self.test2,
            self.testLocs[1], self.testLocs[5]))
        self.assertFalse(self.test3.couldReceive(
            'pISL', self.testData[4], self.test2,
            self.testLocs[1], self.testLocs[5]))
    
    def test_canReceive(self):
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test0.canReceive(
            'pSGL', self.testData[0], self.test1))
        
        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.assertTrue(self.test3.canReceive(
            'pISL', self.testData[0], self.test2))
    
    def test_receive(self):
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test0.receive(
            'pSGL', self.testData[0], self.test1))
        self.assertTrue(any(self.testData[0] in m.data
                            for m in self.test0.modules))
        
        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.assertTrue(self.test3.receive(
            'pISL', self.testData[0], self.test2))
        self.assertTrue(any(self.testData[0] in m.data
                            for m in self.test3.modules))
    
    def test_couldTransfer(self):
        self.test1.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test1.couldTransfer(self.testData[0],
                                                 self.test1.modules[0],
                                                 self.test1.modules[1]))
    
    def test_canTransfer(self):
        self.test1.commission(self.testLocs[1])
        self.test1.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test1.canTransfer(self.testData[0],
                                               self.test1.modules[0],
                                               self.test1.modules[1]))
    
    def test_transfer(self):
        self.test1.commission(self.testLocs[1])
        self.test1.modules[0].transferIn(self.testData[0])
        self.assertTrue(self.test1.transfer(self.testData[0],
                                            self.test1.modules[0],
                                            self.test1.modules[1]))
        self.assertTrue(self.testData[0] in self.test1.modules[1].data)
        self.test1.modules[0].transferIn(self.testData[1])
        self.assertTrue(self.test1.transfer(self.testData[1],
                                            self.test1.modules[0],
                                            self.test1.modules[1]))
        self.assertTrue(self.testData[0] in self.test1.modules[0].data)
        self.assertTrue(self.testData[1] in self.test1.modules[1].data)
        
        self.test4.commission(self.testLocs[1])
        self.test4.modules[0].transferIn(self.testData[2])
        self.assertFalse(self.test4.transfer(self.testData[2],
                                            self.test4.modules[0],
                                            self.test4.modules[1]))
        self.assertTrue(self.testData[2] in self.test4.modules[0].data)
        self.assertTrue(self.test4.transfer(self.testData[2],
                                            self.test4.modules[0],
                                            self.test4.modules[2]))
        self.assertTrue(self.testData[2] in self.test4.modules[2].data)
    
    def test_couldStore(self):
        self.assertFalse(self.test0.couldStore(self.testData[0]))
        self.assertFalse(self.test0.couldStore(self.testData[2]))
        self.assertTrue(self.test1.couldStore(self.testData[0]))
        self.assertFalse(self.test1.couldStore(self.testData[2]))
        self.assertFalse(self.test1.couldStore(self.testData[4]))
        self.assertTrue(self.test4.couldStore(self.testData[0]))
        self.assertTrue(self.test4.couldStore(self.testData[2]))
    
    def test_canStore(self):
        self.test0.commission(self.testLocs[0])
        self.assertFalse(self.test0.canStore(self.testData[0]))
        self.assertFalse(self.test0.canStore(self.testData[2]))
        
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test1.canStore(self.testData[0]))
        self.assertFalse(self.test1.canStore(self.testData[2]))
        self.assertFalse(self.test1.canStore(self.testData[4]))
        self.test1.modules[0].transferIn(self.testData[1])
        self.assertFalse(self.test1.canStore(self.testData[0]))
        
        self.test4.commission(self.testLocs[1])
        self.assertTrue(self.test4.canStore(self.testData[0]))
        self.assertTrue(self.test4.canStore(self.testData[2]))
        self.assertFalse(self.test4.canStore(self.testData[4]))
        self.assertFalse(self.test4.canStore(self.testData[6]))
    
    def test_store(self):
        self.test0.commission(self.testLocs[0])
        self.assertFalse(self.test0.store(self.testData[0]))
        self.assertFalse(self.test0.store(self.testData[2]))
        
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test1.store(self.testData[0]))
        self.assertTrue(any(self.testData[0] in m.data
                            for m in self.test1.modules))
        self.assertFalse(self.test1.store(self.testData[2]))
        self.assertFalse(self.test1.store(self.testData[4]))
        
        self.test4.commission(self.testLocs[1])
        self.assertTrue(self.test4.store(self.testData[0]))
        self.assertTrue(any(self.testData[0] in m.data
                            for m in self.test4.modules))
        self.assertTrue(self.test4.store(self.testData[1]))
        self.assertTrue(any(self.testData[1] in m.data
                            for m in self.test4.modules))
        self.assertTrue(self.test4.store(self.testData[2]))
        self.assertTrue(any(self.testData[2] in m.data
                            for m in self.test4.modules))
        self.assertFalse(self.test4.store(self.testData[3]))
    
    def test_couldSense(self):
        self.assertFalse(self.test0.couldSense(self.testData[0]))
        self.assertFalse(self.test0.couldSense(self.testData[2]))
        self.assertTrue(self.test1.couldSense(self.testData[0]))
        self.assertFalse(self.test1.couldSense(self.testData[2]))
        self.assertFalse(self.test1.couldSense(self.testData[4]))
        self.assertTrue(self.test4.couldSense(self.testData[0]))
        self.assertTrue(self.test4.couldSense(self.testData[2]))
    
    def test_canSense(self):
        self.test0.commission(self.testLocs[0])
        self.assertFalse(self.test0.canSense(Demand(0,'SAR',1)))
        
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test1.canSense(Demand(0,'SAR',1)))
        self.assertFalse(self.test1.canSense(Demand(1,'SAR',1)))
        self.assertFalse(self.test1.canSense(Demand(0,'SAR',2)))
        self.assertFalse(self.test1.canSense(Demand(0,'VIS',1)))
        
        self.test2.commission(self.testLocs[3])
        self.assertFalse(self.test2.canSense(Demand(0,'SAR',1)))
        
        self.test4.commission(self.testLocs[1])
        self.assertTrue(self.test4.canSense(Demand(0,'SAR',1)))
        self.assertTrue(self.test4.canSense(Demand(0,'VIS',1)))
        self.assertFalse(self.test4.canSense(Demand(0,'SAR',2)))
        self.assertFalse(self.test4.canSense(Demand(0,'VIS',2)))
        
    def test_senseAndStore(self):
        self.test1.commission(self.testLocs[1])
        self.assertTrue(self.test1.senseAndStore(self.testContracts[0]))
        self.assertTrue(any(any(d.contract is self.testContracts[0]
                                for d in m.data)
                            for m in self.test1.modules))
        
        self.test4.commission(self.testLocs[1])
        self.assertTrue(self.test4.senseAndStore(self.testContracts[0]))
        self.assertTrue(any(any(d.contract is self.testContracts[0]
                                for d in m.data)
                            for m in self.test4.modules))
        self.assertTrue(self.test4.senseAndStore(self.testContracts[1]))
        self.assertTrue(any(any(d.contract is self.testContracts[1]
                                for d in m.data)
                            for m in self.test4.modules))
    
    def test_getMaxSensed(self):
        self.assertEqual(self.test0.getMaxSensed(), 0)
        self.assertEqual(self.test1.getMaxSensed(), 1)
        self.assertEqual(self.test1.getMaxSensed('SAR'), 1)
        self.assertEqual(self.test1.getMaxSensed('VIS'), 0)
        self.assertEqual(self.test4.getMaxSensed(), 1+1)
        self.assertEqual(self.test4.getMaxSensed('SAR'), 1)
        self.assertEqual(self.test4.getMaxSensed('VIS'), 1)
    
    def test_getSensed(self):
        self.sim.init()
        self.test1.commission(self.testLocs[1])
        self.assertEqual(self.test1.getSensed(), 0)
        self.assertEqual(self.test1.getSensed('SAR'), 0)
        self.assertEqual(self.test1.getSensed('VIS'), 0)
        self.test1.senseAndStore(self.testContracts[0])
        self.assertEqual(self.test1.getSensed(), 1)
        self.assertEqual(self.test1.getSensed('SAR'), 1)
        self.assertEqual(self.test1.getSensed('VIS'), 0)
        
        self.test4.commission(self.testLocs[1])
        self.assertEqual(self.test4.getSensed(), 0)
        self.assertEqual(self.test4.getSensed('SAR'), 0)
        self.assertEqual(self.test4.getSensed('VIS'), 0)
        self.test4.senseAndStore(self.testContracts[0])
        self.assertEqual(self.test4.getSensed(), 1)
        self.assertEqual(self.test4.getSensed('SAR'), 1)
        self.assertEqual(self.test4.getSensed('VIS'), 0)
        self.test4.senseAndStore(self.testContracts[1])
        self.assertEqual(self.test4.getSensed(), 1+1)
        self.assertEqual(self.test4.getSensed('SAR'), 1)
        self.assertEqual(self.test4.getSensed('VIS'), 1)
        
        self.sim.advance()
        self.assertEqual(self.test1.getSensed(), 0)
        self.assertEqual(self.test1.getSensed('SAR'), 0)
        self.assertEqual(self.test1.getSensed('VIS'), 0)
        self.assertEqual(self.test4.getSensed(), 0)
        self.assertEqual(self.test4.getSensed('SAR'), 0)
        self.assertEqual(self.test4.getSensed('VIS'), 0)
    
    def test_getMaxStored(self):
        self.assertEqual(self.test0.getMaxStored(), 0)
        self.assertEqual(self.test1.getMaxStored(), 1)
        self.assertEqual(self.test1.getMaxStored('SAR'), 1)
        self.assertEqual(self.test1.getMaxStored('VIS'), 0)
        self.assertEqual(self.test4.getMaxStored(), 1+1+1)
        self.assertEqual(self.test4.getMaxStored('SAR'), 1+1)
        self.assertEqual(self.test4.getMaxStored('VIS'), 1+1)
    
    def test_getStored(self):
        self.test1.commission(self.testLocs[1])
        self.assertEqual(self.test1.getStored(), 0)
        self.assertEqual(self.test1.getStored('SAR'), 0)
        self.assertEqual(self.test1.getStored('VIS'), 0)
        self.test1.modules[1].transferIn(self.testData[1])
        self.assertEqual(self.test1.getStored(), 0)
        self.assertEqual(self.test1.getStored('SAR'), 0)
        self.assertEqual(self.test1.getStored('VIS'), 0)
        self.test1.store(self.testData[0])
        self.assertEqual(self.test1.getStored(), 1)
        self.assertEqual(self.test1.getStored('SAR'), 1)
        self.assertEqual(self.test1.getStored('VIS'), 0)
        
        self.test4.commission(self.testLocs[1])
        self.assertEqual(self.test4.getStored(), 0)
        self.assertEqual(self.test4.getStored('SAR'), 0)
        self.assertEqual(self.test4.getStored('VIS'), 0)
        self.test4.store(self.testData[0])
        self.assertEqual(self.test4.getStored(), 1)
        self.assertEqual(self.test4.getStored('SAR'), 1)        
        self.assertEqual(self.test4.getStored('VIS'), 1) # stored in DAT
        self.test4.store(self.testData[1])
        self.assertEqual(self.test4.getStored(), 1+1)
        self.assertEqual(self.test4.getStored('SAR'), 1+1)
        self.assertEqual(self.test4.getStored('VIS'), 1)
        self.test4.store(self.testData[2])
        self.assertEqual(self.test4.getStored(), 1+1+1)
        self.assertEqual(self.test4.getStored('SAR'), 1+1)
        self.assertEqual(self.test4.getStored('VIS'), 1+1)
    
    def test_getMaxTransmitted(self):
        self.assertEqual(self.test0.getMaxTransmitted('pSGL'), 1)
        self.assertEqual(self.test0.getMaxTransmitted('pISL'), 0)
        self.assertEqual(self.test1.getMaxTransmitted('pSGL'), 1)
        self.assertEqual(self.test1.getMaxTransmitted('pISL'), 0)
        self.assertEqual(self.test2.getMaxTransmitted('pSGL'), 0)
        self.assertEqual(self.test2.getMaxTransmitted('pISL'), 2)
        self.assertEqual(self.test4.getMaxTransmitted('pSGL'), 1)
        self.assertEqual(self.test4.getMaxTransmitted('pISL'), 0)
    
    def test_getTransmitted(self):
        self.sim.init()
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.assertEqual(self.test1.getTransmitted('pSGL'), 0)
        self.assertEqual(self.test1.getTransmitted('pISL'), 0)
        self.test1.modules[0].transferIn(self.testData[0])
        self.test1.transmit('pSGL', self.testData[0], self.test0)
        self.assertEqual(self.test1.getTransmitted('pSGL'), 1)
        self.assertEqual(self.test1.getTransmitted('pISL'), 0)

        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.assertEqual(self.test2.getTransmitted('pSGL'), 0)
        self.assertEqual(self.test2.getTransmitted('pISL'), 0)
        self.test2.modules[0].transferIn(self.testData[0])
        self.test2.transmit('pISL', self.testData[0], self.test3)
        self.assertEqual(self.test2.getTransmitted('pSGL'), 0)
        self.assertEqual(self.test2.getTransmitted('pISL'), 1)
        
        self.sim.advance()
        self.assertEqual(self.test1.getTransmitted('pSGL'), 0)
        self.assertEqual(self.test1.getTransmitted('pISL'), 0)
        self.assertEqual(self.test2.getTransmitted('pSGL'), 0)
        self.assertEqual(self.test2.getTransmitted('pISL'), 0)
    
    def test_getMaxReceived(self):
        self.assertEqual(self.test0.getMaxReceived('pSGL'), 1)
        self.assertEqual(self.test0.getMaxReceived('pISL'), 0)
        self.assertEqual(self.test1.getMaxReceived('pSGL'), 1)
        self.assertEqual(self.test1.getMaxReceived('pISL'), 0)
        self.assertEqual(self.test2.getMaxReceived('pSGL'), 0)
        self.assertEqual(self.test2.getMaxReceived('pISL'), 2)
        self.assertEqual(self.test4.getMaxReceived('pSGL'), 1)
        self.assertEqual(self.test4.getMaxReceived('pISL'), 0)
    
    def test_getReceived(self):
        self.sim.init()
        self.test0.commission(self.testLocs[0])
        self.test1.commission(self.testLocs[1])
        self.assertEqual(self.test0.getReceived('pSGL'), 0)
        self.assertEqual(self.test0.getReceived('pISL'), 0)
        self.test0.receive('pSGL', self.testData[0], self.test1)
        self.assertEqual(self.test0.getReceived('pSGL'), 1)
        self.assertEqual(self.test0.getReceived('pISL'), 0)
        
        self.test2.commission(self.testLocs[1])
        self.test3.commission(self.testLocs[5])
        self.assertEqual(self.test3.getReceived('pSGL'), 0)
        self.assertEqual(self.test3.getReceived('pISL'), 0)
        self.test2.modules[0].transferIn(self.testData[0])
        self.test3.receive('pISL', self.testData[0], self.test2)
        self.assertEqual(self.test3.getReceived('pSGL'), 0)
        self.assertEqual(self.test3.getReceived('pISL'), 1)
        
        self.sim.advance()
        self.assertEqual(self.test0.getReceived('pSGL'), 0)
        self.assertEqual(self.test0.getReceived('pISL'), 0)
        self.assertEqual(self.test3.getReceived('pSGL'), 0)
        self.assertEqual(self.test3.getReceived('pISL'), 0)
    
    def test_init(self):
        self.test0.init(self.sim)
        self.test0.commission(self.testLocs[0])
        self.test0.init(self.sim)
        self.assertEqual(self.test0.location, None)
    
    def test_tick(self):
        pass
    
    def test_tock(self):
        pass