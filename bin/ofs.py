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
import logging
import math
import sys,os
# add ofspy to system path
sys.path.append(os.path.abspath('..'))

from ofspy.ofs import OFS
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program runs an Orbital Federates simulation.")
    parser.add_argument('elements', type=str, nargs='+',
                        help='the list of initial elements, e.g. 1.GroundSta@SUR1,pSGL 1.SmallSat@LEO1,pSGL,SAR')
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
    
    results = OFS(elements=args.elements, numTurns=args.numTurns,
                  numPlayers=args.numPlayers, initialCash=args.initialCash,
                  seed=args.seed, ops=args.ops, fops=args.fops).execute()
    for result in results:
        print '{0}:{1}'.format(result[0], result[1])