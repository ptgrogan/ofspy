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
from bson.code import Code
import csv
import itertools
import logging
import matplotlib.pyplot as plt
import numpy as np
import pymongo
import re
import sys,os
# add ofspy to system path
sys.path.append(os.path.abspath('..'))

def mapReduce(db, dbName, query=None):
    """
    Performs a map-reduce operation on a database.
    @param db: the database
    @type db: L{Database}
    @param dbName: the database collection name
    @type dbName: L{str}
    """
    # code below based on from https://gist.github.com/RedBeard0531/1886960
    # to compute standard error in a map-reduce function
    # this function computes separate results for player 1, player 2,
    # and total value as p1, p2, tot
    # TODO: generalize to more than two players
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
    if query is None:
        db[dbName].map_reduce(ppMap, ppReduce, '{}_pp'.format(dbName),
                              finalize=ppFinalize)
    else:
        db[dbName].map_reduce(ppMap, ppReduce, '{}_pp'.format(dbName),
                              query=query, finalize=ppFinalize)

def processData(db, dbName, query=None):
    """
    Processes data for a database and returns parsed results.
    @param db: the database
    @type db: L{Database}
    @param dbName: the database collection name
    @type dbName: L{str}
    @param query: the filter query
    @type query: L{dict}
    @return: L{tuple}
    """
    id = np.array([])
    elements = np.array([])
    p1Cost = np.array([])
    p2Cost = np.array([])
    totCost = np.array([])
    p1ValueStdErr = np.array([])
    p2ValueStdErr = np.array([])
    totValueStdErr = np.array([])
    p1ValueAvg = np.array([])
    p2ValueAvg = np.array([])
    totValueAvg = np.array([])
    pisl = np.array([], dtype=np.bool_) # boolean: does this design have pISL?
    oisl = np.array([], dtype=np.bool_) # boolean: does this design have oISL?
    osgl = np.array([], dtype=np.bool_) # boolean: does this desitn have oSGL?
    counter = 0
    with open('data-{}.csv'.format(dbName),'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['id', 'elements', 'ops', 'fops', 'numTurns', 'count',
                         'totCost', 'totAvg', 'totExpVal',
                         'totMin', 'totMax', 'totStdErr',
                         'p1Cost', 'p1Avg', 'p1ExpVal',
                         'p1Min', 'p1Max', 'p1StdErr',
                         'p2Cost', 'p2Avg', 'p2ExpVal',
                         'p2Min', 'p2Max', 'p2StdErr'])
        for doc in db['{}_pp'.format(dbName)].find(query).sort(
            [[u'_id.totCost', pymongo.ASCENDING], [u'_id.elements', pymongo.ASCENDING]]):
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
            p1Cost = np.append(p1Cost, doc[u'_id'][u'p1Cost'])
            p2Cost = np.append(p2Cost, doc[u'_id'][u'p2Cost'])
            totCost = np.append(totCost, doc[u'_id'][u'totCost'])
            p1ValueStdErr = np.append(p1ValueStdErr, doc['value'][u'p1StdErr'])
            p2ValueStdErr = np.append(p2ValueStdErr, doc['value'][u'p2StdErr'])
            totValueStdErr = np.append(totValueStdErr, doc['value'][u'totStdErr'])
            p1ValueAvg = np.append(p1ValueAvg, doc['value'][u'p1Avg'])
            p2ValueAvg = np.append(p2ValueAvg, doc['value'][u'p2Avg'])
            totValueAvg = np.append(totValueAvg, doc['value'][u'totAvg'])
            # determine tech option based on player 1's design
            m = re.search('((1\.[^\s]*\s*)+) (?:(2\.[^\s]*\s*)+)',
                          doc[u'_id'][u'elements'])
            if m:
                pisl = np.append(pisl, 'pISL' in m.group(1))
                oisl = np.append(oisl, 'oISL' in m.group(1))
                osgl = np.append(osgl, 'oSGL' in m.group(1))
            else:
                pisl = np.append(pisl, 'pISL' in doc[u'_id'][u'elements'])
                oisl = np.append(oisl, 'oISL' in doc[u'_id'][u'elements'])
                osgl = np.append(osgl, 'oSGL' in doc[u'_id'][u'elements'])
    p1ExpValue = p1ValueAvg - p1Cost
    p2ExpValue = p2ValueAvg - p2Cost
    totExpValue = totValueAvg - totCost
    independent = np.logical_and(oisl==False, osgl==False)
    return (id, elements, p1Cost, p2Cost, totCost,
            p1ValueStdErr, p2ValueStdErr, totValueStdErr, 
            p1ValueAvg, p2ValueAvg, totValueAvg,
            p1ExpValue, p2ExpValue, totExpValue, 
            pisl, oisl, osgl, independent)
    
