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
Test cases for L{ofspy.event} package.
"""

import unittest

from ...context.event import Event, Demand, Disturbance, ValueSchedule
from ...player import Data

"""
Test cases for L{ofspy.event.Event} class.
"""

class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Event(0)
    def tearDown(self):
        self.default = None
    def test_isDisturbance(self):
        self.assertFalse(self.default.isDisturbance())
    def test_isDemand(self):
        self.assertFalse(self.default.isDemand())

"""
Test cases for L{ofspy.event.Demand} class.
"""

class DemandTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Demand(0, 'SAR', 1)
        self.basic = Demand(1, 'SAR', 1, ValueSchedule([(0,1)],-1))
    def tearDown(self):
        self.default = None
        self.basic = None
    def test_getValueAt(self):
        self.assertEqual(self.default.getValueAt(0),0)
        self.assertEqual(self.basic.getValueAt(0),1)
        self.assertEqual(self.basic.getValueAt(1),-1)
    def test_getDefaultTime(self):
        self.assertEqual(self.default.getDefaultTime(),0)
        self.assertEqual(self.basic.getDefaultTime(),0)
    def test_getDefaultValue(self):
        self.assertEqual(self.default.getDefaultValue(),0)
        self.assertEqual(self.basic.getDefaultValue(),-1)
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

"""
Test cases for L{ofspy.event.ValueSchedule} class.
"""
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

"""
Test cases for L{ofspy.event.Disturbance} class.
"""

class DisturbanceTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Disturbance(0)
        self.basic = Disturbance(1, 0.2, 1)
    def tearDown(self):
        self.default = None
        self.basic = None
    def test_isDisturbance(self):
        self.assertTrue(self.default.isDisturbance())
        self.assertTrue(self.basic.isDisturbance())
    def test_isDemand(self):
        self.assertFalse(self.default.isDemand())
        self.assertFalse(self.basic.isDemand())
