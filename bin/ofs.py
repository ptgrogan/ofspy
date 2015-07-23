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

import sys,os
# add ofspy to system path
sys.path.append(os.path.abspath('..'))

import argparse
import logging
import math

from ofspy.game import Game
from ofspy.simulator import Simulator

class OFS(object):
    def __init__(self, designs=None, numPlayers=1,
                 initialCash=1200, numTurns=12,
                 seed=0, ops='d', fops=''):
        """
        @param args: arguments
        @type args: L{object}
        """
        self.game = Game(numPlayers=numPlayers,
                         initialCash=initialCash)
        self.context = self.game.generateContext(
            seed=seed, ops=ops, fops=fops)
        self.sim = Simulator(entities=[self.context],
                             initTime=0,  timeStep=1,
                             maxTime=numTurns)
        if designs is None:
            designs = []
    
        def initializeGame(time):
            federates = [federate for federation in self.context.federations
                         for federate in federation.federates]
            designSets = []
            for federate in federates:
                designSets.append([])
            
            for eId, design in enumerate(designs):
                specs = design.split(',')
                if len(specs) > 0 and len(specs[0].split('@')) == 2:
                    # parse player ownership and element type
                    if len(specs[0].split('@')[0].split('.')) == 2:
                        pId = int(specs[0].split('@')[0].split('.')[0])-1
                        eType = specs[0].split('@')[0].split('.')[1]
                    else:
                        pId = 0
                        eType = specs[0].split('@')[0]
                    
                    # parse location
                    location = next((l for l in self.context.locations
                                     if l.name == specs[0].split('@')[1]), None)
                    
                    # parse modules
                    if pId < len(federates) and location is not None:                    
                        # generate elements
                        element = self.game.generateElement(eType, pId, eId, mTypes=specs[1:])
                        if element is not None:
                            designSets[pId].append({'element':element,
                                                    'location':location})
                            
            for i, designSet in enumerate(designSets):
                federate = federates[i]
                if federate.initialCash == 0:
                    # special case if 0 initial cash: grant enough for initial design
                    for design in designSet:
                        federate.initialCash += design['element'].getDesignCost()
                        federate.initialCash += design['element'].getCommissionCost(
                            design['location'], self.context)
                    federate.cash = federate.initialCash
                for design in designSet:
                    federate.design(design['element'])
                    federate.commission(design['element'], design['location'], self.context)
        
        def finalizeGame(time):
            for federate in [federate for federation in self.context.federations
                             for federate in federation.federates]:
                federate.liquidate(self.context)
                logging.info('{} final cash: {}'
                            .format(federate.name, federate.cash))
                logging.info('{} ROI: {:.2f}'
                            .format(federate.name, (float(federate.cash)/federate.initialCash)
                                    if federate.initialCash != 0 else 0))
                logging.info('{} %ROI/turn: {:.2%}'
                            .format(federate.name, (math.pow(float(federate.cash)
                                                             /federate.initialCash,
                                                             1./self.sim.maxTime)-1)
                                    if federate.initialCash != 0 else 0))
        self.sim.on('init', initializeGame)
        self.sim.on('complete', finalizeGame)
    
    def execute(self):
        """
        Executes an OFS.
        @return: L{list}
        """
        self.sim.execute()
        results = []
        for federate in [federate for federation in self.context.federations
                         for federate in federation.federates]:
            results.append((federate.initialCash, federate.cash))
        return results
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program runs an Orbital Federates simulation.")
    parser.add_argument('designs', type=str, nargs='+',
                        help='the list of initial designs, e.g. 1.GroundSta@SUR1,pSGL 1.SmallSat@LEO1,pSGL,SAR')
    parser.add_argument('-d', '--numTurns', type=int, default=24,
                        help='simulation duration (number of turns)')
    parser.add_argument('-p', '--numPlayers', type=int, default=1,
                        help='number of players')
    parser.add_argument('-i', '--initialCash', type=int, default=1200,
                        help='initial cash')
    parser.add_argument('-s', '--seed', type=int, default=0,
                        help='random number seed')
    parser.add_argument('-o', '--ops', type=str, default='d6',
                        help='federate operations model specification')
    parser.add_argument('-f', '--fops', type=str, default='',
                        help='federation operations model specification')
    parser.add_argument('-l', '--logging', type=str, default='error',
                        choices=['debug','info','warning','error'],
                        help='logging level')
    
    args = parser.parse_args()
    if args.logging == 'debug':
        level = logging.DEBUG
    elif args.logging == 'info':
        level = logging.INFO
    elif args.logging == 'warning':
        level = logging.WARNING
    elif args.logging == 'error':
        level = logging.ERROR
    logging.basicConfig(level=level)
    
    results = OFS(designs=args.designs, numTurns=args.numTurns,
                  numPlayers=args.numPlayers, initialCash=args.initialCash,
                  seed=args.seed, ops=args.ops, fops=args.fops).execute()
    for result in results:
        print '{0}:{1}'.format(result[0], result[1])