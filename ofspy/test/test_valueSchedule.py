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
Test cases for L{ofspy.valueSchedule}.
"""

import unittest

from ..valueSchedule import ValueSchedule

class ValueScheduleTestCase(unittest.TestCase):
    def setUp(self):
        self.default = ValueSchedule()
        self.basic = ValueSchedule([(0,1)], -1)
        self.nonZeroTime = ValueSchedule([(1,1)], -1)
        self.multipleTimes = ValueSchedule([(0,2),(1,1)], -1)
        self.outOfOrderTimes = ValueSchedule([(1,1),(0,2)], -1)
    def tearDown(self):
        self.default = None
        self.basic = None
        self.nonZeroTime = None
        self.multipleTimes = None
        self.outOfOrderTimes = None
    def test_getValueAt(self):
        self.assertEqual(self.default.getValueAt(0), 0)
        self.assertEqual(self.default.getValueAt(1), 0)
        self.assertEqual(self.default.getValueAt(2), 0)
        
        self.assertEqual(self.basic.getValueAt(0), 1)
        self.assertEqual(self.basic.getValueAt(1), -1)
        self.assertEqual(self.basic.getValueAt(2), -1)

        self.assertEqual(self.nonZeroTime.getValueAt(0), 1)
        self.assertEqual(self.nonZeroTime.getValueAt(1), 1)
        self.assertEqual(self.nonZeroTime.getValueAt(2), -1)

        self.assertEqual(self.multipleTimes.getValueAt(0), 2)
        self.assertEqual(self.multipleTimes.getValueAt(1), 1)
        self.assertEqual(self.multipleTimes.getValueAt(2), -1)

        self.assertEqual(self.outOfOrderTimes.getValueAt(0), 2)
        self.assertEqual(self.outOfOrderTimes.getValueAt(1), 1)
        self.assertEqual(self.outOfOrderTimes.getValueAt(2), -1)
    def test_getDefaultTime(self):
        self.assertEqual(self.default.getDefaultTime(), 0)
        self.assertEqual(self.basic.getDefaultTime(), 0)
        self.assertEqual(self.nonZeroTime.getDefaultTime(), 1)
        self.assertEqual(self.multipleTimes.getDefaultTime(), 1)
        self.assertEqual(self.outOfOrderTimes.getDefaultTime(), 1)