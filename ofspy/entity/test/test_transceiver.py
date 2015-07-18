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
Test cases for L{ofspy.entity.transceiver}.
"""

import unittest

from ofspy.context.data import Data
from ofspy.sim.simulator import Simulator

from ..transceiver import Transceiver

class TransceiverTestCase(unittest.TestCase):
    def setUp(self):
        self.transceivers = [Transceiver(capacity=1, maxTransmitted=1, maxReceived=1),
                        Transceiver(capacity=1, maxTransmitted=1, maxReceived=1),
                        Transceiver(capacity=2, maxTransmitted=2, maxReceived=2),
                        Transceiver(capacity=2, maxTransmitted=2, maxReceived=2)]
        self.testData = [Data('SAR',1), Data('SAR',1), Data('VIS',1), Data('VIS',1),
                         Data('SAR',2), Data('SAR',2), Data('VIS',2), Data('VIS',2)]
        self.sim = Simulator(entities=self.transceivers,
                             initTime=0, timeStep=1, maxTime=3)
        
    def tearDown(self):
        self.transceivers = None
        self.testData = None
        self.sim = None
        
    def test_couldTransmit(self):
        self.assertTrue(self.transceivers[0].couldTransmit(
            self.testData[0], self.transceivers[1]))
        self.assertTrue(self.transceivers[0].couldTransmit(
            self.testData[2], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].couldTransmit(
            self.testData[4], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].couldTransmit(
            self.testData[6], self.transceivers[1]))
        
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[0], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[2], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[4], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[6], self.transceivers[3]))
        
        self.assertTrue(self.transceivers[0].couldTransmit(
            self.testData[0], self.transceivers[0]))
        self.assertFalse(self.transceivers[0].couldTransmit(
            self.testData[4], self.transceivers[0]))
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[0], self.transceivers[2]))
        self.assertTrue(self.transceivers[2].couldTransmit(
            self.testData[4], self.transceivers[2]))
    
    def test_canTransmit(self):
        self.assertFalse(self.transceivers[0].canTransmit(
            self.testData[0], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].canTransmit(
            self.testData[2], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].canTransmit(
            self.testData[4], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].canTransmit(
            self.testData[6], self.transceivers[1]))
        
        self.transceivers[0].transferIn(self.testData[0])
        self.assertTrue(self.transceivers[0].canTransmit(
            self.testData[0], self.transceivers[1]))
        self.transceivers[0].transmit(self.testData[0], self.transceivers[1])
        self.transceivers[0].transferIn(self.testData[2])
        self.assertFalse(self.transceivers[0].canTransmit(
            self.testData[2], self.transceivers[1]))
        
        self.assertFalse(self.transceivers[2].canTransmit(
            self.testData[0], self.transceivers[3]))
        self.assertFalse(self.transceivers[2].canTransmit(
            self.testData[2], self.transceivers[3]))
        self.assertFalse(self.transceivers[2].canTransmit(
            self.testData[4], self.transceivers[3]))
        
        self.transceivers[2].transferIn(self.testData[0])
        self.assertTrue(self.transceivers[2].canTransmit(
            self.testData[0], self.transceivers[3]))
        self.transceivers[2].transmit(self.testData[0], self.transceivers[3])
        self.transceivers[2].transferIn(self.testData[1])
        self.assertTrue(self.transceivers[2].canTransmit(
            self.testData[1], self.transceivers[3]))
        self.transceivers[2].transmit(self.testData[1], self.transceivers[3])
        self.transceivers[2].transferIn(self.testData[2])
        self.assertFalse(self.transceivers[2].canTransmit(
            self.testData[2], self.transceivers[3]))
        self.transceivers[2].transferOut(self.testData[2])
        
        self.transceivers[2].tick(self.sim)
        self.transceivers[2].tock()
        
        self.transceivers[2].transferIn(self.testData[4])
        self.assertTrue(self.transceivers[2].canTransmit(
            self.testData[4], self.transceivers[3]))
        self.transceivers[2].transmit(self.testData[4], self.transceivers[3])
        self.transceivers[2].transferIn(self.testData[5])
        self.assertFalse(self.transceivers[2].canTransmit(
            self.testData[5], self.transceivers[3]))
        
    def test_transmit(self):
        self.transceivers[0].transferIn(self.testData[0])
        self.assertTrue(self.transceivers[0].transmit(
            self.testData[0], self.transceivers[1]))
        self.assertTrue(self.testData[0] not in self.transceivers[0].data)
        
        self.assertFalse(self.transceivers[0].transmit(
            self.testData[1], self.transceivers[1]))
        
        self.transceivers[2].transferIn(self.testData[2])
        self.assertTrue(self.transceivers[2].transmit(
            self.testData[2], self.transceivers[3]))
        self.assertTrue(self.testData[2] not in self.transceivers[2].data)
        self.transceivers[2].transferIn(self.testData[3])
        self.assertTrue(self.transceivers[2].transmit(
            self.testData[3], self.transceivers[3]))
        self.assertTrue(self.testData[3] not in self.transceivers[2].data)
        
        self.transceivers[2].tick(self.sim)
        self.transceivers[2].tock()
        
        self.transceivers[2].transferIn(self.testData[2])
        self.assertTrue(self.transceivers[2].transmit(
            self.testData[2], self.transceivers[3]))
        self.assertTrue(self.testData[2] not in self.transceivers[2].data)
        self.transceivers[2].transferIn(self.testData[6])
        self.assertFalse(self.transceivers[2].transmit(
            self.testData[6], self.transceivers[3]))
        self.assertTrue(self.testData[6] in self.transceivers[2].data)
        self.transceivers[2].transferOut(self.testData[6])
        
        self.transceivers[2].tick(self.sim)
        self.transceivers[2].tock()
        
        self.transceivers[2].transferIn(self.testData[4])
        self.assertTrue(self.transceivers[2].transmit(
            self.testData[4], self.transceivers[3]))
        self.assertTrue(self.testData[4] not in self.transceivers[2].data)
        self.transceivers[2].transferIn(self.testData[1])
        self.assertFalse(self.transceivers[0].transmit(
            self.testData[1], self.transceivers[1]))
        self.assertTrue(self.testData[1] in self.transceivers[2].data)
    
    def test_couldReceive(self):
        self.assertTrue(self.transceivers[0].couldReceive(
            self.testData[0], self.transceivers[1]))
        self.assertTrue(self.transceivers[0].couldReceive(
            self.testData[2], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].couldReceive(
            self.testData[4], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].couldReceive(
            self.testData[6], self.transceivers[1]))
        
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[0], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[2], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[4], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[6], self.transceivers[3]))
        
        self.assertTrue(self.transceivers[0].couldReceive(
            self.testData[0], self.transceivers[0]))
        self.assertFalse(self.transceivers[0].couldReceive(
            self.testData[4], self.transceivers[0]))
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[0], self.transceivers[2]))
        self.assertTrue(self.transceivers[2].couldReceive(
            self.testData[4], self.transceivers[2]))
    
    def test_canReceive(self):
        self.assertTrue(self.transceivers[0].canReceive(
            self.testData[0], self.transceivers[1]))
        self.assertTrue(self.transceivers[0].canReceive(
            self.testData[2], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].canReceive(
            self.testData[4], self.transceivers[1]))
        self.assertFalse(self.transceivers[0].canReceive(
            self.testData[6], self.transceivers[1]))
        
        self.transceivers[0].receive(self.testData[0], self.transceivers[1])
        self.assertFalse(self.transceivers[0].canReceive(
            self.testData[1], self.transceivers[1]))
        self.transceivers[0].transferOut(self.testData[0])
        self.assertFalse(self.transceivers[0].canReceive(
            self.testData[1], self.transceivers[1]))
        
        self.assertTrue(self.transceivers[2].canReceive(
            self.testData[0], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].canReceive(
            self.testData[2], self.transceivers[3]))
        self.assertTrue(self.transceivers[2].canReceive(
            self.testData[4], self.transceivers[3]))
        
        self.transceivers[2].receive(self.testData[0], self.transceivers[3])
        self.assertTrue(self.transceivers[2].canReceive(
            self.testData[1], self.transceivers[3]))
        self.transceivers[2].receive(self.testData[1], self.transceivers[3])
        self.assertFalse(self.transceivers[2].canReceive(
            self.testData[2], self.transceivers[3]))
        self.transceivers[2].transferOut(self.testData[0])
        self.transceivers[2].transferOut(self.testData[1])
        self.assertFalse(self.transceivers[2].canReceive(
            self.testData[2], self.transceivers[3]))
        
        self.transceivers[2].tick(self.sim)
        self.transceivers[2].tock()
        
        self.assertTrue(self.transceivers[2].canReceive(
            self.testData[4], self.transceivers[3]))
        self.transceivers[2].receive(self.testData[4], self.transceivers[3])
        self.transceivers[2].transferOut(self.testData[4])
        self.assertFalse(self.transceivers[2].canReceive(
            self.testData[0], self.transceivers[3]))
    
    def test_receive(self):     
        self.assertTrue(self.transceivers[0].receive(
            self.testData[0], self.transceivers[1]))
        self.assertTrue(self.testData[0] in self.transceivers[0].data)
        self.assertFalse(self.transceivers[0].receive(
            self.testData[1], self.transceivers[1]))
        self.transceivers[0].transferOut(self.testData[0])
                
        self.assertTrue(self.transceivers[2].receive(
            self.testData[0], self.transceivers[3]))
        self.assertTrue(self.testData[0] in self.transceivers[2].data)
        self.assertTrue(self.transceivers[2].receive(
            self.testData[1], self.transceivers[3]))
        self.assertTrue(self.testData[1] in self.transceivers[2].data)
        self.assertFalse(self.transceivers[2].receive(
            self.testData[2], self.transceivers[3]))
        self.transceivers[2].transferOut(self.testData[0])
        self.transceivers[2].transferOut(self.testData[1])
        self.assertFalse(self.transceivers[2].receive(
            self.testData[2], self.transceivers[3]))
        
        self.transceivers[2].tick(self.sim)
        self.transceivers[2].tock()
        
        self.assertTrue(self.transceivers[2].receive(
            self.testData[4], self.transceivers[3]))
        self.assertTrue(self.testData[4] in self.transceivers[2].data)
        self.transceivers[2].transferOut(self.testData[4])
        self.assertFalse(self.transceivers[2].receive(
            self.testData[0], self.transceivers[3]))
    
    def test_isTransceiver(self):
        for transceiver in self.transceivers:
            self.assertTrue(transceiver.isTransceiver())
    
    def test_init(self):
        self.transceivers[0].init(self.sim)
        self.assertIs(self.transceivers[0].transmitted,
                      self.transceivers[0]._initTransmitted)
        self.assertIs(self.transceivers[0].received,
                      self.transceivers[0]._initReceived)
        
        self.transceivers[0]._initTransmitted = 1
        self.transceivers[0]._initReceived = 1
        self.transceivers[0].init(self.sim)
        self.assertIs(self.transceivers[0].transmitted, 1)
        self.assertIs(self.transceivers[0].received, 1)
    
    def test_tock(self):
        self.transceivers[0].init(self.sim)
        self.transceivers[1].init(self.sim)
        self.transceivers[0].transmit(Data('SAR',1), self.transceivers[1])
        self.transceivers[0].tick(self.sim)
        self.transceivers[1].tick(self.sim)
        self.transceivers[0].tock()
        self.transceivers[1].tock()
        self.assertIs(self.transceivers[0].transmitted, 0)
        self.assertIs(self.transceivers[1].received, 0)