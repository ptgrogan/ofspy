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

from multiprocessing import Pool
from scoop import futures

import pymongo
from bson.code import Code

import csv
import numpy as np
import re
import matplotlib.pyplot as plt

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

def executeMASV(db, start, stop, compute):
    execute(db, start, stop, enumMASV(), 2, 0, 24, 'd6,a,1', 'x50,25,6,a,1', compute)

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

def executeBVC(db, start, stop, compute):
    execute(db, start, stop, enumBVC(), 2, 0, 24, 'n', 'd6,a,1', compute)

def execute(db, start, stop, cases, numPlayers,
            initialCash, numTurns, ops, fops, compute):
    executions = [(db, [e for e in elements.split(' ') if e != ''],
        numPlayers, initialCash, numTurns, seed, ops, fops)
        for (seed, elements) in itertools.product(range(start, stop), cases)]
    numComplete = 0.0
    logging.info('Executing {} cases with seeds from {} to {} for {} total executions.'
                 .format(len(cases), start, stop, len(executions)))
    if compute == 'serial':
        for result in map(queryCase, executions):
            print result
    elif compute == 'parallel':
        pool = Pool()
        for result in pool.map(queryCase, executions):
            print result
        pool.close()
    elif compute == 'distributed':
        for result in futures.map(queryCase, executions):
            print result

def queryCase((db, elements, numPlayers, initialCash, numTurns, seed, ops, fops)):
    if db is None:
        return executeCase((elements, numPlayers, initialCash,
                            numTurns, seed, ops, fops))
    else:
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