def pareto(id, cost, expValue):
    """
    Gets the set of non-dominated points.
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @return: L{tuple}
    """
    p_id = np.array([])
    p_cost = np.array([])
    p_value = np.array([])
    for i in range(0,np.size(cost)):
        # check if i is non-dominated
        if np.sum(np.logical_and(cost<=cost[i], expValue>expValue[i])) == 0:
            p_id = np.append(p_id, id[i])
            p_cost = np.append(p_cost, cost[i])
            p_value = np.append(p_value, expValue[i])
    return p_id, p_cost, p_value

def plotTradespaceStep1(c, id, cost, expValue, stdErr):
    """
    Plots the error bars for a tradespace of designs.
    @param c: the color
    @type c: L{str}
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @param stdErr: the design standard errors
    @type stdErr: L{ndarray}
    """
    plt.errorbar(cost, expValue, yerr=1.96*stdErr,
                 fmt='none',color=c,ecolor=c, alpha=0.3)
def plotTradespaceStep2(c, id, cost, expValue):
    """
    Plots the points for a tradespace of designs.
    @param c: the color
    @type c: L{str}
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @param stdErr: the design standard errors
    @type stdErr: L{ndarray}
    """
    plt.plot(cost, expValue, ls='', marker='.',
             mec='none',color=c, alpha=0.3)
def plotTradespaceStep3(c, id, cost, expValue, P_id):
    """
    Plots the Pareto frontier for a tradespace of points.
    @param c: the color
    @type c: L{str}
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @param P_id: the ids of Pareto-optimal designs
    @type P_id: L{ndarray}
    """
    p_id, p_cost, p_value = pareto(id, cost, expValue)
    for i in np.intersect1d(P_id, p_id):
        plt.annotate('%0d'%i, xy=(p_cost[p_id==i], p_value[p_id==i]),
                    xytext=(-5,4), textcoords='offset points', size=8, color=c)    

def tradespaceIndependent(label, id, cost, expValue,
                          stdErr, pisl, oisl, osgl,
                          xlim=[1000, 4000], ylim=[-1000, 10000]):
    """
    Creates a tradespace plot for independent designs.
    @param label: the plot label
    @type label: L{str}
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @param stdErr: the design standard errors
    @type stdErr: L{ndarray}
    @param pisl: mask for designs containing pISL modules
    @type pisl: L{ndarray}
    @param oisl: mask for designs containing oISL modules
    @type oisl: L{ndarray}
    @param osgl: mask for designs containing oSGL modules
    @type osgl: L{ndarray}
    """
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
        
    plt.plot(np.append(P_cost,np.max(cost)),
             np.append(P_value,np.max(P_value)),
             ls='steps-post--', color=[.3,.3,.3])
        
    plt.xlabel('Initial Cost ($\S$)')
    plt.ylabel('24-turn Expected Net Value ($\S$)')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend(['pSGL','pSGL and pISL'],loc='upper left')
    plt.grid()
    plt.gcf().set_size_inches(6.5, 3.5)
    plt.savefig('ts-'+label+'.png', bbox_inches='tight', dpi=300)
        
def tradespaceCentralized(label, id, cost, expValue,
                          stdErr, pisl, oisl, osgl,
                          xlim=[1000, 4000], ylim=[-1000, 10000]):
    """
    Creates a tradespace plot for centralized designs.
    @param label: the plot label
    @type label: L{str}
    @param id: the design ids
    @type id: L{ndarray}
    @param cost: the design costs
    @type cost: L{ndarray}
    @param expValue: the design expected values
    @type expValue: L{ndarray}
    @param stdErr: the design standard errors
    @type stdErr: L{ndarray}
    @param pisl: mask for designs containing pISL modules
    @type pisl: L{ndarray}
    @param oisl: mask for designs containing oISL modules
    @type oisl: L{ndarray}
    @param osgl: mask for designs containing oSGL modules
    @type osgl: L{ndarray}
    """
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
        
    plt.plot(np.append(P_cost,np.max(cost)),
             np.append(P_value,np.max(P_value)),
             ls='steps-post--', color=[.3,.3,.3])
        
    plt.xlabel('Initial Cost ($\S$)')
    plt.ylabel('24-turn Expected Net Value ($\S$)')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend(['pSGL', 'pSGL and pISL', 'pSGL and oISL',
                'oSGL', 'oSGL and pISL', 'oSGL and oISL'],loc='upper left')
    plt.grid()
    plt.gcf().set_size_inches(6.5, 3.5)
    plt.savefig('ts-'+label+'.png', bbox_inches='tight', dpi=300)

