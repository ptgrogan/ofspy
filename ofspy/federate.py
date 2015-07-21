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

from .entity import Entity
from .contract import Contract
from .operations import Operations

class Federate(Entity):
    def __init__(self, name=None, initialCash=0, elements=[],
                 contracts=[], operations=Operations()):
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
        if name is not None:
            Entity.__init__(self, name=name)
        else:
            Entity.__init__(self)
        self.initialCash = initialCash
        self.cash = self.initialCash
        self.elements = elements
        self.contracts = contracts
        self.operations = operations
    
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
        if element not in self.elements:
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
        if element not in self.elements:
            logging.info('{0} could not decommission {1}.'.format(
                self.name, element.name))
        else:
            self.elements.remove(element)
            # self.cash += element.getDecommissionValue()
            logging.info('{0} decommissioned {1} for {2}.'.format(
                self.name, element.name, element.getDecommissionValue()))
            return True
        return False
    
    def liquidate(self, context):
        """
        Liquidates all assets for this federate.
        """
        for element in self.elements[:]:
            self.decommission(element)
        for contract in self.contracts[:]:
            self.resolve(contract, context)
    
    def canContract(self, demand, context):
        """
        Checks if this federate can contract a demand.
        @param demand: the demand to contract
        @type demand: L{Demand}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return (demand in context.currentEvents)
        
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
    
    def canSense(self, demand, element, context):
        """
        Checks if this federate can sense a demand.
        @param demand: the demand to sense
        @type demand: L{Demand}
        @param element: the element to sense
        @type element: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if element not in self.elements:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, element.name))
        elif (self.canContract(demand, context)
              or any(c.demand is demand for c in self.contracts)):
            return element.canSense(demand)
        return False
    
    def senseAndStore(self, contract, element, context):
        """
        Senses and stores data for a contract.
        @param contract: the contract to sense and store
        @type contract: L{Demand}
        @param element: the element to sense
        @type element: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if contract not in self.contracts:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, contract.name))
        elif (self.canSense(contract.demand, element, context)
              and element.senseAndStore(contract)):
            logging.info('{0} sensed and stored data for {1} using {2}'
                        .format(self.name, contract.name, element.name))
            return True
        else:
            logging.warning('{0} could not sense and store data for {1} using {2}'
                        .format(self.name, contract.name, element.name))
        return False
    
    def canTransport(self, protocol, data, txElement, rxElement):
        """
        Checks if this federate can transport data between elements.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transport
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @return: L{bool}
        """
        if txElement not in self.elements:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, txElement.name))
        elif rxElement not in self.elements:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, rxElement.name))
        else:
            return (txElement.canTransmit(protocol, data, rxElement)
                    and rxElement.canReceive(protocol, data, txElement))
    
    def transport(self, protocol, data, txElement, rxElement):
        """
        Transports data between elements.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transport
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @return: L{bool}
        """
        if canTransport(protocol, data, txElement, rxElement):
            if not txElement.transmit(protocol, data, rxElement):
                logging.warning('{0} could not transmit data to {1} with {2}'
                             .format(txElement.name, rxElement.name, prototcol))
            elif not rxElement.transmit(protocol, data, txElement):
                logging.warning('{0} could not receive data from {1} with {2}'
                             .format(rxElement.name, txElement.name, prototcol))
            else:
                logging.info('{0} transported data from {1} to {2} with {3}'
                            .format(self.name, txElement.name, rxElement.name, protocol))
                return True
        else:
            logging.warning('{0} could not transport data between {1} and {2} with {3}'
                         .format(self.name, txElement.name, rxElement.name, prototcol))
        return False
    
    def default(self, contract, context):
        """
        Defaults on a contract.
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
            self.cash -= contract.demand.getDefaultValue()
            self.deleteData(contract)
            self.contracts.remove(contract)
            context.pastEvents.append(contract.demand)
            logging.info('{0} defaulted on {1} for {2} penalty'
                        .format(self.name, contract.name,
                                contract.demand.getDefaultValue()))
            return True
        return False
    
    def deleteData(self, contract):
        """
        Deletes data for a contract.
        @param contract: the contract
        @type contract: L{Contract}
        """
        for element in self.elements:
            for module in element.modules:
                for d in module.data[:]:
                    if d.contract is contract:
                        module.data.remove(d)
    
    def getDataLocation(self, contract):
        """
        Gets the location of data for a contract.
        @param contract: the contract
        @type contract: L{Contract}
        @return: L{Location}
        """
        return next((element.location
                     for element in self.elements
                     if any(any(d.contract is contract
                                for d in module.data)
                            for module in element.modules)), None)
    
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
        elif contract.isCompleted(self.getDataLocation(contract)):
            self.cash += contract.getValue()
            self.deleteData(contract)
            self.contracts.remove(contract)
            context.pastEvents.append(contract.demand)
            logging.info('{0} completed {1} for {2} reward'
                        .format(self.name, contract.name,
                                contract.contract.getValue()))
            return True
        return False
    
    def init(self, sim):
        """
        Initializes this federate in a simulation.
        @param sim: the simulator
        """
        super(Federate, self).init(sim)
        self.cash = self.initialCash
        for element in self.elements:
            element.init(sim)
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