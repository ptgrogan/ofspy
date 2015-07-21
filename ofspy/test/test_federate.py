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

from ..context import Context
from ..game import Game
from ..simulator import Simulator
from ..federate import Federate

class FederateTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(numPlayers=1, initialCash=2000)
        self.context = self.game.generateContext()
        self.sim = Simulator(entities=[self.context],
                        initTime=0, timeStep=1, maxTime=3)
        self.default = Federate(name='Default')
        self.fed = self.context.federations[0].federates[0]
        self.station = self.game.generateElement('GroundSta',mTypes=['pSGL'])
        self.sat1 = self.game.generateElement('SmallSat',mTypes=['pSGL','SAR'])
        self.sat2 = self.game.generateElement('SmallSat',mTypes=['pSGL','VIS'])
        
    def tearDown(self):
        self.game = None
        self.context = None
        self.sim = None
        self.default = None
        self.fed = None
        self.station = None
        self.sat1 = None
        self.sat2 = None
        
    def test_design(self):
        self.assertFalse(self.default.design(self.station))
        self.assertFalse(self.default.design(self.sat1))
        self.assertTrue(self.fed.design(self.station))
        self.assertEqual(self.fed.cash, self.fed.initialCash - self.station.getDesignCost())
        self.assertTrue(self.station in self.fed.elements)
        self.assertTrue(self.fed.design(self.sat1))
        self.assertEqual(self.fed.cash, self.fed.initialCash - self.station.getDesignCost()
                         - self.sat1.getDesignCost())
        self.assertTrue(self.sat1 in self.fed.elements)
    
    def test_commission(self):
        self.fed.design(self.sat1)
        self.assertFalse(self.fed.commission(
            self.sat1, self.context.locations[0], self.context))
        self.assertTrue(self.fed.commission(
            self.sat1, self.context.locations[3], self.context))
        self.assertEqual(self.sat1.location, self.context.locations[3])
        self.assertEqual(self.fed.cash, self.fed.initialCash
                         - self.sat1.getDesignCost()
                         - self.sat1.getCommissionCost(
                            self.context.locations[3], self.context))
        self.fed.design(self.station)
        self.assertFalse(self.fed.commission(
            self.station, self.context.locations[1], self.context))
        self.assertTrue(self.fed.commission(
            self.station, self.context.locations[0], self.context))
        self.assertEqual(self.station.location, self.context.locations[0])
    
    def test_decommission(self):
        self.assertFalse(self.fed.decommission(self.station))
        self.fed.design(self.station)
        self.fed.commission(self.station, self.context.locations[0], self.context)
        self.assertTrue(self.fed.decommission(self.station))
        self.assertTrue(self.station not in self.fed.elements)
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1, self.context.locations[1], self.context)
        self.assertTrue(self.fed.decommission(self.sat1))
        self.assertTrue(self.sat1 not in self.fed.elements)
    
    def test_liquidate(self):
        self.fed.design(self.station)
        self.fed.commission(self.station, self.context.locations[0], self.context)
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1, self.context.locations[1], self.context)
        self.fed.liquidate(self.context)
        self.assertTrue(self.station not in self.fed.elements)
        self.assertTrue(self.sat1 not in self.fed.elements)
    
    def test_canContract(self):
        self.sim.init()
        self.sim.advance()
        event = next(e for e in self.context.currentEvents
                     if e.name == "VIS2.13")
        self.assertTrue(self.fed.canContract(event, self.context))
        self.assertFalse(self.fed.canContract(
            next(e for e in self.context.futureEvents), self.context))
        
    def test_contract(self):
        self.sim.init()
        self.sim.advance()
        event = next(e for e in self.context.currentEvents
                     if e.name == "VIS2.13")
        contract1 = self.fed.contract(event, self.context)
        self.assertIsNot(contract1, None)
        self.assertIn(contract1, self.fed.contracts)
        contract2 = self.fed.contract(
            next(e for e in self.context.futureEvents), self.context)
        self.assertIs(contract2, None)
        self.assertNotIn(contract2, self.fed.contracts)
        
    def test_canSense(self):
        self.sim.init()
        self.fed.design(self.station)
        self.fed.commission(self.station,
                            self.context.locations[0],
                            self.context)
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1,
                            self.context.locations[1],
                            self.context)
        self.fed.design(self.sat2)
        self.fed.commission(self.sat2,
                            self.context.locations[1],
                            self.context)
        self.sim.advance()
        event = next(e for e in self.context.currentEvents
                     if e.name == "VIS2.13")
        self.assertFalse(self.fed.canSense(event, self.sat1, self.context))
        self.assertTrue(self.fed.canSense(event, self.sat2, self.context))
    
    def test_senseAndStore(self):
        self.sim.init()
        self.fed.design(self.station)
        self.fed.commission(self.station,
                            self.context.locations[0],
                            self.context)
        self.fed.design(self.sat1)
        self.fed.commission(self.sat1,
                            self.context.locations[1],
                            self.context)
        self.fed.design(self.sat2)
        self.fed.commission(self.sat2,
                            self.context.locations[1],
                            self.context)
        self.sim.advance()
        event = next(e for e in self.context.currentEvents
                     if e.name == "VIS2.13")
        self.assertTrue(self.fed.senseAndStore(self.fed.contract(event, self.context),
                                               self.sat2, self.context))
        self.assertEqual(len(self.sat2.modules[1].data), 1)
    
    def test_canTransport(self):
        pass
    
    def test_transport(self):
        pass
    
    def test_default(self):
        pass
    
    def test_deleteData(self):
        pass
    
    def test_getDataLocation(self):
        pass
    
    def test_resolve(self):
        pass
    
    def test_init(self):
        pass
    
    def test_tick(self):
        pass
    
    def test_tock(self):
        pass