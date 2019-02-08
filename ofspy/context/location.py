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
The L{ofspy.context.location} package defines different types of
locations for elements.
"""

import uuid

class Location(object):
    """
    An L{Location} defines a valid position of an element.
    """
    def __init__(self, sector, name=None):
        """
        @param sector: the sector of this location
        @type sector: L{int}
        @param name: the name of this location
        @type name: L{str}
        """
        self.sector = sector
        if name is None:
            self.name = uuid.uuid4
        else:
            self.name = name

    def isSurface(self):
        """
        Checks if this is a surface location.

        @return: L{bool}
        """
        return False

    def isOrbit(self):
        """
        Checks if this is an orbital location.

        @return: L{bool}
        """
        return False

    def __str__(self):
        """
        Gets the string representation for this lcation.
        """
        return self.name

class Surface(Location):
    """
    L{Surface} is a ground-based location on the Earth's surface.
    """
    def __init__(self, sector, name=None):
        """
        @param sector: the sector of this surface location
        @type sector: L{int}
        @param name: the name of this surface location
        @type name: L{str}
        """
        Location.__init__(self, sector, name=name)

    def isSurface(self):
        """
        Checks if this is a surface location.

        @return: L{bool}
        """
        return True

class Orbit(Location):
    """
    L{Orbit} is a space-based location in orbit about the Earth.
    """
    def __init__(self, sector, altitude, name=None):
        """
        @param sector: the sector of this orbit location
        @type sector: L{int}
        @param altitude: the altitude of this orbit location
        @type altitude: L{str}
        @param name: the name of this orbit location
        @type name: L{str}
        """
        Location.__init__(self, sector, name)
        self.altitude = altitude

    def isOrbit(self):
        """
        Checks if this is an orbital location.

        @return: L{bool}
        """
        return True
