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
Test cases for L{ofspy.groundStation}.
"""

import unittest

from ..context import Context
from ..orbit import Orbit
from ..surface import Surface
from ..simulator import Simulator
from ..groundStation import GroundStation
from ..storage import Storage
from ..sensor import Sensor
from ..defense import Defense
from ..interSatelliteLink import InterSatelliteLink
from ..spaceGroundLink import SpaceGroundLink

class GroundStationTestCase(unittest.TestCase):
    def setUp(self):
        self.default = GroundStation()
        self.test0 = GroundStation(cost=500, capacity=3,
                             modules=[SpaceGroundLink(cost=50,protocol='pSGL')])
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO')]
        self.sim = Simulator(entities=[self.default, self.test0],
                             initTime=0, timeStep=1, maxTime=3)
        self.context = Context(locations=self.testLocs)
        
    def tearDown(self):
        self.default = None
        self.test1 = None
        self.testLocs = None
        self.sim = None
        self.context = None
        
    def test_canCommission(self):
        self.assertTrue(self.default.canCommission(
            self.testLocs[0], self.context))
        self.assertFalse(self.default.canCommission(
            self.testLocs[1], self.context))
        self.assertFalse(self.default.canCommission(
            self.testLocs[2], self.context))
        self.assertFalse(self.default.canCommission(
            self.testLocs[3], self.context))
        
    def test_getCommissionCost(self):
        self.assertEqual(self.test0.getCommissionCost(
            self.testLocs[0], self.context), 0)
        self.assertEqual(self.test0.getCommissionCost(
            self.testLocs[1], self.context), 0)
        self.assertEqual(self.test0.getCommissionCost(
            self.testLocs[2], self.context), 0)
        self.assertEqual(self.test0.getCommissionCost(
            self.testLocs[3], self.context), 0)
    
    def test_getDecommissionValue(self):
        self.assertEqual(self.test0.getDecommissionValue(), (500+50)*0.5)
        self.test0.commission(self.testLocs[0], self.context)
        self.assertEqual(self.test0.getDecommissionValue(), (500+50)*0.5)
        self.test0.init(self.sim)
        self.test0.commission(self.testLocs[0], self.context)
        self.assertEqual(self.test0.getDecommissionValue(), (500+50)*0.5)
        self.test0.init(self.sim)
        self.test0.commission(self.testLocs[0], self.context)
        self.assertEqual(self.test0.getDecommissionValue(), (500+50)*0.5)
        
    def test_isGround(self):
        self.assertTrue(self.default.isGround())
        self.assertTrue(self.test0.isGround())