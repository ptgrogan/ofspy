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
Test cases for L{ofspy.context.demand}.
"""

import unittest

from ..demand import Demand
from ..data import Data
from ..valueSchedule import ValueSchedule

class DemandTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Demand(0, 'SAR', 1)
        self.basic = Demand(1, 'SAR', 1, ValueSchedule([(0,1)],-1))
    def tearDown(self):
        self.default = None
        self.basic = None
    def test_getValueAt(self):
        self.assertIs(self.default.getValueAt(0),0)
        self.assertIs(self.basic.getValueAt(0),1)
        self.assertIs(self.basic.getValueAt(1),-1)
    def test_getDefaultTime(self):
        self.assertIs(self.default.getDefaultTime(),0)
        self.assertIs(self.basic.getDefaultTime(),0)
    def test_generateData(self):
        self.assertEqual(self.default.generateData().phenomenon, 'SAR')
        self.assertEqual(self.default.generateData().size, 1)
        self.assertEqual(self.basic.generateData().phenomenon, 'SAR')
        self.assertEqual(self.basic.generateData().size, 1)
    def test_isDisturbance(self):
        self.assertFalse(self.default.isDisturbance())
        self.assertFalse(self.basic.isDisturbance())
    def test_isDemand(self):
        self.assertTrue(self.default.isDemand())
        self.assertTrue(self.basic.isDemand())