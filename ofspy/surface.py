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
Surface class.
"""

from .location import Location

class Surface(Location):
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