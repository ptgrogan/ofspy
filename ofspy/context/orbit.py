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
Orbit class.
"""

from .location import Location

class Orbit(Location):
    def __init__(self, sector, altitude):
        """
        @param sector: the sector of this orbit
        @type sector: L{int}
        @param altitude: the altitude of this orbit
        @type sector: L{string}
        """
        Location.__init__(self, sector)
        self.altitude = altitude
        
    def isOrbit(self):
        """
        Checks if this is an orbital location.
        
        @return: L{bool}
        """
        return True