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

"""
ValueSchedule class.
"""

import operator

class ValueSchedule(object):
    def __init__(self, timeValuePairs=[(0,0)], defaultValue=0):
        """
        @param valueSchedule: the set of time-value pairs defining value
        @type valueSchedule: L{list}
        @param defaultValue: the value if defaulted
        @type defaultValue: L{float}
        """
        self.timeValuePairs = sorted(timeValuePairs, key=operator.itemgetter(0))
        self.defaultValue = defaultValue
    
    def getValueAt(self, time):
        """
        Gets the value of this schedule at a time.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        for tvp in self.timeValuePairs:
            if time <= tvp[0]:
                return tvp[1]
        return self.defaultValue
    
    def getDefaultTime(self):
        """
        Gets the time when this schedule enters default.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        return max(tvp[0] for tvp in self.timeValuePairs)
    
    def __str__(self):
        """
        Gets the string representation of this value schedule.
        """
        return '[{0}, {1}]'.format(self.timeValuePairs, self.defaultValue)