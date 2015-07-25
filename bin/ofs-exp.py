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
import itertools
import logging

from scoop import futures

import pymongo

from ofspy.ofs import OFS
    
def enumStations(player, sector, sgl):
    out = map(lambda mods: '{}.GroundSta@SUR{}{}{}'.format(
        player, sector, 
        ',' if len([i for i in mods if i is not None])>0 else '',
        ','.join([i for i in mods if i is not None])),
               itertools.combinations_with_replacement([sgl,None],3))
    out.sort(sortBySize)
    return out

def sizeStation(player, sector, sgl, sats):
    numSGL = reduce(lambda s,i: max(s, i.count(sgl)), sats, 0)
    for sec in range(1,7):
        numSGL = max(numSGL, reduce(lambda s,i: i.count(sgl),
                                    [i for i in sats
                                     if 'EO{}'.format(sec) in i], 0))
    return next(i for i in enumStations(player, sector, sgl)
                if i.count(sgl) == min(3, numSGL))
    
def enumSatellites(player, capacity, orbit, sector, sgl, isl):
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
    out = enumSatellites(player, 2, 'MEO', sector, sgl, isl) \
            + enumSatellites(player, 4, 'MEO', sector, sgl, isl) \
            + enumSatellites(player, 6, 'MEO', sector, sgl, isl)
    out.sort(sortBySize)
    return out

def enumBest1x1Sats(player, sector, sgl, isl):
    return [
        '{}.SmallSat@MEO{},SAR,{}'.format(player, sector, sgl),
        '{}.SmallSat@MEO{},VIS,{}'.format(player, sector, sgl)
    ]

def enum1xNSats(number, player, sector, sgl, isl):
    satsSGL = [enumBest1x1Sats(player, (sector-1+(6-i))%6+1, sgl, isl)
               for i in range(number)]
    satsISL = [enum1x1Sats(player, (sector-1+(6-i))%6+1, sgl, isl)
               for i in range(number)]
    
    out = map(lambda j: ' '.join(map(lambda i: satsSGL[i][j[i]], range(number))),
              [i for i in itertools.combinations_with_replacement(
                range(len(satsSGL[0])), number)
               if all(sgl in satsSGL[0][j]
                      and ('VIS' in satsSGL[0][j]
                           or 'SAR' in satsSGL[0][j])
                      and not isl in satsSGL[0][j]
                      for j in i)]) \
            + map(lambda j: ' '.join(map(lambda i: satsISL[i][j[i]], range(number))),
                  [i for i in itertools.combinations_with_replacement(
                    range(len(satsISL[0])), number)
                   if all(isl in satsISL[0][j]
                          and sgl in satsISL[0][j]
                          for j in i)
                   and any('VIS' in satsISL[0][j]
                           or 'SAR' in satsISL[0][j]
                           or 'ISL' in satsISL[0][j]
                           for j in i)
                   and sum(satsISL[0][j].count('MediumSat')
                           for j in i) <= 2
                   and sum(satsISL[0][j].count('LargeSat')
                           for j in i) <= 1])
    out.sort(sortBySize)
    return out

def enum1xNSatDesigns(number, player, sector, sgl, isl):
    return map(lambda sats: ' '.join([sats, sizeStation(
        player, sector, sgl, sats.split(' '))]),
               enum1xNSats(number, player, (sector-1+(6-1))%6+1, sgl, isl))

def enumPxNSats(number, players, sectors, sgl, isl):
    sats = [enum1xNSats(number, players[i], sectors[i], sgl, isl)
            for i in range(len(players))]
    
    out = map(lambda j: '  '.join(map(lambda i: sats[i][j[i]], range(len(players)))),
              [i for i in itertools.combinations_with_replacement(
                range(len(sats[0])), len(players))
               if all(sgl in sats[0][j]
                      and ('VIS' in sats[0][j]
                           or 'SAR' in sats[0][j])
                      and not isl in sats[0][j]
                      for j in i)
               and sum(sats[0][j].count('MediumSat')
                       for j in i) <= 2
               and sum(sats[0][j].count('LargeSat')
                       for j in i) <= 1]) \
            + map(lambda j: '  '.join(map(lambda i: sats[i][j[i]], range(len(players)))),
                  [i for i in itertools.combinations_with_replacement(
                    range(len(sats[0])), len(players))
                   if all(isl in sats[0][j]
                          and sgl in sats[0][j]
                          for j in i)
                   and any('VIS' in sats[0][j]
                           or 'SAR' in sats[0][j]
                           or 'ISL' in sats[0][j]
                           for j in i)
                   and sum(sats[0][j].count('MediumSat')
                           for j in i) <= 2
                   and sum(sats[0][j].count('LargeSat')
                           for j in i) <= 1])
    out.sort(sortBySize)
    return out

def enumPxNSatDesigns(number, players, sectors, sgl, isl):
    return map(lambda sats: '   '.join(
        [sats, ' '.join(map(lambda i: sizeStation(players[i], sectors[i],
                                         sgl, sats.split('  ')[i].split(' ')),
                   range(len(players))))]),
        enumPxNSats(number, players, 
            map(lambda sector: (sector-1+(6-1))%6+1, sectors), sgl, isl))

def enumSymmetricPxNSats(number, players, sectors, sgl, isl):
    sats = [enum1xNSats(number, players[i], sectors[i], sgl, isl)
            for i in range(len(players))]
    out = map(lambda j: '  '.join(map(lambda i: sats[i][j], range(len(players)))),
                       [i for i in range(len(sats[0]))
                        if 'VIS' in sats[0][i]
                        or 'SAR' in sats[0][i]])
    out.sort(sortBySize)
    return out

