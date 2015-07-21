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
Test cases for L{ofspy.interSatelliteLink}.
"""

import unittest

from ..data import Data
from ..surface import Surface
from ..orbit import Orbit
from ..simulator import Simulator

from ..interSatelliteLink import InterSatelliteLink

class InterSatelliteLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.isls = [InterSatelliteLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        InterSatelliteLink(capacity=1, maxTransmitted=1, maxReceived=1),
                        InterSatelliteLink(capacity=2, maxTransmitted=2, maxReceived=2),
                        InterSatelliteLink(capacity=2, maxTransmitted=2, maxReceived=2)]
        self.testData = [Data('SAR',1), Data('VIS',1)]
        self.testLocs = [Surface(0), Orbit(0,'LEO'), Orbit(0,'MEO'), Orbit(0,'GEO'),
                         Surface(1), Orbit(1,'LEO'), Orbit(1,'MEO'), Orbit(1,'GEO'),
                         Surface(2), Orbit(2,'LEO'), Orbit(2,'MEO'), Orbit(2,'GEO')]
        self.sim = Simulator(entities=self.isls,
                             initTime=0, timeStep=1, maxTime=3)
        
    def tearDown(self):
        self.isls = None
        self.testData = None
        self.testLocs = None
        self.sim = None
        
    def test_couldTransmit(self):
        self.assertFalse(self.isls[0].couldTransmit(
            self.testData[0], self.isls[1],
            self.testLocs[0], self.testLocs[0]))
        self.assertFalse(self.isls[0].couldTransmit(
            self.testData[1], self.isls[2],
            self.testLocs[1], self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[2],
                o, self.testLocs[1]))
        for o in self.testLocs[5:8]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[9:12]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[5]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[2].couldTransmit(
                self.testData[1], self.isls[3],
                o, self.testLocs[1]))
    
    def test_couldReceive(self):
        self.assertFalse(self.isls[0].couldReceive(
            self.testData[0], self.isls[1],
            self.testLocs[0], self.testLocs[0]))
        self.assertFalse(self.isls[0].couldReceive(
            self.testData[1], self.isls[2],
            self.testLocs[1], self.testLocs[0]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[2],
                o, self.testLocs[1]))
        for o in self.testLocs[5:8]:
            self.assertTrue(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[9:12]:
            self.assertFalse(self.isls[0].couldReceive(
                self.testData[0], self.isls[1],
                o, self.testLocs[1]))
        for o in self.testLocs[9:12]:
            self.assertTrue(self.isls[0].couldTransmit(
                self.testData[0], self.isls[1],
                o, self.testLocs[5]))
        for o in self.testLocs[1:4]:
            self.assertTrue(self.isls[2].couldReceive(
                self.testData[1], self.isls[3],
                o, self.testLocs[1]))
    
    def test_isSGL(self):
        for isl in self.isls:
            self.assertTrue(isl.isISL())