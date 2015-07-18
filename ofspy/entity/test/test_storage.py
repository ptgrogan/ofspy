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
Test cases for L{ofspy.entity.storage}.
"""

import unittest

from ofspy.context.data import Data

from ..storage import Storage

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