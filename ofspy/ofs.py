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

import logging
import math

from .game import Game
from .simulator import Simulator

class OFS(object):
    def __init__(self, elements, numPlayers, initialCash,
                 numTurns, seed, ops, fops):
        """
        @param elements: elements
        @type elements: L{str}
        @param numPlayers: number of players
        @type numPlayers: L{int}
        @param initialCash: initial cash
        @type initialCash: L{float}
        @param numTurns: number of turns
        @type numTurns: L{int}
        @param seed: random number seed
        @type seed: L{int}
        @param ops: operations specification
        @type ops: L{str}
        @param fops: federation operations specification
        @type fops: L{str}
        """
        self.game = Game(numPlayers=numPlayers,
                         initialCash=initialCash)
        self.context = self.game.generateContext(
            seed=seed, ops=ops, fops=fops)
        self.sim = Simulator(entities=[self.context],
                             initTime=0,  timeStep=1,
                             maxTime=numTurns)
        if elements is None:
            elements = []
    
        def initializeGame(time):
            federates = [federate for federation in self.context.federations
                         for federate in federation.federates]
            elementSets = []
            for federate in federates:
                elementSets.append([])
            
            for eId, element in enumerate(elements):
                specs = element.split(',')
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
                            elementSets[pId].append({'element':element,
                                                    'location':location})
                            
            for i, elementSet in enumerate(elementSets):
                federate = federates[i]
                if federate.initialCash is None or federate.initialCash == 0:
                    federate.initialCash = 0
                    # special case if 0 initial cash: grant enough for initial element
                    for element in elementSet:
                        federate.initialCash += element['element'].getDesignCost()
                        federate.initialCash += element['element'].getCommissionCost(
                            element['location'], self.context)
                    federate.cash = federate.initialCash
                for element in elementSet:
                    federate.design(element['element'])
                    federate.commission(element['element'], element['location'], self.context)
        
        def finalizeGame(time):
            for federate in [federate for federation in self.context.federations
                             for federate in federation.federates]:
                federate.liquidate(self.context)
                logging.info('{} final cash: {}'
                            .format(federate.name, federate.cash))
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