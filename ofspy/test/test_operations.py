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
Test cases for L{ofspy.federate}.
"""

import unittest
import logging

#logging.disable(logging.WARNING)

from ..context import Context
from ..game import Game
from ..simulator import Simulator
from ..operations import Operations
from ..operations import DynamicOperations

class OperationsTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(numPlayers=1, initialCash=2000)
        self.context = self.game.generateContext()
        self.sim = Simulator(entities=[self.context],
                        initTime=0, timeStep=1, maxTime=3)
        self.fed = self.context.federations[0].federates[0]
        self.station = self.game.generateElement('GroundSta',pId=0,eId=0,mTypes=['pSGL'])
        self.sat1 = self.game.generateElement('SmallSat',pId=0,eId=1,mTypes=['pSGL','SAR'])
        self.sat2 = self.game.generateElement('SmallSat',pId=0,eId=2,mTypes=['pSGL','VIS'])
        self.sat3 = self.game.generateElement('MediumSat',pId=0,eId=3,mTypes=['pSGL','SAR','VIS'])
        
    def tearDown(self):
        self.game = None
        self.context = None
        self.sim = None
        self.fed = None
        self.sat1 = None
        self.sat2 = None
        self.sat3 = None
        
class OperationsGetStoragePenaltyTestCase(OperationsTestCase):
    def test_getStoragePenalty(self):
        self.sim.init()
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1, self.context.locations[1], self.context)
        self.fed.design(self.sat2)
        self.fed.commission(self.sat2, self.context.locations[1], self.context)
        self.fed.design(self.sat3)
        self.fed.commission(self.sat3, self.context.locations[1], self.context)
        self.ops = Operations()
        self.sim.advance()
        self.assertAlmostEqual(self.ops.getStoragePenalty(
            self.sat1, self.context), -244.7368421)
        self.assertAlmostEqual(self.ops.getStoragePenalty(
            self.sat2, self.context), -222.3684211)
        self.assertAlmostEqual(self.ops.getStoragePenalty(
            self.sat3, self.context), -467.1052632)
        
class DynamicOperationsExecuteTestCase(OperationsTestCase):
    def test_execute(self):
        self.fed.operations = DynamicOperations()
        self.sim.init()
        self.fed.design(self.station)
        self.fed.commission(self.station, self.context.locations[0], self.context)
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1, self.context.locations[1], self.context)
        self.sim.advance()
        self.fed.operations.execute(self.fed, self.context)