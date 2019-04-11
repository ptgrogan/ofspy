"""
Copyright 2015 Paul T. Grogan, Massachusetts Institute of Technology
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

"""
L{ofspy.player.operations} package.
"""

import math
from functools import reduce

class Operations(object):
    """
    L{Operations} represents an operational decision-making algorithm.
    """
    def __init__(self):
        self.penaltyMemo = {}

    def execute(self, controller, context):
        """
        Executes this operations model.
        @param controller: the controller for this operations model
        @type controller: L{Entity}
        @param context: the context of operations
        @type context: L{Context}
        """
        pass

    def getStoragePenalty(self, element, context):
        if not element in self.penaltyMemo:
            demands = [e for e in context.events
                       if e.isDemand()
                       and element.couldSense(e.generateData())]
                       #and (element.couldSense(e.generateData())
                       #     or (any(m.isLink() and m.isISL()
                       #             for m in element.modules)))]
            values = [0]
            values.extend(map(lambda d: d.getValueAt(0), demands))
            values = list(set(values))
            values.sort()
            counts = list(map(lambda v: len([d for d in demands if d.getValueAt(0) == v]), values))
            counts[0] += len(context.events) - len(demands)
            expValMax = reduce(lambda e, v:
                               e + v*(math.pow(sum(counts[0:values.index(v)+1]), 1)
                                      - math.pow(sum(counts[0:values.index(v)]), 1))
                               / math.pow(sum(counts),1), values)
            self.penaltyMemo[element] = -1*max(100, expValMax) # minimum penalty 100
        return self.penaltyMemo[element]