def postProcessMASV(db, suffix=''):
    """
    Performs post-processing for the multi-actor system value experiment.
    @param db: the database
    @type db: L{Database}
    @param suffix: the experiment suffix
    @type suffix: L{str}
    """
    mapReduce(db, 'masv{}'.format(suffix))
    (id, elements, p1Cost, p2Cost, totCost,
     p1ValueStdErr, p2ValueStdErr, totValueStdErr, 
     p1ValueAvg, p2ValueAvg, totValueAvg,
     p1ExpValue, p2ExpValue, totExpValue, 
     pisl, oisl, osgl, independent) = processData(db, 'masv{}'.format(suffix))
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    if np.size(id[independent] > 0):
        tradespaceIndependent('masv-i{}'.format(suffix), id[independent], 
            p1Cost[independent], 
            p1ExpValue[independent],
            p1ValueStdErr[independent], 
            pisl[independent], 
            oisl[independent], 
            osgl[independent])
    if np.size(id) > 0:
        tradespaceCentralized('masv-c{}'.format(suffix), id, 
            p1Cost, p1ExpValue, p1ValueStdErr,
            pisl, oisl, osgl)

def postProcessBVC(db, suffix=''):
    """
    Performs post-processing for the bounding value of collaboration experiment.
    @param db: the database
    @type db: L{Database}
    @param suffix: the experiment suffix
    @type suffix: L{str}
    """
    mapReduce(db, 'bvc{}'.format(suffix))
    (id, elements, p1Cost, p2Cost, totCost,
     p1ValueStdErr, p2ValueStdErr, totValueStdErr, 
     p1ValueAvg, p2ValueAvg, totValueAvg,
     p1ExpValue, p2ExpValue, totExpValue, 
     pisl, oisl, osgl, independent) = processData(db, 'bvc{}'.format(suffix))
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    if np.size(id[independent] > 0):
        tradespaceIndependent('bvc-i{}'.format(suffix), id[independent], 
            totCost[independent]/2, 
            totExpValue[independent]/2,
            totValueStdErr[independent]/2, 
            pisl[independent], 
            oisl[independent], 
            osgl[independent],
            ylim=[-500, 4000])
    if np.size(id) > 0:
        tradespaceCentralized('bvc-c{}'.format(suffix), id, 
            totCost/2, totExpValue/2, totValueStdErr/2,
            pisl, oisl, osgl,
            ylim=[-500, 4000] if suffix == '3' else [-500, 10000])