def enumSymmetricPxNSatDesigns(number, players, sectors, sgl, isl):
    return map(lambda sats: '   '.join(
        [sats, ' '.join(map(lambda i: sizeStation(players[i], sectors[i],
                                         sgl, sats.split('  ')[i].split(' ')),
                   range(len(players))))]),
        enumSymmetricPxNSats(number, players, 
            map(lambda sector: (sector-1+(6-1))%6+1, sectors), sgl, isl))

def enumMASV():
    out = map(lambda d: d + " 2.MediumSat@MEO1,VIS,SAR,oSGL,oISL 2.GroundSta@SUR4,oSGL",
               set(enumSymmetricPxNSatDesigns(1,[1],[1],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1],[1],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1],[1],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1],[1],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1],[1],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1],[1],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1],[1],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1],[1],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1],[1],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1],[1],'oSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1],[1],'oSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1],[1],'oSGL','oISL')))
    out.sort(sortBySize)
    return out

def executeMASV(dbHost, dbPort, start, stop):
    execute(dbHost, dbPort, start, stop, enumMASV(), 2, 0, 24, 'd6,a,1', 'x50,25,6,a,1')

def enumBVC():
    out = list(set(enumSymmetricPxNSatDesigns(1,[1,2],[1,6],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1,2],[1,5],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1,2],[1,4],'pSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1,2],[1,6],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1,2],[1,5],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1,2],[1,4],'pSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1,2],[1,6],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1,2],[1,5],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1,2],[1,4],'oSGL','pISL'))
                | set(enumSymmetricPxNSatDesigns(1,[1,2],[1,6],'oSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(2,[1,2],[1,5],'oSGL','oISL'))
                | set(enumSymmetricPxNSatDesigns(3,[1,2],[1,4],'oSGL','oISL')))
    out.sort(sortBySize)
    return out

def executeBVC(dbHost, dbPort, start, stop):
    execute(dbHost, dbPort, start, stop, enumBVC(), 2, 0, 24, 'n', 'd6,a,1')

def execute(dbHost, dbPort, start, stop, cases, numPlayers,
            initialCash, numTurns, ops, fops):
    executions = [(dbHost, dbPort, [e for e in elements.split(' ') if e != ''],
        numPlayers, initialCash, numTurns, seed, ops, fops)
        for (seed, elements) in itertools.product(range(start, stop), cases)]
    numComplete = 0.0
    logging.info('Executing {} cases with seeds from {} to {} for {} total executions.'
                 .format(len(cases), start, stop, len(executions)))
    for result in futures.map(queryCase, executions):
        print result

def queryCase((dbHost, dbPort, elements, numPlayers, initialCash, numTurns, seed, ops, fops)):
    if dbHost is None:
        return executeCase((elements, numPlayers, initialCash,
                            numTurns, seed, ops, fops))
    else:
        db = pymongo.MongoClient(dbHost, dbPort).ofs
        doc = db.results.find_one({'elements': ' '.join(elements),
                                   'numPlayers':numPlayers,
                                   'initialCash':initialCash,
                                   'numTurns':numTurns,
                                   'seed':seed,
                                   'ops':ops,
                                   'fops': fops})
        if doc is None:
            results = executeCase((elements, numPlayers, initialCash, 
                                   numTurns, seed, ops, fops))
            db.results.insert_one({'elements': ' '.join(elements),
                                   'numPlayers':numPlayers,
                                   'initialCash':initialCash,
                                   'numTurns':numTurns,
                                   'seed':seed,
                                   'ops':ops,
                                   'fops': fops,
                                   'results': results})
        else:
            results = [tuple(result) for result in doc[u'results']]
        return results

def executeCase((elements, numPlayers, initialCash, numTurns, seed, ops, fops)):
    return OFS(elements=elements, numPlayers=numPlayers, initialCash=initialCash,
               numTurns=numTurns, seed=seed, ops=ops, fops=fops).execute()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program runs an OFS experiment.")
    parser.add_argument('experiment', type=str, nargs='+',
                        help='the experiment to run: masv or bvc')
    parser.add_argument('-d', '--numTurns', type=int, default=24,
                        help='simulation duration (number of turns)')
    parser.add_argument('-p', '--numPlayers', type=int, default=1,
                        help='number of players')
    parser.add_argument('-i', '--initialCash', type=int, default=1200,
                        help='initial cash')
    parser.add_argument('-o', '--ops', type=str, default='d6',
                        help='federate operations model specification')
    parser.add_argument('-f', '--fops', type=str, default='',
                        help='federation operations model specification')
    parser.add_argument('-l', '--logging', type=str, default='error',
                        choices=['debug','info','warning','error'],
                        help='logging level')
    parser.add_argument('-s', '--start', type=int, default=0,
                        help='starting random number seed')
    parser.add_argument('-t', '--stop', type=int, default=10,
                        help='stopping random number seed')
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
    
    if len(args.experiment) == 1 and args.experiment[0] == 'masv':
        executeMASV(args.dbHost, args.dbPort, args.start, args.stop)
    elif len(args.experiment) == 1 and args.experiment[0] == 'bvc':
        executeBVC(args.dbHost, args.dbPort, args.start, args.stop)
    else:
        execute(args.dbHost, args.dbPort, args.start, args.stop,
                [' '.join(args.experiment)],
                args.numPlayers, args.initialCash, args.numTurns,
                args.ops, args.fops)