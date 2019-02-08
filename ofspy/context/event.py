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
The L{ofspy.context.events} package defines different types of events
that can occur in the environment.
"""

import operator
import uuid

from ..player import Data

class Event(object):
    """
    An L{Event} defines an uncertain occurrance.
    """

    def __init__(self, sector, name=None):
        """
        @param sector: the spatial sector where this event occurs
        @type sector: L{int}
        @param name: the name of this event
        @type name: L{str}
        """
        self.sector = sector
        if name is None:
            self.name = uuid.uuid4
        else:
            self.name = name

    def isDemand(self):
        """
        Checks if this is a demand event.

        @return: L{bool}
        """
        return False

    def isDisturbance(self):
        """
        Checks if this is a disturbance event.

        @return: L{bool}
        """
        return False

    def __str__(self):
        """
        Gets the string representation of this event.
        """
        return self.name

class ValueSchedule(object):
    """
    A L{ValueSchedule} determines the value of a time-varying asset.
    """
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

class Demand(Event):
    """
    A L{Demand} defines a demand for data collection and down-link.
    """

    def __init__(self, sector, phenomenon, size,
                 valueSchedule=ValueSchedule(), name=None):
        """
        @param sector: the associated spatial sector
        @type sector: L{int}
        @param phenomenon: the phenomenon demanded
        @type phenomenon: L{str}
        @param size: the size of data demanded
        @type size: L{int}
        @param valueSchedule: the value schedule for completing this demand
        @type valueSchedule: L{ValueSchedule}
        @param name: the name of this demand
        @type name: L{str}
        """
        Event.__init__(self, sector, name=name)
        self.phenomenon = phenomenon
        self.size = size
        self.valueSchedule = valueSchedule

    def getValueAt(self, time):
        """
        Gets the value of this demand at an elapsed time.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        return self.valueSchedule.getValueAt(time)

    def getDefaultTime(self):
        """
        Gets the time when this demand is defaulted.
        @param time: the time
        @type time: L{float}
        @return: L{float}
        """
        return self.valueSchedule.getDefaultTime()

    def isDefaultedAt(self, time):
        """
        Checks if this demand is defaulted at an elapsed time.
        @param time: the time
        @type time: L{float}
        @return: L{bool}
        """
        return time > self.getDefaultTime()

    def isCompletedAt(self, location):
        """
        Checks if this demand is completed at a location.
        @param location: the location
        @type location: L{Location}
        @return: L{bool}
        """
        return location is not None and location.isSurface()

    def getDefaultValue(self):
        """
        Gets the defaulted value of this demand.
        @return: L{float}
        """
        return self.valueSchedule.defaultValue

    def generateData(self, contract=None):
        """
        Generates data for this demand.
        @return: L{Data}
        """
        return Data(self.phenomenon, self.size, contract)

    def isDemand(self):
        """
        Checks if this is a demand event.

        @return: L{bool}
        """
        return True

class Disturbance(Event):
    """
    A L{Disturbance} defines a potentially-damaging event.
    """

    def __init__(self, sector, hitChance=0, maxHits=0, name=None):
        """
        @param sector: the associated spatial sector
        @type sector: L{int}
        @param hitChance: the chance this disturbance hits a subsystem
        @type hitChance: L{float}
        @param maxHits: the maximum number of hits per system
        @type maxHits: L{int}
        @param name: the name of this disturbance
        @type name: L{str}
        """
        Event.__init__(self, sector, name=name)
        self.hitChance = hitChance
        self.maxHits = maxHits

    def isDisturbance(self):
        """
        Checks if this is a disturbance event.

        @return: L{bool}
        """
        return True
