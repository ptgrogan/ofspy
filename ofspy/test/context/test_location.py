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
Test cases for L{ofspy.location} package.
"""

import unittest

from ...context.location import Location, Surface, Orbit

"""
Test cases for L{ofspy.location.Location} class.
"""

class LocationTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Location(0)
    def tearDown(self):
        self.default = None
    def test_isSurface(self):
        self.assertFalse(self.default.isSurface())
    def test_isOrbit(self):
        self.assertFalse(self.default.isOrbit())

"""
Test cases for L{ofspy.location.Surface} class.
"""

class SurfaceTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Surface(0)
    def tearDown(self):
        self.default = None
    def test_isSurface(self):
        self.assertTrue(self.default.isSurface())
    def test_isOrbit(self):
        self.assertFalse(self.default.isOrbit())

"""
Test cases for L{ofspy.location.Orbit} class.
"""

class OrbitTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Orbit(0, "LEO")
    def tearDown(self):
        self.default = None
    def test_isSurface(self):
        self.assertFalse(self.default.isSurface())
    def test_isOrbit(self):
        self.assertTrue(self.default.isOrbit())
