"""
Copyright 2017 Paul T. Grogan, Stevens Institute of Technology

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

import numpy as np
import scipy.stats as stats
import multiprocessing
import functools

from ofspy.ofs import OFS

def run_mono(seed, elements):
    return OFS(elements=elements, numPlayers=3, initialCash=0,
               numTurns=24, seed=seed, ops='d6,a,1', fops='n').execute()
def run_dist(seed, elements):
    return OFS(elements=elements, numPlayers=3, initialCash=0,
               numTurns=24, seed=seed, ops='d6,a,1', fops='x100,100,6,a,1').execute()

def compute_npv(cashflow, discount_rate):
    #return np.sum(cashflow[i]*(1-discount_rate)**i for i in range(len(cashflow)))
    return np.sum(cashflow[i]*(1-discount_rate)**(6*int(i/6)) for i in range(len(cashflow)))

def generate_data(mono, dist, discount_rate=0.0, num_runs=10, run_mono=run_mono, run_dist=run_dist):
    pool = multiprocessing.Pool(4)
    
    mono_designs = [element for player in mono for element in player]
    dist_designs = [element for player in dist for element in player]
    
    d_12_designs = [element for i, player in enumerate(dist) for element in player if i==0 or i==1]
    d_13_designs = [element.replace('MEO5','MEO3')  for i, player in enumerate(dist) for element in player if i==0 or i==2]
    d_23_designs = [element.replace('MEO4','MEO5') 
                    for i, player in enumerate(dist) for element in player if i==1 or i==2]
    
    mono_npv_1 = np.zeros(num_runs)
    mono_npv_2 = np.zeros(num_runs)
    mono_npv_3 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_mono, elements=mono_designs), range(num_runs))
    
    for seed, result in enumerate(results):
        mono_npv_1[seed] = compute_npv(result[0]['cashFlow'], discount_rate)
        mono_npv_2[seed] = compute_npv(result[1]['cashFlow'], discount_rate)
        mono_npv_3[seed] = compute_npv(result[2]['cashFlow'], discount_rate)

    print 'Mono E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(mono_npv_1), stats.norm.ppf(0.975)*stats.sem(mono_npv_1),
            np.mean(mono_npv_2), stats.norm.ppf(0.975)*stats.sem(mono_npv_2),
            np.mean(mono_npv_3), stats.norm.ppf(0.975)*stats.sem(mono_npv_3))
    
    dist_npv_1 = np.zeros(num_runs)
    dist_npv_2 = np.zeros(num_runs)
    dist_npv_3 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_mono, elements=dist_designs), range(num_runs))
    
    for seed, result in enumerate(results):
        dist_npv_1[seed] = compute_npv(result[0]['cashFlow'], discount_rate)
        dist_npv_2[seed] = compute_npv(result[1]['cashFlow'], discount_rate)
        dist_npv_3[seed] = compute_npv(result[2]['cashFlow'], discount_rate)
        
    print 'Dist_0 E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(dist_npv_1), stats.norm.ppf(0.975)*stats.sem(dist_npv_1),
            np.mean(dist_npv_2), stats.norm.ppf(0.975)*stats.sem(dist_npv_2),
            np.mean(dist_npv_3), stats.norm.ppf(0.975)*stats.sem(dist_npv_3))
    
    dist_npv_1_12 = np.zeros(num_runs)
    dist_npv_2_12 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_dist, elements=d_12_designs), range(num_runs))
    
    for seed, result in enumerate(results):
        dist_npv_1_12[seed] = compute_npv(result[0]['cashFlow'], discount_rate)
        dist_npv_2_12[seed] = compute_npv(result[1]['cashFlow'], discount_rate)
        
    print 'Dist_12 E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(dist_npv_1_12), stats.norm.ppf(0.975)*stats.sem(dist_npv_1_12),
            np.mean(dist_npv_2_12), stats.norm.ppf(0.975)*stats.sem(dist_npv_2_12),
            np.mean(dist_npv_3), stats.norm.ppf(0.975)*stats.sem(dist_npv_3))
    
    dist_npv_1_13 = np.zeros(num_runs)
    dist_npv_3_13 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_dist, elements=d_13_designs), range(num_runs))
        
    for seed, result in enumerate(results):
        dist_npv_1_13[seed] = compute_npv(result[0]['cashFlow'], discount_rate)
        dist_npv_3_13[seed] = compute_npv(result[2]['cashFlow'], discount_rate)
        
    print 'Dist_13 E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(dist_npv_1_13), stats.norm.ppf(0.975)*stats.sem(dist_npv_1_13),
            np.mean(dist_npv_2), stats.norm.ppf(0.975)*stats.sem(dist_npv_2),
            np.mean(dist_npv_3_13), stats.norm.ppf(0.975)*stats.sem(dist_npv_3_13))
    
    dist_npv_2_23 = np.zeros(num_runs)
    dist_npv_3_23 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_dist, elements=d_23_designs), range(num_runs))
        
    for seed, result in enumerate(results):
        dist_npv_2_23[seed] = compute_npv(result[1]['cashFlow'], discount_rate)
        dist_npv_3_23[seed] = compute_npv(result[2]['cashFlow'], discount_rate)
        
    print 'Dist_23 E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(dist_npv_1), stats.norm.ppf(0.975)*stats.sem(dist_npv_1),
            np.mean(dist_npv_2_23), stats.norm.ppf(0.975)*stats.sem(dist_npv_2_23),
            np.mean(dist_npv_3_23), stats.norm.ppf(0.975)*stats.sem(dist_npv_3_23))
    
    dist_npv_1_123 = np.zeros(num_runs)
    dist_npv_2_123 = np.zeros(num_runs)
    dist_npv_3_123 = np.zeros(num_runs)
    
    results = pool.map(functools.partial(run_dist, elements=dist_designs), range(num_runs))
        
    for seed, result in enumerate(results):
        dist_npv_1_123[seed] = compute_npv(result[0]['cashFlow'], discount_rate)
        dist_npv_2_123[seed] = compute_npv(result[1]['cashFlow'], discount_rate)
        dist_npv_3_123[seed] = compute_npv(result[2]['cashFlow'], discount_rate)
        
    print 'Dist_123 E[NPV]: {:.2f} ({:.2f}),  {:.2f} ({:.2f}),  {:.2f} ({:.2f})'.format(
            np.mean(dist_npv_1_123), stats.norm.ppf(0.975)*stats.sem(dist_npv_1_123),
            np.mean(dist_npv_2_123), stats.norm.ppf(0.975)*stats.sem(dist_npv_2_123),
            np.mean(dist_npv_3_123), stats.norm.ppf(0.975)*stats.sem(dist_npv_3_123))
    
    pool.terminate()
    
    return (mono_npv_1, mono_npv_2, mono_npv_3, 
            dist_npv_1, dist_npv_2, dist_npv_3, 
            dist_npv_1_12, dist_npv_2_12, 
            dist_npv_1_13, dist_npv_3_13, 
            dist_npv_2_23, dist_npv_3_23, 
            dist_npv_1_123, dist_npv_2_123, dist_npv_3_123)

def analyze_results((mono_npv_1, mono_npv_2, mono_npv_3, 
     dist_npv_1, dist_npv_2, dist_npv_3, 
     dist_npv_1_12, dist_npv_2_12,
     dist_npv_1_13, dist_npv_3_13, 
     dist_npv_2_23, dist_npv_3_23, 
     dist_npv_1_123, dist_npv_2_123, dist_npv_3_123)):
    
    lambda_ = [np.log((np.mean(mono_npv_1) - np.mean(dist_npv_1))/(np.mean(dist_npv_1_123) - np.mean(mono_npv_1))),
               np.log((np.mean(mono_npv_2) - np.mean(dist_npv_2))/(np.mean(dist_npv_2_123) - np.mean(mono_npv_2))),
               np.log((np.mean(mono_npv_3) - np.mean(dist_npv_3))/(np.mean(dist_npv_3_123) - np.mean(mono_npv_3)))]
    
    print 'Deviation loss ratios: {:.2f}, {:.2f}, {:.2f}'.format(lambda_[0], lambda_[1], lambda_[2])
    
    a_12 = ((0.5*(np.mean(dist_npv_1_12) - np.mean(dist_npv_1) + np.mean(mono_npv_1) - np.mean(mono_npv_1))
                +0.5*(np.mean(dist_npv_1_123) - np.mean(dist_npv_1_13) + np.mean(mono_npv_1) - np.mean(mono_npv_1)))/
                (np.mean(mono_npv_1) - np.mean(dist_npv_1) + np.mean(dist_npv_1_123) - np.mean(mono_npv_1)))
    
    a_13 = ((0.5*(np.mean(dist_npv_1_13) - np.mean(dist_npv_1) + np.mean(mono_npv_1) - np.mean(mono_npv_1))
                +0.5*(np.mean(dist_npv_1_123) - np.mean(dist_npv_1_12) + np.mean(mono_npv_1) - np.mean(mono_npv_1)))/
                (np.mean(mono_npv_1) - np.mean(dist_npv_1) + np.mean(dist_npv_1_123) - np.mean(mono_npv_1)))
    
    a_21 = ((0.5*(np.mean(dist_npv_2_12) - np.mean(dist_npv_2) + np.mean(mono_npv_2) - np.mean(mono_npv_2))
                +0.5*(np.mean(dist_npv_2_123) - np.mean(dist_npv_2_23) + np.mean(mono_npv_2) - np.mean(mono_npv_2)))/
                (np.mean(mono_npv_2) - np.mean(dist_npv_2) + np.mean(dist_npv_2_123) - np.mean(mono_npv_2)))
    
    a_23 = ((0.5*(np.mean(dist_npv_2_23) - np.mean(dist_npv_2) + np.mean(mono_npv_2) - np.mean(mono_npv_2))
                +0.5*(np.mean(dist_npv_2_123) - np.mean(dist_npv_2_12) + np.mean(mono_npv_2) - np.mean(mono_npv_2)))/
                (np.mean(mono_npv_2) - np.mean(dist_npv_2) + np.mean(dist_npv_2_123) - np.mean(mono_npv_2)))
    
    a_31 = ((0.5*(np.mean(dist_npv_3_13) - np.mean(dist_npv_3) + np.mean(mono_npv_3) - np.mean(mono_npv_3))
                +0.5*(np.mean(dist_npv_3_123) - np.mean(dist_npv_3_23) + np.mean(mono_npv_3) - np.mean(mono_npv_3)))/
                (np.mean(mono_npv_3) - np.mean(dist_npv_3) + np.mean(dist_npv_3_123) - np.mean(mono_npv_3)))
    
    a_32 = ((0.5*(np.mean(dist_npv_3_23) - np.mean(dist_npv_3) + np.mean(mono_npv_3) - np.mean(mono_npv_3))
                +0.5*(np.mean(dist_npv_3_123) - np.mean(dist_npv_3_13) + np.mean(mono_npv_3) - np.mean(mono_npv_3)))/
                (np.mean(mono_npv_3) - np.mean(dist_npv_3) + np.mean(dist_npv_3_123) - np.mean(mono_npv_3)))
    
    A = np.matrix([np.array([0, a_12, a_13]), 
                   np.array([a_21, 0, a_23]), 
                   np.array([a_31, a_32, 0])])
    
    x, v = np.linalg.eig(np.transpose(A))
    
    w = np.real(v[:,np.where(np.isclose(x, 1))[0][0]][:,0])
    w = np.divide(w, np.sum(w))
    print 'Weights: {:.2f}, {:.2f}, {:.2f}'.format(w.item(0,0), w.item(1,0), w.item(2,0))
    
    R = np.real(w[0]*lambda_[0] + w[1]*lambda_[1] + w[2]*lambda_[2])
    print 'WALM Risk: {:.2f}'.format(R.item(0,0))
    
    return lambda_,A,w,R
    

#%% main method
if __name__ == '__main__':
    #%% generate data
    mono = [[], 
            ['2.SmallSat@MEO6,SAR,pSGL','2.GroundSta@SUR1,pSGL'], 
            ['3.SmallSat@MEO4,VIS,pSGL','3.GroundSta@SUR5,pSGL']]
    dist_0 = [['1.SmallSat@MEO5,oISL,oSGL','1.GroundSta@SUR3,oSGL'],
              ['2.MediumSat@MEO6,SAR,oISL,pSGL,oSGL','2.GroundSta@SUR1,pSGL'], 
              ['3.MediumSat@MEO4,VIS,oISL,pSGL,oSGL','3.GroundSta@SUR5,pSGL']]
    lambda_0,A_0,w_0,R_0 = analyze_results(generate_data(mono, dist_0, discount_rate=0.02, num_runs=1000))

    dist_1 = [['1.SmallSat@MEO5,SAR,oSGL','1.GroundSta@SUR3,oSGL'],
              ['2.MediumSat@MEO6,SAR,pSGL,oSGL','2.GroundSta@SUR1,pSGL'], 
              ['3.MediumSat@MEO4,VIS,pSGL,oSGL','3.GroundSta@SUR5,pSGL']]
    lambda_1,A_1,w_1,R_1 = analyze_results(generate_data(mono, dist_1, discount_rate=0.02, num_runs=1000))