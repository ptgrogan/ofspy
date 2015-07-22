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
Test cases for L{ofspy.lp_solve}.
"""

import unittest

from ..lp_solve import LinearProgram
from ..lp_solve import Row

class RowTestCase(unittest.TestCase):
    def test_add(self):
        r = Row()
        r.add('test', 1)
        self.assertIn('test', r.raw)
        self.assertEqual(r.raw['test'], 1)
        r.add('test', 2)
        self.assertEqual(r.raw['test'], 1+2)
        r2 = Row()
        r2.add('test', 3)
        r2.add('moo', 1)
        r.add(row=r2)
        self.assertEqual(r.raw['test'], 1+2+3)
        self.assertIn('moo', r.raw)
        self.assertEqual(r.raw['moo'], 1)
    def test_subtract(self):
        r = Row()
        r.add('test', 6)
        r.subtract('test', 2)
        self.assertEqual(r.raw['test'], 6-2)
        r2 = Row()
        r2.add('test', 1)
        r2.add('moo', 1)
        r.subtract(row=r2)
        self.assertEqual(r.raw['test'], 6-2-1)
        self.assertIn('moo', r.raw)
        self.assertEqual(r.raw['moo'], -1)
    def test_multiply(self):
        r = Row()
        r.add('test', 2)
        r.add('moo', 1)
        r.multiply(2)
        self.assertEqual(r.raw['test'], 2*2)
        self.assertEqual(r.raw['moo'], 1*2)
    def test_toText(self):
        r = Row()
        r.add('test', 2)
        r.add('moo', 1)
        self.assertEqual(r.toText(),' +2 test +1 moo')
        self.assertEqual(Row().toText(),'0')

class LinearProgramTestCase(unittest.TestCase):
    def test_setOutputFile(self):
        lp = LinearProgram()
        lp.setOutputFile('')
    def test_addColumn(self):
        lp = LinearProgram()
        lp.addColumn('x')
        self.assertIn('x', lp.columns)
        self.assertEqual(lp.columns['x'], 1)
        lp.addColumn('y', True)
        self.assertIn('y', lp.columns)
        self.assertEqual(lp.columns['y'], 2)
    def test_addConstraint(self):
        lp = LinearProgram()
        lp.addColumn('x')
        lp.addColumn('y')
        r = Row()
        r.add('x', 1)
        lp.addConstraint(r, 'LE', 1)
    def test_setObjective(self):
        lp = LinearProgram()
        lp.addColumn('x')
        lp.addColumn('y')
        r = Row()
        r.add('x', 1)
        r.add('y', 1)
        lp.addConstraint(r, 'LE', 1)
        j = Row()
        j.add('x', 0.1)
        j.add('y', 0.2)
        lp.setObjective(j, False)
    def test_solve(self):
        lp = LinearProgram()
        lp.addColumn('x')
        lp.addColumn('y')
        r = Row()
        r.add('x', 1)
        r.add('y', 1)
        lp.addConstraint(r, 'LE', 1)
        j = Row()
        j.add('x', 0.1)
        j.add('y', 0.2)
        lp.setObjective(j, False)
        lp.solve()
        self.assertAlmostEqual(lp.solution[0][0], 0)
        self.assertAlmostEqual(lp.solution[0][1], 1)
        self.assertAlmostEqual(lp.solution[1], 1)
    def test_get(self):
        lp = LinearProgram()
        lp.addColumn('x')
        lp.addColumn('y')
        r = Row()
        r.add('x', 1)
        r.add('y', 1)
        lp.addConstraint(r, 'LE', 1)
        j = Row()
        j.add('x', 0.1)
        j.add('y', 0.2)
        lp.setObjective(j, False)
        code, description = lp.solve()
        self.assertAlmostEqual(lp.get('x'), 0)
        self.assertAlmostEqual(lp.get('y'), 1)
        self.assertAlmostEqual(lp.getValue(), 1)
    