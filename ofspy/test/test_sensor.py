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
Test cases for L{ofspy.sensor}.
"""

import unittest

from ..data import Data
from ..demand import Demand
from ..surface import Surface
from ..orbit import Orbit
from ..simulator import Simulator
from ..sensor import Sensor
from ..contract import Contract

class SensorTestCase(unittest.TestCase):
    def setUp(self):
        self.sensors = [Sensor(capacity=1, phenomenon='SAR', maxSensed=1),
                        Sensor(capacity=1, phenomenon='VIS', maxSensed=1),
                        Sensor(capacity=2, phenomenon='SAR', maxSensed=2),
                        Sensor(capacity=2, phenomenon='VIS', maxSensed=2)]
        self.sim = Simulator(entities=self.sensors,
                             initTime=0, timeStep=1, maxTime=3)
        
    def tearDown(self):
        self.sensors = None
        self.sim = None
        
    def test_couldSense(self):
        self.assertTrue(self.sensors[0].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[0].couldSense(Data('SAR',2)))
        self.assertFalse(self.sensors[0].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[0].couldSense(Data('VIS',2)))
        
        self.assertFalse(self.sensors[1].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[1].couldSense(Data('SAR',2)))
        self.assertTrue(self.sensors[1].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[1].couldSense(Data('VIS',2)))
        
        self.assertTrue(self.sensors[2].couldSense(Data('SAR',1)))
        self.assertTrue(self.sensors[2].couldSense(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldSense(Data('VIS',1)))
        self.assertFalse(self.sensors[2].couldSense(Data('VIS',2)))
        
        self.assertFalse(self.sensors[3].couldSense(Data('SAR',1)))
        self.assertFalse(self.sensors[3].couldSense(Data('SAR',2)))
        self.assertTrue(self.sensors[3].couldSense(Data('VIS',1)))
        self.assertTrue(self.sensors[3].couldSense(Data('VIS',2)))
    
    def test_canSense(self):
        self.assertTrue(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[0].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Surface(0), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[0].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        
        self.assertTrue(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertTrue(self.sensors[1].canSense(
            Orbit(0,'MEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'GEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Surface(0), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))
        self.assertFalse(self.sensors[1].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'MEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'GEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Surface(0), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Surface(0), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))
        
        self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1)))
        self.assertTrue(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',1)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'SAR',2)))
        self.assertFalse(self.sensors[2].canSense(
            Orbit(0,'LEO'), Demand(0,'VIS',2)))
        
    def test_senseAndStore(self):
        self.assertTrue(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.assertFalse(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[0].data[:]:
            self.sensors[0].transferOut(d)
        self.assertFalse(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.sensors[0].tick(self.sim)
        self.sensors[0].tock()
        self.assertTrue(self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[2].data[:]:
            self.sensors[2].transferOut(d)
        self.assertFalse(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        self.sensors[2].tick(self.sim)
        self.sensors[2].tock()
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1))))
        for d in self.sensors[2].data[:]:
            self.sensors[2].transferOut(d)
        self.sensors[2].tick(self.sim)
        self.sensors[2].tock()
        self.assertTrue(self.sensors[2].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',2))))
        
        self.sensors[1].transferIn(Data('VIS',1))
        self.assertFalse(self.sensors[1].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'VIS',1))))
        for d in self.sensors[1].data[:]:
            self.sensors[1].transferOut(d)
        self.assertTrue(self.sensors[1].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'VIS',1))))
        
    def test_couldTransferIn(self):
        self.assertTrue(self.sensors[0].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('VIS',1)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[0].couldTransferIn(Data('VIS',2)))
        
        self.assertFalse(self.sensors[1].couldTransferIn(Data('SAR',1)))
        self.assertTrue(self.sensors[1].couldTransferIn(Data('VIS',1)))
        self.assertFalse(self.sensors[1].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[1].couldTransferIn(Data('VIS',2)))
        
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',1)))
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',2)))
        
        self.sensors[2].transferIn(Data('SAR', 1))
        
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',1)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',1)))
        self.assertTrue(self.sensors[2].couldTransferIn(Data('SAR',2)))
        self.assertFalse(self.sensors[2].couldTransferIn(Data('VIS',2)))
    
    def test_isSensor(self):
        for sensor in self.sensors:
            self.assertTrue(sensor.isSensor())
    
    def test_init(self):
        self.sensors[0].init(self.sim)
        self.assertEqual(self.sensors[0].sensed, self.sensors[0]._initSensed)
        
        self.sensors[0]._initSensed = 1
        self.sensors[0].init(self.sim)
        self.assertEqual(self.sensors[0].sensed, 1)
    
    def test_tock(self):
        self.sensors[0].init(self.sim)
        self.sensors[0].senseAndStore(
            Orbit(0,'LEO'), Contract(Demand(0,'SAR',1)))
        self.sensors[0].tick(self.sim)
        self.sensors[0].tock()
        self.assertEqual(self.sensors[0].sensed, 0)