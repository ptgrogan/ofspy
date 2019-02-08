"""
Copyright 2015 Paul T. Grogan, Massachusetts Institute of Technology
Copyright 2017 Paul T. Grogan, Massachusetts Institute of Technology

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
Test cases for L{ofspy.player.Contract} class.
"""

import unittest
import logging

from ...context.event import Demand, ValueSchedule
from ...context.location import Surface, Orbit
from ...simulation import Simulator
from ...player import Contract

class ContractTestCase(unittest.TestCase):
    def setUp(self):
        self.contract1 = Contract(Demand(0, 'SAR', 1, ValueSchedule([(0,1)],-1)))
        self.contract2 = Contract(Demand(1, 'SAR', 1, ValueSchedule([(1,4), (2,2)],-1)))
        self.sim = Simulator(entities=set([self.contract1, self.contract2]),
                             initTime=0, timeStep=1, maxTime=3)
        self.surface = Surface(0)
        self.orbit = Orbit(0, 'LEO')

    def tearDown(self):
        self.contract1 = None
        self.contract2 = None
        self.sim = None
        self.surface = None
        self.orbit = None

    def test_getValue(self):
        self.sim.init()
        self.assertEqual(self.contract1.getValue(), 1)
        self.assertEqual(self.contract2.getValue(), 4)
        self.sim.advance()
        self.assertEqual(self.contract1.getValue(), -1)
        self.assertEqual(self.contract2.getValue(), 4)
        self.sim.advance()
        self.assertEqual(self.contract1.getValue(), -1)
        self.assertEqual(self.contract2.getValue(), 2)
        self.sim.advance()
        self.assertEqual(self.contract1.getValue(), -1)
        self.assertEqual(self.contract2.getValue(), -1)

    def test_isDefaulted(self):
        self.sim.init()
        self.assertFalse(self.contract1.isDefaulted(self.orbit))
        self.assertFalse(self.contract2.isDefaulted(self.orbit))
        self.assertFalse(self.contract1.isDefaulted(self.surface))
        self.assertFalse(self.contract2.isDefaulted(self.surface))
        self.assertTrue(self.contract1.isDefaulted(None))
        self.assertTrue(self.contract2.isDefaulted(None))
        self.sim.advance()
        self.assertTrue(self.contract1.isDefaulted(self.orbit))
        self.assertFalse(self.contract2.isDefaulted(self.orbit))
        self.assertTrue(self.contract1.isDefaulted(self.surface))
        self.assertFalse(self.contract2.isDefaulted(self.surface))
        self.assertTrue(self.contract1.isDefaulted(None))
        self.assertTrue(self.contract2.isDefaulted(None))
        self.sim.advance()
        self.assertTrue(self.contract1.isDefaulted(self.orbit))
        self.assertFalse(self.contract2.isDefaulted(self.orbit))
        self.assertTrue(self.contract1.isDefaulted(self.surface))
        self.assertFalse(self.contract2.isDefaulted(self.surface))
        self.assertTrue(self.contract1.isDefaulted(None))
        self.assertTrue(self.contract2.isDefaulted(None))
        self.sim.advance()
        self.assertTrue(self.contract1.isDefaulted(self.orbit))
        self.assertTrue(self.contract2.isDefaulted(self.orbit))
        self.assertTrue(self.contract1.isDefaulted(self.surface))
        self.assertTrue(self.contract2.isDefaulted(self.surface))
        self.assertTrue(self.contract1.isDefaulted(None))
        self.assertTrue(self.contract2.isDefaulted(None))

    def test_isCompleted(self):
        self.sim.init()
        self.assertFalse(self.contract1.isCompleted(self.orbit))
        self.assertFalse(self.contract2.isCompleted(self.orbit))
        self.assertTrue(self.contract1.isCompleted(self.surface))
        self.assertTrue(self.contract2.isCompleted(self.surface))
        self.assertFalse(self.contract1.isCompleted(None))
        self.assertFalse(self.contract2.isCompleted(None))
        self.sim.advance()
        self.assertFalse(self.contract1.isCompleted(self.orbit))
        self.assertFalse(self.contract2.isCompleted(self.orbit))
        self.assertFalse(self.contract1.isCompleted(self.surface))
        self.assertTrue(self.contract2.isCompleted(self.surface))
        self.assertFalse(self.contract1.isCompleted(None))
        self.assertFalse(self.contract2.isCompleted(None))
        self.sim.advance()
        self.assertFalse(self.contract1.isCompleted(self.orbit))
        self.assertFalse(self.contract2.isCompleted(self.orbit))
        self.assertFalse(self.contract1.isCompleted(self.surface))
        self.assertTrue(self.contract2.isCompleted(self.surface))
        self.assertFalse(self.contract1.isCompleted(None))
        self.assertFalse(self.contract2.isCompleted(None))
        self.sim.advance()
        self.assertFalse(self.contract1.isCompleted(self.orbit))
        self.assertFalse(self.contract2.isCompleted(self.orbit))
        self.assertFalse(self.contract1.isCompleted(self.surface))
        self.assertFalse(self.contract2.isCompleted(self.surface))
        self.assertFalse(self.contract1.isCompleted(None))
        self.assertFalse(self.contract2.isCompleted(None))

    def test_init(self):
        self.contract1.init(self.sim)
        self.assertEqual(self.contract1.elapsedTime, self.contract1._initElapsedTime)

        self.contract1._initElapsedTime = 1
        self.contract1.init(self.sim)
        self.assertEqual(self.contract1.elapsedTime, 1)

    def test_tick(self):
        self.contract1.init(self.sim)
        self.contract2.init(self.sim)
        self.contract1.tick(self.sim)
        self.contract2.tick(self.sim)
        self.assertEqual(self.contract1.elapsedTime, self.sim.initTime)
        self.assertEqual(self.contract2.elapsedTime, self.sim.initTime)
        self.contract1.tock()
        self.contract2.tock()
        self.contract1.tick(self.sim)
        self.contract2.tick(self.sim)
        self.assertEqual(self.contract1.elapsedTime, self.sim.timeStep)
        self.assertEqual(self.contract2.elapsedTime, self.sim.timeStep)

    def test_tock(self):
        self.contract1.init(self.sim)
        self.contract2.init(self.sim)
        self.contract1.tick(self.sim)
        self.contract2.tick(self.sim)
        self.contract1.tock()
        self.contract2.tock()
        self.assertEqual(self.contract1.elapsedTime, self.sim.timeStep)
        self.assertEqual(self.contract2.elapsedTime, self.sim.timeStep)
        self.contract1.tick(self.sim)
        self.contract2.tick(self.sim)
        self.contract1.tock()
        self.contract2.tock()
        self.assertEqual(self.contract1.elapsedTime, 2*self.sim.timeStep)
        self.assertEqual(self.contract2.elapsedTime, 2*self.sim.timeStep)
