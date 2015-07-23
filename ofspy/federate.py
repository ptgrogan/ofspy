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
Federate class.
"""

import logging

from .controller import Controller
from .contract import Contract
from .operations import Operations

class Federate(Controller):
    def __init__(self, name=None, initialCash=0, elements=None,
                 contracts=None, operations=Operations()):
        """
        @param name: the name of this federate
        @type name: L{str}
        @param initialCash: the initial cash for this federate
        @type initialCash: L{float}
        @param elements: the elements controlled by this federate
        @type elements: L{list}
        @param contracts: the contracts owned by this federate
        @type contracts: L{list}
        @param operations: the operations model of this federate
        @type operations: L{Operations}
        """
        Controller.__init__(self, name=name)
        self.initialCash = initialCash
        self.cash = self.initialCash
        if elements is None:
            self._initElements = []
        else:
            self._initElements = elements
        self.elements = self._initElements
        if contracts is None:
            self._initContracts = []
        else:
            self._initContracts = contracts
        self.contracts = self._initContracts
        self.operations = operations
    
    def getElements(self):
        """
        Gets the elements controlled by this controller.
        @return L{list}
        """
        return self.elements[:]
    
    def getFederates(self):
        """
        Gets the federates controlled by this controller.
        @return L{list}
        """
        return [self]
    
    def getContracts(self):
        """
        Gets the contracts controlled by this controller.
        @return L{list}
        """
        return self.contracts[:]
    
    def design(self, element):
        """
        Designs an element for this federate.
        @param element: the element to design
        @type element: L{Element}
        @return L{bool}
        """
        if element.getContentsSize() > element.capacity:
            logging.warning('{0} contents exceeds capacity.'
                         .format(element.name))
        elif element.getDesignCost() > self.cash:
            logging.warning('{0} design costs exceeds cash.'
                         .format(element.name))
        else:
            self.elements.append(element)
            self.cash -= element.getDesignCost()
            logging.info('{0} designed {1} for {2}'
                        .format(self.name, element.name,
                                element.getDesignCost()))
            return True
        return False
    
    def commission(self, element, location, context):
        """
        Commissions an element at a location.
        @param element: the element to commission
        @type element: L{Element}
        @param location: the location at which to commission
        @type location: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if element not in self.getElements():
            logging.warning('{0} does not control {1}.'
                        .format(self.name, element.name))
        elif element.getCommissionCost(location, context) > self.cash:
            logging.warning('{0} commission cost exceeds cash.'
                         .format(element.name))
        elif element.commission(location, context):
            logging.info('{0} commissioned {1} for {2}.'
                        .format(self.name, element.name,
                                element.getCommissionCost(location, context)))
            self.cash -= element.getCommissionCost(location, context)
            return True
        else:
            logging.warning('{0} could not commission {1}.'
                         .format(self.name, element.name))
        return False
    
    def decommission(self, element):
        """
        Decommissions an element.
        @param element: the element to decommission
        @type element: L{Element}
        @return: L{bool}
        """
        if element not in self.getElements():
            logging.info('{0} could not decommission {1}.'.format(
                self.name, element.name))
        else:
            self.elements.remove(element)
            # self.cash += element.getDecommissionValue()
            logging.info('{0} decommissioned {1} for {2}.'.format(
                self.name, element.name, element.getDecommissionValue()))
            return True
        return False
        
    def contract(self, demand, context):
        """
        Contracts a demand for this federate.
        @param demand: the demand to contract
        @type demand: L{Demand}
        @param context: the context
        @type context: L{Context}
        @return: L{Contract}
        """
        if self.canContract(demand, context):
            context.currentEvents.remove(demand)
            contract = Contract(demand)
            self.contracts.append(contract)
            logging.info('{0} contracted for {1}'
                        .format(self.name, demand.name))
            return contract
        else:
            logging.warning('{0} could not contract for {1}'
                        .format(self.name, demand.name))
        return None
        
    def resolve(self, contract, context):
        """
        Resolves a contract.
        @param contract: the transmission protocol
        @type contract: L{Contract}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if contract not in self.contracts:
            logging.warning('{0} does not own {1}.'
                        .format(self.name, contract.name))
        else:
            self.cash += contract.getValue()
            self.deleteData(contract)
            self.contracts.remove(contract)
            context.pastEvents.append(contract.demand)
            logging.info('{0} resolved {1} for {2} cash'
                        .format(self.name, contract.name,
                                contract.getValue()))
            return True
        return False
    
    def init(self, sim):
        """
        Initializes this federate in a simulation.
        @param sim: the simulator
        """
        super(Federate, self).init(sim)
        self.cash = self.initialCash
        self.elements = self._initElements
        for element in self.elements:
            element.init(sim)
        self.contracts = self._initContracts
        for contract in self.contracts:
            contract.init(sim)
    
    def tick(self, sim):
        """
        Ticks this federate in a simulation.
        @param sim: the simulator
        """
        super(Federate, self).tick(sim)
        for element in self.elements:
            element.tick(sim)
        for contract in self.contracts:
            contract.tick(sim)
    
    def tock(self):
        """
        Tocks this federate in a simulation.
        """
        super(Federate, self).tock()
        for element in self.elements:
            element.tock()
        for contract in self.contracts:
            contract.tock()