def postPostProcessBVC(db):
    """
    Performs post-post-processing for all variants of the
    bounding value of collaboration experiment.
    @param db: the database
    @type db: L{Database}
    """
    (id_1, elements_1, p1Cost_1, p2Cost_1, totCost_1,
     p1ValueStdErr_1, p2ValueStdErr_1, totValueStdErr_1, 
     p1ValueAvg_1, p2ValueAvg_1, totValueAvg_1,
     p1ExpValue_1, p2ExpValue_1, totExpValue_1, 
     pisl_1, oisl_1, osgl_1, independent_1) = processData(db, 'bvc')
    (id_2, elements_2, p1Cost_2, p2Cost_2, totCost_2,
     p1ValueStdErr_2, p2ValueStdErr_2, totValueStdErr_2, 
     p1ValueAvg_2, p2ValueAvg_2, totValueAvg_2,
     p1ExpValue_2, p2ExpValue_2, totExpValue_2, 
     pisl_2, oisl_2, osgl_2, independent_2) = processData(db, 'bvc2')
    (id_3, elements_3, p1Cost_3, p2Cost_3, totCost_3,
     p1ValueStdErr_3, p2ValueStdErr_3, totValueStdErr_3, 
     p1ValueAvg_3, p2ValueAvg_3, totValueAvg_3,
     p1ExpValue_3, p2ExpValue_3, totExpValue_3, 
     pisl_3, oisl_3, osgl_3, independent_3) = processData(db, 'bvc3')
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    
    # plot transformation tradespaces at varying levels of estimated cooperation
    # for centralized and federated strategies
    """
    for p in range(5,100,5):
        tradespaceCentralized('bvc-uc{}'.format(p), id_1, 
            (totCost_1*float(p)/100 + totCost_3*(1-float(p)/100))/2,
            (totExpValue_1*float(p)/100 + totExpValue_3*(1-float(p)/100))/2,
            (totValueStdErr_1*float(p)/100 + totValueStdErr_3*(1-float(p)/100))/2,
            pisl_1, oisl_1, osgl_1,
            ylim=[-500, 10000])
        tradespaceCentralized('bvc-uf{}'.format(p), id_2, 
            (totCost_2*float(p)/100 + totCost_3*(1-float(p)/100))/2,
            (totExpValue_2*float(p)/100 + totExpValue_3*(1-float(p)/100))/2,
            (totValueStdErr_2*float(p)/100 + totValueStdErr_3*(1-float(p)/100))/2,
            pisl_2, oisl_2, osgl_2,
            ylim=[-500, 10000])
    """

    # set of pareto-optimal points
    i_id, i_cost, i_value = pareto(id_3, totCost_3/2, totExpValue_3/2)
    f_id, f_cost, f_value = pareto(id_2, totCost_2/2, totExpValue_2/2)
    c_id, c_cost, c_value = pareto(id_1, totCost_1/2, totExpValue_1/2)
    
    # evaluate centralized pareto-optimal points under independent strategy
    x_value = np.array([])
    for i in c_id:
        x_value = np.append(x_value, totExpValue_3[id_3==i]/2)
    
    # evaluate federated pareto-optimal points under independent strategy
    xf_value = np.array([])
    for i in f_id:
        xf_value = np.append(xf_value, totExpValue_3[id_3==i]/2)
    
    # compute errors
    i_err = np.array([totValueStdErr_3[np.where(id_3==i)]/2 for i in i_id])
    c_err = np.array([totValueStdErr_1[np.where(id_1==i)]/2 for i in c_id])
    xc_err = np.array([totValueStdErr_3[np.where(id_3==i)]/2 for i in c_id])
    f_err = np.array([totValueStdErr_2[np.where(id_2==i)]/2 for i in f_id])
    xf_err = np.array([totValueStdErr_3[np.where(id_3==i)]/2 for i in f_id])
    
    # evaluate lower and upper bounds and independent value at sampled points
    x = np.linspace(np.min(totCost_1/2), np.max(totCost_1/2),1000)
    v_ub = np.array([])
    v_i = np.array([])
    v_lb = np.array([])
    f_ub = np.array([])
    f_lb = np.array([])
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
        f_ub = np.append(f_ub, np.max(f_value[f_cost<=i])
                         if np.count_nonzero(f_cost<=i) > 0
                         else f_value[0]);
        f_lb = np.append(f_lb, xf_value[np.argmax(f_value[f_cost<=i])]
                         if np.count_nonzero(f_cost<=i) > 0
                         else xf_value[0]);
    
    # generate risk-reward tradespace for centralized strategy
    plt.clf()
    plt.fill_between(x, v_ub, v_i, color='none', hatch='/',
                     edgecolor=[.3,.3,1,.5], linewidth=0.0)
    plt.fill_between(x, v_i, v_lb, color='none', hatch='\\',
                     edgecolor=[1,.3,.3,.5], linewidth=0.0)
    plt.plot(np.append(i_cost, np.max(totCost_3/2)),
             np.append(i_value, np.max(i_value)),
             ls='steps-post-', color='k')
    plt.plot(np.append(c_cost, np.max(totCost_1/2)),
             np.append(c_value, np.max(c_value)),
             ls='steps-post--', color='b')
    plt.plot(np.append(c_cost, np.max(totCost_1/2)),
             np.append(x_value, np.max(x_value)),
             ls='steps-post:', color='r')
    # plot design points with labels
    plt.errorbar(i_cost, i_value, yerr=1.96*i_err,
                 fmt='none',color='k',ecolor='k', alpha=0.3)
    plt.errorbar(c_cost, c_value, yerr=1.96*c_err,
                 fmt='none',color='b',ecolor='b', alpha=0.3)
    plt.errorbar(c_cost, x_value, yerr=1.96*xc_err,
                 fmt='none',color='r',ecolor='r', alpha=0.3)
    for i in i_id:
        plt.annotate('%0d'%i, xy=(i_cost[i_id==i], i_value[i_id==i]),
                    xytext=(-8,2), textcoords='offset points', size=6, color='k')
    for i in c_id:
        plt.annotate('%0d'%i, xy=(c_cost[c_id==i], c_value[c_id==i]),
                    xytext=(-8,2), textcoords='offset points', size=6, color='b')
        plt.annotate('%0d'%i, xy=(c_cost[c_id==i], x_value[c_id==i]),
                    xytext=(2,-8), textcoords='offset points', size=6, color='r')
    plt.plot(np.append(i_cost, np.max(totCost_3/2)),
             np.append(i_value, np.max(i_value)),
             ls='steps-post-', color='k') # repeated to mask red color
    plt.annotate('Upside Potential of Centralized Strategy', xy=(2100, 4000), xytext=(1100, 6100), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='b'), 
            xycoords='data', textcoords='data', size=8, color='b')
    plt.annotate('Upside Potential of any Federated Strategy', xy=(2450, 4300), 
            xycoords='data', textcoords='data', size=8, color='k')
    plt.annotate('', xy=(2400, 3300), xytext=(2400, 5500),
            arrowprops=dict(arrowstyle='<->',connectionstyle='arc3',ec='k'), 
            xycoords='data', textcoords='data', size=8, color='k')
    plt.annotate('Downside Risk of Centralized Strategy', xy=(2550, 2000), xytext=(2750,600), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='r'), 
            xycoords='data', textcoords='data', size=8, color='r')
    plt.xlabel('Initial Cost ($\S$)')
    plt.ylabel('24-turn Expected Net Value ($\S$)')
    plt.xlim([1000, 4000])
    plt.ylim([-1000, 10000])
    plt.legend([r'Independent $(\mathcal{V}_i^{I,I} \approx \mathcal{V}_i^{I,C})$',
                r'Centralized, Successful $(\mathcal{V}_i^{C,C})$',
                r'Centralized, Failed ($\mathcal{V}_i^{C,I})$'],
        loc='upper left',
        handlelength=5)
    plt.gcf().set_size_inches(7, 3.5)
    plt.savefig('ts-bvc.png', bbox_inches='tight', dpi=300)
        
    # generate risk-reward tradespace for federated strategy
    plt.clf()
    plt.fill_between(x, v_ub, v_i, color='none', hatch='/',
                     edgecolor=[.3,.3,1,.5], linewidth=0.0, alpha=.3)
    plt.fill_between(x, v_i, v_lb, color='none', hatch='\\',
                     edgecolor=[1,.3,.3,.5], linewidth=0.0, alpha=.3)
    plt.fill_between(x, f_ub, v_i, color='none', hatch='\\\\',
                     edgecolor=[.3,.3,1,.5], linewidth=0.0)
    plt.fill_between(x, v_i, f_lb, color='none', hatch='//',
                     edgecolor=[1,.3,.3,.5], linewidth=0.0)
    plt.plot(np.append(i_cost, np.max(totCost_3/2)),
             np.append(i_value, np.max(i_value)),
             ls='steps-post-', color='k')
    plt.plot(np.append(c_cost, np.max(totCost_1/2)),
             np.append(c_value, np.max(c_value)),
             ls='steps-post--', color='b', alpha=.3)
    plt.plot(np.append(c_cost, np.max(totCost_1/2)),
             np.append(x_value, np.max(x_value)),
             ls='steps-post:', color='r', alpha=.3)
    plt.plot(np.append(f_cost, np.max(totCost_2/2)),
             np.append(f_value, np.max(f_value)),
             ls='steps-post--', color='b')
    plt.plot(np.append(f_cost, np.max(totCost_2/2)),
             np.append(xf_value, np.max(xf_value)),
             ls='steps-post:', color='r')
    plt.plot(np.append(i_cost, np.max(totCost_3/2)),
             np.append(i_value, np.max(i_value)),
             ls='steps-post-', color='k') # repeated to mask red color
    # plot design points with labels
    plt.errorbar(i_cost, i_value, yerr=1.96*i_err,
                 fmt='none',color='k',ecolor='k', alpha=0.3)
    plt.errorbar(f_cost, f_value, yerr=1.96*f_err,
                 fmt='none',color='b',ecolor='b', alpha=0.3)
    plt.errorbar(f_cost, xf_value, yerr=1.96*xf_err,
                 fmt='none',color='r',ecolor='r', alpha=0.3)
    for i in i_id:
        plt.annotate('%0d'%i, xy=(i_cost[i_id==i], i_value[i_id==i]),
                    xytext=(-8,2), textcoords='offset points', size=6, color='k')
    for i in f_id:
        plt.annotate('%0d'%i, xy=(f_cost[f_id==i], f_value[f_id==i]),
                    xytext=(-8,2), textcoords='offset points', size=6, color='b')
        plt.annotate('%0d'%i, xy=(f_cost[f_id==i], xf_value[f_id==i]),
                    xytext=(2,-8), textcoords='offset points', size=6, color='r')
    plt.xlabel('Initial Cost ($\S$)')
    plt.ylabel('24-turn Expected Net Value ($\S$)')
    plt.xlim([1000, 4000])
    plt.ylim([-1000, 10000])
    plt.legend([r'Independent $(\mathcal{V}_i^{I,I}\approx\mathcal{V}_i^{I,C}\approx\mathcal{V}_i^{I,F})$',
                r'Centralized, Successful $(\mathcal{V}_i^{C,C})$',
                r'Centralized, Failed $(\mathcal{V}_i^{C,I}\approx\mathcal{V}_i^{C,F})$',
                r'Federated, Successful $(\mathcal{V}_i^{F,F})$',
                r'Federated, Failed $(\mathcal{V}_i^{F,I}\approx\mathcal{V}_i^{F,C})$'],
        loc='upper left',
        handlelength=5)
    plt.gcf().set_size_inches(7, 3.5)
    plt.savefig('ts-bvc-fed.png', bbox_inches='tight', dpi=300)
    
    # hard-code initial cost of interest for case study
    initialCost = 2000
    
    plt.clf()
    
    p = np.linspace(0,1,100)
    pi_value = np.array([])
    pc_value = np.array([])
    pf_value = np.array([])
    pc2_value = np.array([])
    pf2_value = np.array([])
    pf3_value = np.array([])
    for p_i in p:
        pi_value = np.append(pi_value, np.max([
            totExpValue_3[np.where(id_3==i)]/2
            for i in id_3[np.where(totCost_3/2<=initialCost)]]))
        pc_value = np.append(pc_value, np.max([
            totExpValue_3[np.where(id_3==i)]/2 * (1-p_i)
            + totExpValue_1[np.where(id_1==i)]/2 * p_i
            for i in id_1[np.where(totCost_1/2<=initialCost)]]))
        pf_value = np.append(pf_value, np.max([
            totExpValue_3[np.where(id_3==i)]/2 * (1-p_i)
            + totExpValue_2[np.where(id_2==i)]/2 * p_i
            for i in id_2[np.where(totCost_2/2<=initialCost)]]))
        pc2_value = np.append(pc2_value, 
            totExpValue_3[np.where(id_3==53)]/2 * (1-p_i)
            + totExpValue_1[np.where(id_3==53)]/2 * p_i)
        pf2_value = np.append(pf2_value, 
            totExpValue_3[np.where(id_2==61)]/2 * (1-p_i)
            + totExpValue_2[np.where(id_2==61)]/2 * p_i)
        pf3_value = np.append(pf3_value, 
            totExpValue_3[np.where(id_2==41)]/2 * (1-p_i)
            + totExpValue_2[np.where(id_2==41)]/2 * p_i)
    plt.plot(p,pi_value,'-k',p,pc_value,'--k',p,pf_value,':k')
    plt.plot(p[p<.25],pc2_value[p<.25], ls='--', color=[.3,.3,.3,.3])
    plt.plot(p[p<.87],pf2_value[p<.87], ls=':', color=[.3,.3,.3,.3])
    plt.plot(p[np.logical_or(p<.45,p>.87)],pf3_value[np.logical_or(p<.45,p>.87)], ls=':', color=[.3,.3,.3,.3])
    plt.legend([r'Independent $(\Upsilon_i)$', r'Centralized $(\Upsilon_i^C)$',r'Federated $(\Upsilon_i^F)$'],
        loc='upper left', handlelength=5)
    plt.xlabel('Probability of Cooperation $(P_j(c))$')
    plt.ylabel(r'24-turn Expected Net Value $(\S)$')
    plt.ylim([0,4000])
    plt.annotate(r'$\pi_j^C(d_{53})$', xy=(.25, 1800), xytext=(.25, 1100), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='k'), 
            xycoords='data', textcoords='data', ha='center', size=8, color='k')
    plt.annotate(r'$\pi_j^F(d_{61})$', xy=(.56, 1800), xytext=(.56, 800), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='k'), 
            xycoords='data', textcoords='data', ha='center', size=8, color='k')
    plt.annotate(r'$\pi_j^F(d_{41})$', xy=(.45, 1800), xytext=(.45, 1100), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='k'), 
            xycoords='data', textcoords='data', ha='center', size=8, color='k')
    plt.annotate(r'$\pi_j^F(d_{61},d_{41})$', xy=(.87, 2600), xytext=(.87, 1100), 
            arrowprops=dict(arrowstyle='->',connectionstyle='arc3',ec='k'), 
            xycoords='data', textcoords='data', ha='center', size=8, color='k')
    ax2 = plt.gca().twinx()
    ax2.set_ylim([0,4000])
    ax2.set_yticks([pf2_value[0],pc2_value[0],pi_value[0],pf_value[-1],pc_value[-1]])
    ax2.set_yticklabels([r'$\mathcal{V}_i^{F,I}$',r'$\mathcal{V}_i^{C,I}$',
                         r'$\mathcal{V}_i^{I,I}$',r'$\mathcal{V}_i^{F,F}$',
                         r'$\mathcal{V}_i^{C,C}$'])
    plt.gcf().set_size_inches(3.5, 3)
    plt.savefig('ts-bvc-prob.png', bbox_inches='tight', dpi=300)
    
    
    
    # find optimal design under independent strategy
    for j in i_id:
        i = np.where(i_id==j)[0][0]
        if (i + 1 == np.size(i_id) \
                and i_cost[i] <= initialCost) \
                or (i + 1 < np.size(i_id) \
                and i_cost[i] <= initialCost \
                and i_cost[i+1] > initialCost):
            print '===independent case==='
            print 'cost: ' + '%.0f'%i_cost[i] + ', value: ' + '%.0f'%i_value[i]
            print 'id ' + '%0d'%j + ': ' + elements_3[id_3==j].tostring()
    
    # find optimal design under centralized strategy
    for j in c_id:
        i = np.where(c_id==j)[0][0]
        if (i + 1 == np.size(c_id) \
                and c_cost[i] <= initialCost) \
                or (i + 1 < np.size(c_id) \
                    and c_cost[i] <= initialCost \
                    and c_cost[i+1] > initialCost):
            print '===centralized (successful) case==='
            print 'cost: ' + '%.0f'%c_cost[i] + ', value: ' + '%.0f'%c_value[i]
            print 'id ' + '%0d'%j + ': ' + elements_1[id_1==j].tostring()
            
    # find optimal centralized design, evaluated under independent strategy
    for j in c_id:
        i = np.where(c_id==j)[0][0]
        if (i + 1 == np.size(c_id) \
                and c_cost[i] <= initialCost) \
                or (i + 1 < np.size(c_id) \
                and c_cost[i] <= initialCost \
                and c_cost[i+1] > initialCost):
            print '===centralized (failed) case==='
            print 'cost: ' + '%.0f'%c_cost[i] + ', value: ' + '%.0f'%x_value[i]
            print 'id ' + '%0d'%j + ': ' + elements_3[id_3==j].tostring()
            
    # find optimal design under federated strategy
    for j in f_id:
        i = np.where(f_id==j)[0][0]
        if (i + 1 == np.size(f_id) \
                and f_cost[i] <= initialCost) \
                or (i + 1 < np.size(f_id) \
                    and f_cost[i] <= initialCost \
                    and f_cost[i+1] > initialCost):
            print '===federated (successful) case==='
            print 'cost: ' + '%.0f'%f_cost[i] + ', value: ' + '%.0f'%f_value[i]
            print 'id ' + '%0d'%j + ': ' + elements_2[id_2==j].tostring()
            
    # find optimal federated design, evaluated under independent strategy
    for j in f_id:
        i = np.where(f_id==j)[0][0]
        if (i + 1 == np.size(f_id) \
                and f_cost[i] <= initialCost) \
                or (i + 1 < np.size(f_id) \
                and f_cost[i] <= initialCost \
                and f_cost[i+1] > initialCost):
            print '===federated (failed) case==='
            print 'cost: ' + '%.0f'%f_cost[i] + ', value: ' + '%.0f'%xf_value[i]
            print 'id ' + '%0d'%j + ': ' + elements_3[id_3==j].tostring()

