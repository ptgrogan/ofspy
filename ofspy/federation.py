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
Federation class.
"""

import logging

from .controller import Controller
from .operations import Operations

class Federation(Controller):
    def __init__(self, name=None, federates=None, operations=Operations()):
        """
        @param name: the name of this federation
        @type name: L{str}
        @param federates: the federates within this federation
        @type federates: L{list}
        @param operations: the operations model of this federation
        @type operations: L{Operations}
        """
        Controller.__init__(self, name=name)
        if federates is None:
            self._initFederates = []
        else:
            self._initFederates = federates
        self.federates = self._initFederates[:]
        self.operations = operations
    
    def getElements(self):
        """
        Gets the elements controlled by this federation.
        @return L{list}
        """
        return [element for federate in self.federates
                for element in federate.elements]
    
    def getFederates(self):
        """
        Gets the federates controlled by this federation.
        @return L{list}
        """
        return self.federates[:]
    
    def getContracts(self):
        """
        Gets the contracts controlled by this federation.
        @return L{list}
        """
        return [contract for federate in self.federates
                for contract in federate.contracts]
    
    def join(self, federate):
        """
        Joins a federate to this federation.
        @param federate: the federate to join
        @type federate: L{Federate}
        @return: L{bool}
        """
        if federate in self.federates:
            logging.info('{0} already a member of {1}'
                         .format(federate.name, self.name))
        else:
            self.federates.append(federate)
            logging.info('{0} joined {1}'
                         .format(federate.name, self.name))
            self.trigger('join', self, federate)
            return True
        return False
    
    def quit(self, federate):
        """
        Quits a federate from this federation.
        @param federate: the federate to quit
        @type federate: L{Federate}
        @return: L{bool}
        """
        if federate not in self.federates:
            logging.warning('{0} is not a member of {1}'
                         .format(federate.name, self.name))
        else:
            self.federates.remove(federate)
            logging.info('{0} quit {1}'
                         .format(federate.name, self.name))
            self.trigger('quit', self, federate)
            return True
        return False

    def init(self, sim):
        """
        Initializes this federation in a simulation.
        @param sim: the simulator
        """
        super(Federation, self).init(sim)
        self.federates = self._initFederates[:]
        for federate in self.federates:
            federate.init(sim)
    
    def tick(self, sim):
        """
        Ticks this federation in a simulation.
        @param sim: the simulator
        """
        super(Federation, self).tick(sim)
        for federate in self.federates:
            federate.tick(sim)
    
    def tock(self):
        """
        Tocks this federation in a simulation.
        """
        super(Federation, self).tock()
        for federate in self.federates:
            federate.tock()