def postProcessBVC(db):
    if db is None:
        logging.error('DB host required for post-processing.')
        return
    # code below based on from https://gist.github.com/RedBeard0531/1886960
    ppMap = Code(
        "function() {" +
        "  emit({elements: this.elements," +
        "        ops: this.ops,"+
        "        fops: this.fops,"+
        "        numTurns: this.numTurns,"+
        "        p1Cost: this.results[0][0],"+
        "        p2Cost: this.results[1][0],"+
        "        totCost: this.results[0][0] + this.results[1][0],"+
        "       },"+
        "       {count: 1,"+
        "        p1Sum: this.results[0][1],"+
        "        p1Min: this.results[0][1],"+
        "        p1Max: this.results[0][1],"+
        "        p1Diff: 0,"+
        "        p2Sum: this.results[1][1],"+
        "        p2Min: this.results[1][1],"+
        "        p2Max: this.results[1][1],"+
        "        p2Diff: 0,"+
        "        totSum: this.results[0][1] + this.results[1][1],"+
        "        totMin: this.results[0][1] + this.results[1][1],"+
        "        totMax: this.results[0][1] + this.results[1][1],"+
        "        totDiff: 0,"+
        "       });"+
               "}")
    ppReduce = Code(
        "function(key, values) {" +
        "  var a = values[0];" +
        "  for (var i = 1; i < values.length; i++) {"+
        "    var b = values[i];"+
        "    var p1Delta = a.p1Sum/a.count - b.p1Sum/b.count;"+
        "    var p2Delta = a.p2Sum/a.count - b.p2Sum/b.count;"+
        "    var totDelta = a.totSum/a.count - b.totSum/b.count;"+
        "    var weight = (a.count * b.count) / (a.count + b.count);"+
        "    a.p1Diff += b.p1Diff + p1Delta*p1Delta*weight;"+
        "    a.p2Diff += b.p2Diff + p2Delta*p2Delta*weight;"+
        "    a.totDiff += b.totDiff + totDelta*totDelta*weight;"+
        "    a.p1Sum += b.p1Sum;"+
        "    a.p2Sum += b.p2Sum;"+
        "    a.totSum += b.totSum;"+
        "    a.count += b.count;"+
        "    a.p1Min = Math.min(a.p1Min, b.p1Min);"+
        "    a.p2Min = Math.min(a.p2Min, b.p2Min);"+
        "    a.totMin = Math.min(a.totMin, b.totMin);"+
        "    a.p1Max = Math.max(a.p1Max, b.p1Max);"+
        "    a.p2Max = Math.max(a.p2Max, b.p2Max);"+
        "    a.totMax = Math.max(a.totMax, b.totMax);"+
        "  }"+
        "  return a;"+
        "}")
    ppFinalize = Code(
        "function(key, value) {" +
        "  value.p1Avg = value.p1Sum / value.count;" +
        "  value.p2Avg = value.p2Sum / value.count;" +
        "  value.totAvg = value.totSum / value.count;" +
        "  value.p1Var = value.p1Diff / value.count;" +
        "  value.p2Var = value.p2Diff / value.count;" +
        "  value.totVar = value.totDiff / value.count;" +
        "  value.p1StdDev = Math.sqrt(value.p1Var);" +
        "  value.p2StdDev = Math.sqrt(value.p2Var);" +
        "  value.totStdDev = Math.sqrt(value.totVar);" +
        "  value.p1StdErr = value.p1StdDev / Math.sqrt(value.count);" +
        "  value.p2StdErr = value.p2StdDev / Math.sqrt(value.count);" +
        "  value.totStdErr = value.totStdDev / Math.sqrt(value.count);" +
        "  return value;"+
        "}")
    db.results.map_reduce(ppMap, ppReduce, 'bvc', finalize=ppFinalize)
    
    id = np.array([])
    elements = np.array([])
    totCost = np.array([])
    p1Cost = np.array([])
    totValueStdErr = np.array([])
    totValueAvg = np.array([])
    pisl = np.array([], dtype=np.bool_)
    oisl = np.array([], dtype=np.bool_)
    osgl = np.array([], dtype=np.bool_)
    counter = 0
    with open('data-bvc.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['id', 'elements', 'ops', 'fops', 'numTurns', 'count',
                         'totCost', 'totAvg', 'totExpVal',
                         'totMin', 'totMax', 'totStdErr',
                         'p1Cost', 'p1Avg', 'p1ExpVal',
                         'p1Min', 'p1Max', 'p1StdErr',
                         'p2Cost', 'p2Avg', 'p2ExpVal',
                         'p2Min', 'p2Max', 'p2StdErr'])
        for doc in db.bvc.find().sort(u'_id.totCost', pymongo.ASCENDING):
            counter += 1
            writer.writerow([counter, doc[u'_id'][u'elements'].encode('ascii','ignore').replace(',','|'),
                             doc[u'_id'][u'ops'].encode('ascii','ignore').replace(',','|'),
                             doc[u'_id'][u'fops'].encode('ascii','ignore').replace(',','|'),
                             doc[u'_id'][u'numTurns'],
                             doc[u'value'][u'count'],
                             doc[u'_id'][u'totCost'],
                             doc[u'value'][u'totAvg'],
                             doc[u'value'][u'totAvg'] - doc[u'_id'][u'totCost'],
                             doc[u'value'][u'totMin'],
                             doc[u'value'][u'totMax'],
                             doc[u'value'][u'totStdErr'],
                             doc[u'_id'][u'p1Cost'],
                             doc[u'value'][u'p1Avg'],
                             doc[u'value'][u'p1Avg'] - doc[u'_id'][u'p1Cost'],
                             doc[u'value'][u'p1Min'],
                             doc[u'value'][u'p1Max'],
                             doc[u'value'][u'p1StdErr'],
                             doc[u'_id'][u'p2Cost'],
                             doc[u'value'][u'p2Avg'],
                             doc[u'value'][u'p2Avg'] - doc[u'_id'][u'p2Cost'],
                             doc[u'value'][u'p2Min'],
                             doc[u'value'][u'p2Max'],
                             doc[u'value'][u'p2StdErr']])
            id = np.append(id, counter)
            elements = np.append(elements, doc[u'_id'][u'elements'].encode('ascii','ignore'))
            totCost = np.append(totCost, doc[u'_id'][u'totCost'])
            p1Cost = np.append(p1Cost, doc[u'_id'][u'p1Cost'])
            totValueStdErr = np.append(totValueStdErr, doc['value'][u'totStdErr'])
            totValueAvg = np.append(totValueAvg, doc['value'][u'totAvg'])
            pisl = np.append(pisl, 'pISL' in doc[u'_id'][u'elements'])
            oisl = np.append(oisl, 'oISL' in doc[u'_id'][u'elements'])
            osgl = np.append(osgl, 'oSGL' in doc[u'_id'][u'elements'])
            
    totExpValue = totValueAvg - totCost
    independent = np.logical_and(oisl==False, osgl==False)
    
    def pareto(id, cost, expValue):
        p_id = np.array([])
        p_cost = np.array([])
        p_value = np.array([])
        for i in range(0,np.size(cost)):
            if np.sum(np.logical_and(cost<=cost[i], expValue>expValue[i])) == 0:
                p_id = np.append(p_id, id[i])
                p_cost = np.append(p_cost, cost[i])
                p_value = np.append(p_value, expValue[i])
        return p_id, p_cost, p_value
    
    def plotTradespaceStep1(c, id, cost, expValue, stdErr):
        plt.errorbar(cost, expValue, yerr=1.96*stdErr,
                     fmt='none',color=c,ecolor=c, alpha=0.3)
    def plotTradespaceStep2(c, id, cost, expValue):
        plt.plot(cost, expValue, ls='', marker='.',
                 mec='none',color=c, alpha=0.3)
    def plotTradespaceStep3(c, id, cost, expValue, P_id):
        p_id, p_cost, p_value = pareto(id, cost, expValue)
        for i in np.intersect1d(P_id, p_id):
            plt.annotate('%0d'%i, xy=(p_cost[p_id==i], p_value[p_id==i]),
                        xytext=(-5,4), textcoords='offset points', size=8, color=c)    
    
    def tradespaceIndependent(label, id, cost, expValue, stdErr, pisl, oisl, osgl):
        plt.clf()
        filters = [np.logical_and.reduce((pisl==False,oisl==False,osgl==False)),
                   np.logical_and.reduce((pisl==True,oisl==False,osgl==False))]
        colors = ['k','b']
        
        for i, f in enumerate(filters):
            plotTradespaceStep1(colors[i], id[f], cost[f], expValue[f], stdErr[f])
        for i, f in enumerate(filters):
            plotTradespaceStep2(colors[i], id[f], cost[f], expValue[f])
        P_id, P_cost, P_value = pareto(id, cost, expValue)
        for i, f in enumerate(filters):
            plotTradespaceStep3(colors[i], id[f], cost[f], expValue[f], P_id)
            
        plt.plot(P_cost, P_value, ls='steps-post--', color=[.3,.3,.3])
            
        plt.xlabel('Initial Cost ($\S$)')
        plt.ylabel('24-turn Expected Net Value ($\S$)')
        plt.xlim([1000, 4000])
        plt.ylim([-2000, 10000])
        plt.legend(['pSGL','pSGL and pISL'],loc='upper left')
        plt.grid()
        plt.gcf().set_size_inches(6.5, 3.5)
        plt.savefig('ts-'+label+'.png', bbox_inches='tight', dpi=300)
            
    def tradespaceCentralized(label, id, cost, expValue, stdErr, pisl, oisl, osgl):
        plt.clf()
        filters = [np.logical_and.reduce((pisl==False,oisl==False,osgl==False)),
                   np.logical_and.reduce((pisl==True,oisl==False,osgl==False)),
                   np.logical_and.reduce((pisl==False,oisl==True,osgl==False)),
                   np.logical_and.reduce((pisl==False,oisl==False,osgl==True)),
                   np.logical_and.reduce((pisl==True,oisl==False,osgl==True)),
                   np.logical_and.reduce((pisl==False,oisl==True,osgl==True))]
        colors = ['k','b','g','r','m','y']
        
        for i, f in enumerate(filters):
            plotTradespaceStep1(colors[i], id[f], cost[f], expValue[f], stdErr[f])
        for i, f in enumerate(filters):
            plotTradespaceStep2(colors[i], id[f], cost[f], expValue[f])
        P_id, P_cost, P_value = pareto(id, cost, expValue)
        for i, f in enumerate(filters):
            plotTradespaceStep3(colors[i], id[f], cost[f], expValue[f], P_id)
            
        plt.plot(P_cost, P_value, ls='steps-post--', color=[.3,.3,.3])
            
        plt.xlabel('Initial Cost ($\S$)')
        plt.ylabel('24-turn Expected Net Value ($\S$)')
        plt.xlim([1000, 4000])
        plt.ylim([-2000, 10000])
        plt.legend(['pSGL', 'pSGL and pISL', 'pSGL and oISL',
                    'oSGL', 'oSGL and pISL', 'oSGL and oISL'],loc='upper left')
        plt.grid()
        plt.gcf().set_size_inches(6.5, 3.5)
        plt.savefig('ts-'+label+'.png', bbox_inches='tight', dpi=300)
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    if np.size(id[independent] > 0):
        tradespaceIndependent('bvc-i', id[independent], 
            totCost[independent]/2, 
            totExpValue[independent]/2,
            totValueStdErr[independent]/2, 
            pisl[independent], 
            oisl[independent], 
            osgl[independent])
    if np.size(id) > 0:
        tradespaceCentralized('bvc-c', id, 
            totCost/2, totExpValue/2,
            totValueStdErr/2,  pisl, oisl, osgl)
    
    i_id, i_cost, i_value = pareto(id[independent], 
            totCost[independent]/2, 
            totExpValue[independent]/2)
    c_id, c_cost, c_value = pareto(id, totCost/2, totExpValue/2)
            
    x_value = np.array([])
    for i in c_id:
        m = re.search('^((1\.[^\s]*\s*)+) (?:(2\.[^\s]*\s*)+) '
                      + '(?:(1\.[^\s]*\s*)*) (?:(2\.[^\s]*\s*)*)$',
                      elements[id==i].tostring())
        if m:
            query = m.group(1).replace('oSGL','pSGL').replace('oISL','pISL')
            for element in elements[independent]:
                n = re.search('^((1\.[^\s]*\s*)+) (?:(2\.[^\s]*\s*)+) '
                              + '(?:(1\.[^\s]*\s*)*) (?:(2\.[^\s]*\s*)*)$',
                              element)
                if n and query == n.group(1):
                    # correct value for differences in initial costs
                    x_value = np.append(x_value, totExpValue[elements==element]/2
                                        + p1Cost[elements==element] - c_cost[i==c_id])
    
    x = np.linspace(max(np.amin(i_cost), np.amin(c_cost)), 
            max(np.amax(i_cost), np.amax(c_cost)),100)
    v_ub = np.array([])
    v_i = np.array([])
    v_lb = np.array([])
    for i in x:
        v_ub = np.append(v_ub, np.max(c_value[c_cost<=i])
                         if np.count_nonzero(c_cost<=i) > 0
                         else c_value[0]);
        v_i = np.append(v_i, np.max(i_value[i_cost<=i])
                        if np.count_nonzero(i_cost<=i) > 0
                        else i_value[0]);
        v_lb = np.append(v_lb, x_value[np.argmax(c_value[c_cost<=i])]
                         if np.count_nonzero(c_cost<=i) > 0
                         else x_value[0]);
    
    plt.clf()
    plt.fill_between(x, v_ub, v_i, color='none', hatch='/',
                     edgecolor=[.3,.3,.3,.5], linewidth=0.0)
    plt.fill_between(x, v_i, v_lb, color='none', hatch='\\',
                     edgecolor=[1,.3,.3,.5], linewidth=0.0)
    plt.plot(i_cost, i_value, ls='steps-post-', color='k')
    plt.plot(c_cost, c_value, ls='steps-post--', color='k')
    plt.plot(c_cost, x_value, ls='steps-post--', color='r')
    
    plt.annotate('Upside Potential of FSS Success', xy=(2400, 5000), 
            xycoords='data', textcoords='data', size=8, color='k')
    plt.annotate('Downside Risk of FSS Failure', xy=(2250, 1600), xytext=(2500,600), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='r'), 
            xycoords='data', textcoords='data', size=8, color='r')
    
    plt.xlabel('Initial Cost ($\S$)')
    plt.ylabel('24-turn Expected Net Value ($\S$)')
    plt.xlim([1000, 4000])
    plt.ylim([-2000, 10000])
    plt.legend(['Independent Pareto Frontier ($V_i$)','Centralized Pareto Frontier, FSS Success ($V_c$)','Centralized Pareto Frontier, FSS Failure  ($V_x$)'],loc='upper left')
    plt.grid()
    plt.gcf().set_size_inches(6.5, 3.5)
    plt.savefig('tsc-bvc.png', bbox_inches='tight', dpi=300)
    
    initialCost = 2000
    
    for id in i_id:
        i = np.where(i_id==id)[0][0]
        if (i + 1 == np.size(i_id) \
                and i_cost[i] <= initialCost) \
                or (i + 1 < np.size(i_id) \
                and i_cost[i] <= initialCost \
                and i_cost[i+1] > initialCost):
            print '===independent case==='
            print 'cost: ' + '%.0f'%i_cost[i] + ', value: ' + '%.0f'%i_value[i]
            print 'id ' + '%0d'%id + ': ' + elements[id==id].tostring()
            
    for id in c_id:
        i = np.where(c_id==id)[0][0]
        if (i + 1 == np.size(c_id) \
                and c_cost[i] <= initialCost) \
                or (i + 1 < np.size(c_id) \
                    and c_cost[i] <= initialCost \
                    and c_cost[i+1] > initialCost):
            print '===centralized (successful) case==='
            print 'cost: ' + '%.0f'%c_cost[i] + ', value: ' + '%.0f'%c_value[i]
            print 'id ' + '%0d'%id + ': ' + elements[id==id].tostring()
            
    for id in c_id:
        i = np.where(c_id==id)[0][0]
        if (i + 1 == np.size(c_id) \
                and c_cost[i] <= initialCost) \
                or (i + 1 < np.size(c_id) \
                and c_cost[i] <= initialCost \
                and c_cost[i+1] > initialCost):
            print '===centralized (failed) case==='
            print 'cost: ' + '%.0f'%c_cost[i] + ', value: ' + '%.0f'%x_value[i]
            print 'id ' + '%0d'%id + ': ' + elements[id==id].tostring()
    

def postProcessMASV(db):
    if db is None:
        logging.error('DB host required for post-processing.')
        return
    
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
    parser.add_argument('-c', '--compute', type=str, default='parallel',
                        choices=['serial','parallel','distributed'],
                        help='computing mode')
    parser.add_argument('--postProcess', action='store_true',
                        help='post-process results')
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
    
    db = None
    if args.dbHost is not None:
        db = pymongo.MongoClient(args.dbHost, args.dbPort).ofs
    
    if len(args.experiment) == 1 and args.experiment[0] == 'masv':
        executeMASV(db, args.start, args.stop, args.compute)
    elif len(args.experiment) == 1 and args.experiment[0] == 'bvc':
        if args.postProcess:
            postProcessBVC(db)
        else:
            executeBVC(db, args.start, args.stop, args.compute)
    else:
        execute(db, args.start, args.stop, [' '.join(args.experiment)],
                args.numPlayers, args.initialCash, args.numTurns,
                args.ops, args.fops, args.compute)