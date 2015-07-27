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

import argparse
import csv
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from functools import partial
import itertools
import logging
import numpy as np
import pymongo
import random
from scoop import futures
import sys,os
# add ofspy to system path
sys.path.append(os.path.abspath('..'))

from ofspy.ofs import OFS

parser = argparse.ArgumentParser(description="This program runs an OFS generic algorithm.")
parser.add_argument('-d', '--numTurns', type=int, default=24,
                    help='simulation duration (number of turns)')
parser.add_argument('-o', '--ops', type=str, default='n',
                    help='federate operations model specification')
parser.add_argument('-f', '--fops', type=str, default='d6,a,1',
                    help='federation operations model specification')
parser.add_argument('-l', '--logging', type=str, default='error',
                    choices=['debug','info','warning','error'],
                    help='logging level')
parser.add_argument('-s', '--seed', type=int, default=0,
                    help='random number seed')
parser.add_argument('-N', '--numExecutions', type=int, default=10,
                    help='number of executions per design')
parser.add_argument('-g', '--numGenerations', type=int, default=20,
                    help='number of generations')
parser.add_argument('-n', '--maxSatsEach', type=int, default=2,
                    help='maximum satellites per player')
parser.add_argument('-c', '--maxCost', type=int, default=4000,
                    help='maximum total cost')
parser.add_argument('-x', '--probCross', type=float, default=0.5,
                    help='probability of crossing')
parser.add_argument('-m', '--probMutate', type=float, default=0.2,
                    help='probability of mutation')
parser.add_argument('-p', '--initPopulation', type=int, default=200,
                    help='initial population')
parser.add_argument('--dbHost', type=str, default=None,
                    help='database host')
parser.add_argument('--dbPort', type=int, default=27017,
                    help='database port')

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

    
if args.dbHost is None:
    db = None
else:
    db = pymongo.MongoClient(args.dbHost, args.dbPort).ofs

def enumSatellites(player, capacity, orbit, sector, sgl, isl):
    """
    Enumerates all satellite definitions for a set of constraints.
    @param player: the player to design the satellite
    @type player: L{int}
    @param capacity: the capacity of the satellite for modules
    @type capacity: L{int}
    @param orbit: the orbit in which to commission the satellite
    @type orbit: L{int}
    @param sector: the sector in which to commission the satellite
    @type sector: L{int}
    @param sgl: the SGL protocol used by the satellite
    @type sgl: L{str}
    @param isl: the ISL protocol used by the satellite
    @type isl: L{str}
    @return: L{str}
    """
    size = ''
    if capacity == 2:
        size='Small'
    elif capacity == 4:
        size='Medium'
    elif capacity == 6:
        size='Large'
    allSpecs = itertools.combinations(
        ['VIS','SAR','DAT',sgl,isl,None],capacity)
    specs = [i for i in allSpecs
             if (sgl in i or isl in i)
             and (not sgl in i or ('VIS' in i or 'SAR' in i or isl in i))
             and (not isl in i or ('VIS' in i or 'SAR' in i or 'DAT' in i or sgl in i))
             and len([j for j in i if j is None]) < 2
             and ('GEO' != orbit or not ('VIS' in i or 'SAR' in i))]
    out = map(lambda mods: '{}.{}Sat@{}{}{}{}'.format(
        player, size, orbit, sector,
        ',' if len([i for i in mods if i is not None])>0 else '',
        ','.join([i for i in mods if i is not None])), specs)
    out.sort(sortBySize)
    return out

def sortBySize(a, b):
    """
    Sorts a set of satellite definitions by size.
    @param a: a satellite definition
    @type a: L{str}
    @param b: a satellite definition
    @type b: L{str}
    @return: L{int}
    """
    if isinstance(a, list) and isinstance(b, list):
        a = " ".join(a)
        b = " ".join(b)
    if a.count(',') == b.count(','):
        if a.count('VIS')+a.count('SAR')+a.count('DAT') \
                == b.count('VIS')+b.count('SAR')+b.count('DAT'):
            if a.count('VIS')+a.count('SAR') == b.count('VIS')+b.count('SAR'):
                if a.count('VIS') == b.count('VIS'):
                    if a.count('SAR') == b.count('SAR'):
                        return len(a) - len(b)
                    else:
                        return a.count('SAR') - b.count('SAR')
                else:
                    return a.count('VIS') - b.count('VIS')
            else:
                return a.count('VIS')+a.count('SAR') - b.count('VIS')+b.count('SAR')
        else:
            return a.count('VIS')+a.count('SAR')+a.count('DAT') \
                    - b.count('VIS')+b.count('SAR')+b.count('DAT')
    else:
        return a.count(',') - b.count(',')

