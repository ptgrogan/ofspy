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
Based on node-lp_solve by Stephen Remde released under an MIT license
https://github.com/smremde/node-lp_solve
"""

from lpsolve55 import *

class LinearProgram(object):
    ConstraintTypes = {'LE':1, 'GE':2, 'EQ':3}
    ConstraintText = {'LE':'<=', 'GE':'>=', 'EQ':'='}
    SolveResult = {
        '-5': 'UNKNOWNERROR',
        '-4': 'DATAIGNORED',
        '-3': 'NOBFP',
        '-2': 'NOMEMORY',
        '-1': 'NOTRUN',
        '0': 'OPTIMAL',
        '1': 'SUBOPTIMAL',
        '2': 'INFEASIBLE',
        '3': 'UNBOUNDED',
        '4': 'DEGENERATE',
        '5': 'NUMFAILURE',
        '6': 'USERABORT',
        '7': 'TIMEOUT',
        '8': 'RUNNING',
        '9': 'PRESOLVED'
    }
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        lpsolve('delete_lp', self.lp)
    
    def __init__(self, name=None):
        self.lp = lpsolve('make_lp', 0, 0)
        if name is not None:
            lpsolve('set_lp_name', self.lp, name)
        lpsolve('set_verbose', self.lp, 'IMPORTANT')
        lpsolve('set_outputfile', self.lp, '')
        self.version = lpsolve('lp_solve_version')
        self.columns = {}
        self.constraints = []
        self.objective = Row()
        self.solution = []
        
    def setOutputFile(self, fname):
        """
        Sets the output file for this linear program.
        @param fname: the file name
        @type fname: L{str}
        """
        fileName = fname if fname is not None else ''
        if not lpsolve('set_outputfile', self.lp, fileName):
            raise Exception('error writing to file {0}'.format(fileName))
        
    def addColumn(self, name=None, isInteger=False, isBinary=False):
        """
        Adds a column to this linear program.
        @param name: the column name
        @type name: L{str}
        @param isInteger: true, if this is an integer column
        @type isInteger: L{bool}
        @param isBinary: true, if this is a binary column
        @type isBinary: L{bool}
        @return: L{str}
        """
        colId = len(self.columns)+1
        if name is None:
            name = 'col_{}'.format(cId)
        self.columns[name] = colId
        
        colValues = [0]*(lpsolve('get_Nrows', self.lp)+1)
        
        if not lpsolve('add_column', self.lp, colValues):
            raise Exception('error adding column {}'.format(name))
        #if not lpsolve('set_col_name', self.lp, colId, name):
        #    raise Exception('error setting column name {}'.format(name))
        if isInteger and not lpsolve('set_int', self.lp, colId, isInteger):
            raise Exception('error setting integer type for column {}'.format(name))
        if isBinary and not lpsolve('set_binary', self.lp, colId, isBinary):
            raise Exception('error setting binary type for column {}'.format(name))
        
        return name
            
    def addConstraint(self, row, constraintType, constant, name=None):
        """
        Adds a constraint to this linear program.
        @param row: the constraint row
        @type row: L{Row}
        @param constraintType: the constraint type
        @type constraintType: L{str}
        @param constant: the constraint constant
        @type constant: L{float}
        @param name: the constraint name
        @type name: L{str}
        """
        colValues = [0]*(lpsolve('get_Ncolumns', self.lp)+1)
        
        for key in row.raw:
            colId = self.columns[key]
            colValues[colId] += row.raw[key]
            
        if name is None:
            name = 'con_{}'.format(len(self.constraints)+1)
        
        self.constraints.append({'name': name,
                                 'row': row.toText(),
                                 'constraint':constraintType,
                                 'constant': constant})
        if not lpsolve('add_constraint', self.lp, colValues[1:],
                       LinearProgram.ConstraintTypes[constraintType],
                       constant):
            raise Exception('error adding constraint {}'.format(name))
        # nRows = lpsolve('get_Nrows', self.lp)
        # lpsolve('set_row_name', self.lp, nRows, name)
    
    def setObjective(self, row, minimize=True):
        """
        Sets the objective for this linear program.
        @param row: the objective row
        @type row: L{Row}
        @param minimize: true, if the objective is minimized
        @type minimize: L{bool}
        """
        colValues = [0]*(lpsolve('get_Ncolumns', self.lp)+1)
        
        for key in row.raw:
            colId = self.columns[key]
            colValues[colId] += row.raw[key]
        self.objective = {'minimize': minimize,
                          'row': row}
        
        if minimize:
            lpsolve('set_minim', self.lp)
        else:
            lpsolve('set_maxim', self.lp)
            
        if not lpsolve('set_obj_fn', self.lp, colValues[1:]):
            raise Exception('error setting objective function')
    def solve(self):
        """
        Solves the linear program.
        """
        code = lpsolve('solve', self.lp)
        if code == 0 or code == 1 or code == 9:
             self.solution = lpsolve('get_variables', self.lp)[0]
        return code, LinearProgram.SolveResult[str(code)]
    def get(self, column):
        """
        Gets the solved value for a column.
        @param column: the column
        @type column: L{str}
        @return: L{float}
        """
        return (None if len(self.solution) < self.columns[column] - 1
                else self.solution[self.columns[column] - 1])
    def dumpProgram(self):
        """
        Dumps the program to a string format.
        @return: L{str}
        """
        string = ('minimize' if self.objective['minimize']
                  else 'maximize') + ':' + self.objective['row'].toText() + ';\n'
        for c in self.constraints:
            string += '{}: {} {} {};\n'.format(
                c['name'], c['row'],
                LinearProgram.ConstraintText[c['constraint']],
                c['constant'])
        return string
    def dumpSolution(self):
        """
        Dumps the solution to a string format.
        @return: L{str}
        """
        string = ''
        for col in self.columns:
            string += '{} = {};\n'.format(
                col, self.solution[self.columns[col]-1])
        return string

class Row(object):
    def __init__(self, clone=None):
        self.raw = {}
        if clone is not None:
            for key in clone.raw:
                self.raw[key] = clone[key]
    
    def add(self, key=None, value=None, row=None):
        """
        Adds a key-value pair or row to this row.
        @param key: the key to add
        @type key: L{str}
        @param value: the value to add
        @type value: L{float}
        @param row: the row to add
        @type row: L{Row}
        @return: L{Row}
        """
        if key is not None and value is not None:
            self.raw[key] = ((self.raw[key]
                              if key in self.raw
                              else 0) + value)
        if row is not None and hasattr(row, 'raw'):
            for key in row.raw:
                self.raw[key] = ((self.raw[key]
                                  if key in self.raw
                                  else 0) + row.raw[key])
        return self
    
    def subtract(self, key=None, value=None, row=None):
        """
        Subtracts a key-value pair or row from this row.
        @param key: the key to subtract
        @type key: L{str}
        @param value: the value to subtract
        @type value: L{float}
        @param row: the row to subtract
        @type row: L{Row}
        @return: L{Row}
        """
        if key is not None and value is not None:
            self.raw[key] = ((self.raw[key]
                              if key in self.raw
                              else 0) - value)
        if row is not None and hasattr(row, 'raw'):
            for key in row.raw:
                self.raw[key] = ((self.raw[key]
                                  if key in self.raw
                                  else 0) - row.raw[key])
        return self
            
    def multiply(self, value):
        """
        Multiplies this row by a scalar value.
        @param value: the scalar value
        @type value: L{float}
        @return: L{Row}
        """
        if value == 0:
            self.raw = {}
        else:
            for key in self.raw:
                self.raw[key] = self.raw[key] * value
        return self
    
    def toText(self):
        """
        Gets the lp_solve-compatible text format for this row.
        @return: L{str}
        """
        string = ''
        for key in self.raw:
            if self.raw[key] == 0:
                continue
            if self.raw[key] < 0:
                string += ' -'
                self.raw[key] = -self.raw[key]
            else:
                string += ' +'
            string += '{} {}'.format(self.raw[key], key)
        return string if string != '' else '0'