def postProcessGA(db, maxCost=None):
    """
    Performs post-processing for genetic algorithm experiment.
    @param db: the database
    @type db: L{Database}
    """
    mapReduce(db, 'ga')
    query = {}
    if maxCost is not None:
        query['_id.totCost'] = {'$lte':maxCost}
    (id, elements, p1Cost, p2Cost, totCost,
     p1ValueStdErr, p2ValueStdErr, totValueStdErr, 
     p1ValueAvg, p2ValueAvg, totValueAvg,
     p1ExpValue, p2ExpValue, totExpValue, 
     pisl, oisl, osgl, independent) = processData(
        db, 'ga', query=query if query != {} else None)
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    if np.size(id) > 0:
        tradespaceCentralized('ga', id, 
            totCost/2, totExpValue/2, totValueStdErr/2,
            pisl, oisl, osgl,
            xlim=[np.min(totCost/2)
                  - .1*(np.max(totCost/2)
                        - np.min(totCost/2)),
                  np.max(totCost/2)
                  + .1*(np.max(totCost/2)
                        - np.min(totCost/2))],
            ylim=[np.min(totExpValue/2)
                  - .1*(np.max(totExpValue/2)
                        - np.min(totExpValue/2)),
                  np.max(totExpValue/2)
                  + .1*(np.max(totExpValue/2)
                        - np.min(totExpValue/2))])