def enum1x1Sats(player, sector, sgl, isl):
    """
    Enumerates all 1-player, 1-satellite definitions.
    @param player: the player to design the satellite
    @type player: L{int}
    @param sector: the sector in which to commission the satellite
    @type sector: L{int}
    @param sgl: the SGL protocol used by the satellite
    @type sgl: L{str}
    @param isl: the ISL protocol used by the satellite
    @type isl: L{str}
    @return: L{str}
    """
    out = enumSatellites(player, 2, 'MEO', sector, sgl, isl) \
            + enumSatellites(player, 4, 'MEO', sector, sgl, isl) \
            + enumSatellites(player, 6, 'MEO', sector, sgl, isl)
    out.sort(sortBySize)
    return out

prototypes = ['']
prototypes.extend(enum1x1Sats(1,1,'pSGL','pISL'))
prototypes.extend(enum1x1Sats(1,1,'pSGL','oISL'))
prototypes.extend(enum1x1Sats(1,1,'oSGL','pISL'))
prototypes.extend(enum1x1Sats(1,1,'oSGL','oISL'))
prototypes.sort(sortBySize)
    
creator.create("FitnessMax", base.Fitness, weights=(-1.0,1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_sat", random.randint,
                 0, len(prototypes)-1)
toolbox.register("individual", tools.initRepeat,
                 creator.Individual, toolbox.attr_sat,
                 2*args.maxSatsEach)
toolbox.register("population", tools.initRepeat,
                 list, toolbox.individual)

def queryCase((elements, numPlayers, initialCash,
               numTurns, seed, ops, fops)):
    """
    Queries and retrieves existing results or executes an OFS simulation.
    @param elements: the design specifications
    @type elements: L{list}
    @param numPlayers: the number of players
    @type numPlayers: L{int}
    @param initialCash: the initial cash
    @type initialCash: L{int}
    @param numTurns: the number of turns
    @type numTurns: L{int}
    @param seed: the random number seed
    @type seed: L{int}
    @param ops: the operations definition
    @type ops: L{str}
    @param fops: the federation operations definition
    @type fops: L{str}
    @return: L{list}
    """
    global db
    
    if db is None:
        return executeCase((elements, numPlayers, initialCash,
                            numTurns, seed, ops, fops))
        
    query = {u'elements': ' '.join(elements),
             u'numPlayers':numPlayers,
             u'initialCash':initialCash,
             u'numTurns':numTurns,
             u'seed':seed,
             u'ops':ops,
             u'fops': fops}
    doc = db.ga.find_one(query)
    if doc is None:
        doc = db.results.find_one(query)
        if doc is None:
            results = executeCase((elements, numPlayers, initialCash, 
                                   numTurns, seed, ops, fops))
            doc = {u'elements': ' '.join(elements),
                   u'numPlayers':numPlayers,
                   u'initialCash':initialCash,
                   u'numTurns':numTurns,
                   u'seed':seed,
                   u'ops':ops,
                   u'fops': fops,
                   u'results': results}
            db.results.insert_one(doc)
        db.ga.insert_one(doc)
    return [tuple(result) for result in doc[u'results']]

def executeCase((elements, numPlayers, initialCash, numTurns, seed, ops, fops)):
    """
    Executes an OFS simulation.
    @param elements: the design specifications
    @type elements: L{list}
    @param numPlayers: the number of players
    @type numPlayers: L{int}
    @param initialCash: the initial cash
    @type initialCash: L{int}
    @param numTurns: the number of turns
    @type numTurns: L{int}
    @param seed: the random number seed
    @type seed: L{int}
    @param ops: the operations definition
    @type ops: L{str}
    @param fops: the federation operations definition
    @type fops: L{str}
    """
    return OFS(elements=elements, numPlayers=numPlayers, initialCash=initialCash,
               numTurns=numTurns, seed=seed, ops=ops, fops=fops).execute()
        
def getSatellite(i, player, sector):
    """
    Gets the specified satellite definition.
    @param i: the prototype id
    @type i: L{int}
    @param player: the player to design the satellite
    @type player: L{int}
    @param sector: the sector in which to commission the satellite
    @type sector: L{int}
    @return: L{str}
    """
    global prototypes
    
    return prototypes[i].replace("1.", str(player)+".") \
            .replace("MEO1","MEO"+str(sector))

def getIndividual(individual, maxSatsEach):
    """
    Decodes the GA individual to a design definition.
    @param individual: the individual
    @type individual: L{list}
    @param maxSatsEach: the max number of satellites
    @type maxSatsEach: L{int}
    @return: L{str}
    """
    satellites = []
    offsets = np.cumsum(np.array(individual) > 0)
    for i in range(maxSatsEach):
        satellites.append(getSatellite(
            individual[i], 1, (6 - offsets[i] % 6) + 1))
    for i in range(maxSatsEach, 2*maxSatsEach):
        satellites.append(getSatellite(
            individual[i], 2, (6 - offsets[i] % 6) + 1))
    
    stations = []
    p1Station= '1.GroundSta@SUR1';
    for i in range(0, maxSatsEach):
        if 'pSGL' in satellites[i] and 'pSGL' not in p1Station:
            p1Station += ',pSGL'
    for i in range(0, 2*maxSatsEach):
        if 'oSGL' in satellites[i] and 'oSGL' not in p1Station:
            p1Station += ',oSGL'
    stations.append(p1Station)
        
    p2Station = '2.GroundSta@SUR'+str((6 - offsets[maxSatsEach] % 6) + 1);
    for i in range(maxSatsEach, 2*maxSatsEach):
        if 'pSGL' in satellites[i] and 'pSGL' not in p2Station:
            p2Station += ',pSGL'
    for i in range(0, 2*maxSatsEach):
        if 'oSGL' in satellites[i] and 'oSGL' not in p2Station:
            p2Station += ',oSGL'
    stations.append(p2Station)
    
    return '{} {}'.format(' '.join([s for s in satellites if s != '']),
                          ' '.join(stations))

def evalIndividual(individual, numTurns, ops, fops,
                   maxSatsEach, maxCost, numExecutions):
    """
    Evaluates the GA individual and returns the expected cost and value.
    @param individual: the individual
    @type individual: L{list}
    @param numTurns: the number of turns
    @type numTurns: L{int}
    @param ops: the operations specification
    @type ops: L{int}
    @param fops: the federation operations specification
    @type fops: L{int}
    @param maxSatsEach: the max number of satellites
    @type maxSatsEach: L{int}
    @param maxCost: the maximum cost allowed
    @type maxCost: L{int}
    @param numExecutions: the number of executions to perform
    @type numExecutions: L{int}
    @return: L{tuple}
    """
    elements = [e for e in getIndividual(
        individual, maxSatsEach).split(' ') if e != '']
    results = []
    for seed in range(numExecutions):
        results.append(queryCase((elements, 2, 0, numTurns,
                                  seed, ops, fops)))
    
    costs = [sum(r[0] for r in result) for result in results]
    values = [sum(r[1] for r in result) for result in results]
    netValues = [sum(r[1] - r[0] for r in result)
                     for result in results]
    expCost = sum(costs)/len(costs)
    expValue = sum(values)/len(values)
    if expCost > maxCost:
        return maxCost, 0
    else:
        return expCost, expValue

toolbox.register("evaluate", partial(evalIndividual,
                                     numTurns=args.numTurns,
                                     ops=args.ops,
                                     fops=args.fops,
                                     maxSatsEach=args.maxSatsEach,
                                     maxCost=args.maxCost,
                                     numExecutions=args.numExecutions))
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt,
                 low=0, up=len(prototypes)-1, indpb=0.05)
