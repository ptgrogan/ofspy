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
Test cases for L{ofspy.entity.satellite}.
"""

import unittest

from ofspy.context.orbit import Orbit
from ofspy.context.surface import Surface
from ofspy.sim.simulator import Simulator

from ..satellite import Satellite
from ..storage import Storage
from ..sensor import Sensor
from ..defense import Defense
from ..interSatelliteLink import InterSatelliteLink
from ..spaceGroundLink import SpaceGroundLink

class SatelliteTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Satellite()
        self.test1 = Satellite(cost=200, capacity=2,
                             modules=[Sensor(cost=250,phenomenon='SAR'),
                                      SpaceGroundLink(cost=50,protocol='pSGL')])
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO')]
        self.sim = Simulator(entities=[self.default, self.test1],
                             initTime=0, timeStep=1, maxTime=3)
        
    def tearDown(self):
        self.default = None
        self.test1 = None
        self.testLocs = None
        self.sim = None
        
    def test_canCommission(self):
        self.assertFalse(self.default.canCommission(self.testLocs[0]))
        self.assertTrue(self.default.canCommission(self.testLocs[1]))
        self.assertTrue(self.default.canCommission(self.testLocs[2]))
        self.assertTrue(self.default.canCommission(self.testLocs[3]))
        
    def test_getCommissionCost(self):
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[0]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[1]), 0)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[2]), 200*0.5)
        self.assertEqual(self.test1.getCommissionCost(self.testLocs[3]), 200*1.0)
    
    def test_getDecommissionValue(self):
        self.assertEqual(self.test1.getDecommissionValue(), (200+250+50)*0.5)
        self.test1.commission(self.testLocs[1])
        self.assertEqual(self.test1.getDecommissionValue(), (200+250+50)*0.5)
        self.test1.init(self.sim)
        self.test1.commission(self.testLocs[2])
        self.assertEqual(self.test1.getDecommissionValue(), (200+250+50)*0.5)
        self.test1.init(self.sim)
        self.test1.commission(self.testLocs[3])
        self.assertEqual(self.test1.getDecommissionValue(), (200+250+50)*0.5)
        
    def test_isSpace(self):
        self.assertTrue(self.default.isSpace())
        self.assertTrue(self.test1.isSpace())