def postProcessAll(db, numTurns=None, numPlayers=None,
                   initialCash=None, ops=None, fops=None):
    """
    Performs post-processing for all experimental results.
    @param db: the database
    @type db: L{Database}
    @param numTurns: the number of turns
    @type numTurns: L{int}
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
    query = {}
    if numTurns is not None:
        query['numTurns'] = numTurns
    if numPlayers is not None:
        query['numPlayers'] = numPlayers
    if initialCash is not None:
        query['initialCash'] = initialCash
    if ops is not None:
        query['ops'] = ops
    if fops is not None:
        query['fops'] = fops
    mapReduce(db, 'results', query=query if query != {} else None)
    (id, elements, p1Cost, p2Cost, totCost,
     p1ValueStdErr, p2ValueStdErr, totValueStdErr, 
     p1ValueAvg, p2ValueAvg, totValueAvg,
     p1ExpValue, p2ExpValue, totExpValue, 
     pisl, oisl, osgl, independent) = processData(db, 'results')
    
    plt.rcParams.update({'axes.labelsize':8,
                         'font.size':8, 
                         'font.family':'Times New Roman',
                         'legend.fontsize':8, 
                         'xtick.labelsize':8,
                         'ytick.labelsize':8})
    if np.size(id) > 0:
        tradespaceCentralized('results', id, 
            totCost/2, totExpValue/2, totValueStdErr/2,
            pisl, oisl, osgl)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program post-processes an OFS experiment.")
    parser.add_argument('experiment', type=str,
                        help='the experiment to run: masv, bvc, ga, or all')
    parser.add_argument('-l', '--logging', type=str, default='error',
                        choices=['debug','info','warning','error'],
                        help='logging level')
    parser.add_argument('--dbHost', type=str, default='localhost',
                        help='database host')
    parser.add_argument('--dbPort', type=int, default=27017,
                        help='database port')
    parser.add_argument('-c', '--maxCost', type=int, default=None,
                        help='maximum total cost for ga')
    parser.add_argument('-d', '--numTurns', type=int, default=None,
                        help='filter for all experiments: simulation duration (number of turns)')
    parser.add_argument('-p', '--numPlayers', type=int, default=None,
                        help='filter for all experiments: number of players')
    parser.add_argument('-i', '--initialCash', type=int, default=None,
                        help='filter for all experiments: initial cash')
    parser.add_argument('-o', '--ops', type=str, default=None,
                        help='filter for all experiments: federate operations model specification')
    parser.add_argument('-f', '--fops', type=str, default=None,
                        help='filter for all experiments: federation operations model specification')
    
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
    
    db = pymongo.MongoClient(args.dbHost, args.dbPort).ofs
    
    if args.experiment == 'masv':
        postProcessMASV(db)
    elif args.experiment == 'masv2':
        postProcessMASV(db, '2')
    elif args.experiment == 'bvc':
        postProcessBVC(db)
    elif args.experiment == 'bvc2':
        postProcessBVC(db, '2')
    elif args.experiment == 'bvc3':
        postProcessBVC(db, '3')
    elif args.experiment == 'bvcP':
        postPostProcessBVC(db)
    elif args.experiment == 'ga':
        postProcessGA(db, args.maxCost)
    else:
        postProcessAll(db, args.numTurns, args.numPlayers,
                       args.initialCash, args.ops, args.fops)