toolbox.register("select", tools.selNSGA2)
toolbox.register("map", futures.map)

def executeGA(numTurns, ops, fops, maxSatsEach, maxCost,
              numGenerations, probCross, probMutate,
              initPopulation, seed):
    """
    Executes a GA.
    @param numTurns: the number of turns
    @type numTurns: L{int}
    @param ops: the operations specification
    @type ops: L{int}
    @param fops: the federation operations specification
    @type fops: L{int}
    @param maxSatsEach: the max number of satellites
    @type maxSatsEach: L{int}
    @param maxCost: the maximum cost allowed
    @type maxCost: L{int}
    @param numGenerations: the number of generations
    @type numGenerations: L{int}
    @param probCross: the probability of crossing
    @type probCross: L{float}
    @param probMutate: the probability of mutation
    @type probMutate: L{float}
    @param initPopulation: the initial population size
    @type initPopulation: L{int}
    @param seed: the random number seed
    @type seed: L{int}
    """
    global db
    db.ga.delete_many({}) # clear old results from ga
    
    random.seed(seed)
    
    pop = toolbox.population(n=initPopulation)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    
    pop = algorithms.eaSimple(pop, toolbox, cxpb=probCross,
                              mutpb=probMutate, ngen=numGenerations,
                              stats=stats, halloffame=hof, verbose=True)
    print 'Pareto Front:'
    print '{0:>12} {1:>12} {2}'.format("Exp. Cost", "Exp. Value", "Definition")
    for individual in hof:
        print "{0:12.1f} {1:12.1f} {2}\n".format(
            individual.fitness.values[0], 
            individual.fitness.values[1], 
            getIndividual(individual, maxSatsEach))
    with open('data-ga.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Individual', 'Total Cost',
                         'Exp. Value', 'Exp. Net Value'])
        for individual in hof:
            writer.writerow([getIndividual(individual, maxSatsEach),
                             individual.fitness.values[0],
                             individual.fitness.values[1],
                             individual.fitness.values[1] - 
                             individual.fitness.values[0]])
    
if __name__ == '__main__':    
    executeGA(args.numTurns, args.ops, args.fops,
              args.maxSatsEach, args.maxCost,
              args.numGenerations, args.probCross,
              args.probMutate, args.initPopulation, args.seed)