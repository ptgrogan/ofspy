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
Test cases for L{ofspy.game} package.
"""

import unittest

from ..game import Game

class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.default = Game(2, 1000)

    def tearDown(self):
        self.default = None

    def test_generateContext(self):
        self.default.generateContext(seed=0, ops='', fops='')
