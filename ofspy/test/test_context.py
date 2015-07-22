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
Test cases for L{ofspy.context}.
"""

import unittest

from ..federation import Federation
from ..simulator import Simulator
from ..context import Context
from ..surface import Surface
from ..orbit import Orbit
from ..demand import Demand
from ..valueSchedule import ValueSchedule

class ContextTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Context(seed=0)
        self.locs = []
        for s in range(6):
            self.locs.append(Surface(s, name='SUR{0}'.format(s+1)))
            self.locs.append(Orbit(s, 'LEO', name='LEO{0}'.format(s+1)))
            self.locs.append(Orbit(s, 'MEO', name='MEO{0}'.format(s+1)))
            self.locs.append(Orbit(s, 'GEO', name='GEO{0}'.format(s+1)))
        self.evts = []
        for d in range(8):
            self.evts.append(Demand(None, 'SAR', 1,
                                    ValueSchedule([(1,500),(4,400)], -50),
                                    name='SAR1.{0}'.format(d+1)))
        for d in range(12):
            self.evts.append(Demand(None, 'SAR', 1,
                                    ValueSchedule([(2,450),(5,350)], -100),
                                    name='SAR2.{0}'.format(d+1)))
        for d in range(23):
            self.evts.append(Demand(None, 'SAR', 1,
                                    ValueSchedule([(3,400),(6,300)], -150),
                                    name='SAR3.{0}'.format(d+1)))
        for d in range(8):
            self.evts.append(Demand(None, 'VIS', 1,
                                    ValueSchedule([(1,600),(4,500)], -50),
                                    name='VIS1.{0}'.format(d+1)))
        for d in range(17):
            self.evts.append(Demand(None, 'VIS', 1,
                                    ValueSchedule([(2,500),(5,400)], -100),
                                    name='VIS2.{0}'.format(d+1)))
        for d in range(8):
            self.evts.append(Demand(None, 'VIS', 1,
                                    ValueSchedule([(3,450),(6,350)], -150),
                                    name='VIS3.{0}'.format(d+1)))
            
        self.default = Context(locations=self.locs, events=self.evts,
                               federations=[Federation()], seed=0)
        self.sim = Simulator(entities=[self.default],
                             initTime=0, timeStep=1, maxTime=3)
    def tearDown(self):
        self.default = None
        self.locs = None
        self.evts = None
        
    def test_propagate(self):
        self.assertEqual(self.default.propagate(self.locs[0], 0), self.locs[0])
        self.assertEqual(self.default.propagate(self.locs[0], 1), self.locs[0])
        self.assertEqual(self.default.propagate(self.locs[0], 2), self.locs[0])
        self.assertEqual(self.default.propagate(self.locs[1], 0), self.locs[1])
        self.assertEqual(self.default.propagate(self.locs[1], 1), self.locs[9])
        self.assertEqual(self.default.propagate(self.locs[1], 2), self.locs[17])
        self.assertEqual(self.default.propagate(self.locs[1], 3), self.locs[1])
        self.assertEqual(self.default.propagate(self.locs[1], 4), self.locs[9])
        self.assertEqual(self.default.propagate(self.locs[1], -1), self.locs[17])
        self.assertEqual(self.default.propagate(self.locs[2], 0), self.locs[2])
        self.assertEqual(self.default.propagate(self.locs[2], 1), self.locs[6])
        self.assertEqual(self.default.propagate(self.locs[2], 2), self.locs[10])
        self.assertEqual(self.default.propagate(self.locs[3], 0), self.locs[3])
        self.assertEqual(self.default.propagate(self.locs[3], 1), self.locs[3])
        self.assertEqual(self.default.propagate(self.locs[3], 2), self.locs[3])
        
    def test_init(self):
        self.assertEqual(self.default.currentEvents, [])
        self.assertEqual(self.default.futureEvents, [])
        self.assertEqual(self.default.pastEvents, [])
        self.default.init(self.sim)
        self.assertEqual(self.default.currentEvents, [])
        self.assertNotEqual(self.default.futureEvents, [])
        self.assertEqual(len(self.default.futureEvents),
                         len(self.default.events))
        self.assertEqual(self.default.pastEvents, [])
        
    def test_tick(self):
        self.default.init(self.sim)
        self.default.tick(self.sim)
        
    def test_tock(self):
        self.default.init(self.sim)
        self.default.tick(self.sim)
        self.default.tock()
        self.assertEqual(len(self.default.currentEvents), 6)
        self.assertEqual(len(self.default.futureEvents),
                         len(self.default.events) - 6)