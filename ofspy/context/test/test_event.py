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
Test cases for L{ofspy.context.event}.
"""

import unittest

from ..event import Event

class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Event(0)
    def tearDown(self):
        self.default = None
    def test_isDisturbance(self):
        self.assertFalse(self.default.isDisturbance())
    def test_isDemand(self):
        self.assertFalse(self.default.isDemand())