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

from ofspy.game import Game
from ofspy.simulator import Simulator

def execute():
    parser = argparse.ArgumentParser(description="This program runs an OFSPY execution.")
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
    
    game = Game(numPlayers=args.numPlayers,
                initialCash=args.initialCash)
    
    context = game.generateContext(seed=args.seed,
                                   ops=args.ops,
                                   fops=args.fops)
    
    sim = Simulator(entities=[context],
                    initTime=0,
                    timeStep=1,
                    maxTime=args.numTurns)

    def initializeGame(time):
        federates = [federate for federation in context.federations
                     for federate in federation.federates]
        designSets = []
        for federate in federates:
            designSets.append([])
        
        for eId, design in enumerate(args.designs):
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
                location = next((l for l in context.locations
                                 if l.name == specs[0].split('@')[1]), None)
                
                # parse modules
                if pId < len(federates) and location is not None:                    
                    # generate elements
                    element = game.generateElement(eType, pId, eId)
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
                        design['location'], context)
                federate.cash = federate.initialCash
            for design in designSet:
                federate.design(design['element'])
                federate.commission(design['element'], design['location'], context)
    
    def finalizeGame(time):
        for federate in [federate for federation in context.federations
                         for federate in federation.federates]:
            federate.liquidate(context)
            logging.info('{0} final cash: {1}'
                        .format(federate.name, federate.cash))
            logging.info('{0} ROI: {1}'
                        .format(federate.name, federate.cash/federate.initialCash))
            print '{0}:{1}'.format(federate.initialCash, federate.cash)
            
    sim.on('init', initializeGame)
    sim.on('complete', finalizeGame)
    sim.execute()
    
if __name__ == '__main__':
    execute()