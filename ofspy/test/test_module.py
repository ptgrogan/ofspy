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
Test cases for L{ofspy.module}.
"""

import unittest

from ..data import Data
from ..module import Module

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
        