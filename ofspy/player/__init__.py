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
The L{ofspy.player} package contains classes related to the players.
"""

import logging

from ..simulation import Entity
from .operations import Operations

class Controller(Entity):
    """
    A L{Controller} can execute controlled functions.
    """
    def __init__(self, name=None, operations=Operations(), priceSGL=0, priceISL=0):
        """
        @param name: the name of this controller
        @type name: L{str}
        @param operations: the operations model of this controller
        @type operations: L{Operations}
        @param priceSGL: the price for SGL services
        @type priceSGL: L{float}
        @param priceISL: the price for ISL services
        @type priceISL: L{float}
        """
        Entity.__init__(self, name=name)
        self.operations = operations
        self.priceSGL = priceSGL
        self.priceISL = priceISL
    
    def getElements(self):
        """
        Gets the elements controlled by this controller.
        @return L{list}
        """
        return []

    def getFederates(self):
        """
        Gets the federates controlled by this controller.
        @return L{list}
        """
        return []

    def getContracts(self):
        """
        Gets the contracts controlled by this controller.
        @return L{list}
        """
        return []

    def liquidate(self, context):
        """
        Liquidates all assets.
        """
        for element in self.getElements():
            self.decommission(element)
        for contract in self.getContracts():
            self.resolve(contract, context)

    def canContract(self, demand, context):
        """
        Checks if this controller can contract a demand.
        @param demand: the demand to contract
        @type demand: L{Demand}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return (demand in context.currentEvents
                and any(element.canSense(demand)
                        for element in self.getElements()))

    def canResolve(self, contract):
        """
        Checks if this controller can resolve a contract.
        @param contract: the contract to resolve
        @type contract: L{Contract}
        @return: L{bool}
        """
        return contract in self.getContracts()

    def canSense(self, demand, element, context):
        """
        Checks if this controller can sense a demand.
        @param demand: the demand to sense
        @type demand: L{Demand}
        @param element: the element to sense
        @type element: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        # can sense demand if:
        # element is controlled by this controller
        # AND the element can sense the demand
        # AND (this controller can contract the demand
        #      OR this controller has a contract for the demand)
        return (element in self.getElements()
                and element.canSense(demand)
                and (self.canContract(demand, context)
                    or any(contract.demand is demand
                       for contract in self.getContracts())))

    def senseAndStore(self, contract, element, context):
        """
        Senses and stores data for a contract.
        @param contract: the contract to sense and store
        @type contract: L{Contract}
        @param element: the element to sense
        @type element: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if contract not in self.getContracts():
            logging.warning('{0} does not control {1}.'
                        .format(self.name, contract.name))
        elif element not in self.getElements():
            logging.warning('{0} does not control {1}.'
                        .format(self.name, element.name))
        elif self.canSense(contract.demand, element, context):
            # find the federate which can sense this demand
            for federate in [federate for federate in self.getFederates()
                             if federate.canSense(contract.demand, element, context)]:
                element.senseAndStore(contract)
                logging.info('{0} sensed and stored data for {1} using {2}'
                            .format(federate.name, contract.name, element.name))
                self.trigger('sense', federate, contract, element)
                return True
        else:
            logging.warning('{0} could not sense and store data for {1} using {2}'
                        .format(self.name, contract.name, element.name))
        return False

    def couldTransport(self, protocol, data, txElement,
                       rxElement, txLocation, rxLocation, context):
        """
        Checks if this controller could transport data between elements.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transport
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @param txLocation: the transmitting location
        @type txLocation: L{Location}
        @param rxLocation: the receiving location
        @type rxLocation: L{Location}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return (txElement.couldTransmit(protocol, data, rxElement,
                                        txLocation, rxLocation, context)
                and rxElement.couldReceive(protocol, data, txElement,
                                           txLocation, rxLocation, context)
                and ('o' in protocol
                     or next((federate for federate in self.getFederates()
                              if txElement in federate.elements), None)
                     is next((federate for federate in self.getFederates()
                              if rxElement in federate.elements), None)))

    def canTransport(self, protocol, data, txElement, rxElement, context):
        """
        Checks if this controller can transport data between elements.
        @param protocol: the transmission protocol
        @type protocol: L{str}
        @param data: the data to transport
        @type data: L{Data}
        @param txElement: the transmitting element
        @type txElement: L{Element}
        @param rxElement: the receiving element
        @type rxElement: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        return (self.couldTransport(protocol, data, txElement, rxElement,
                                    txElement.location, rxElement.location, context)
                and txElement in self.getElements()
                and rxElement in self.getElements()
                and txElement.canTransmit(protocol, data, rxElement, context)
                and rxElement.canReceive(protocol, data, txElement, context))

    def transport(self, protocol, data, txElement, rxElement, context):
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
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if txElement not in self.getElements():
            logging.warning('{0} does not control {1}.'
                        .format(self.name, txElement.name))
        elif rxElement not in self.getElements():
            logging.warning('{0} does not control {1}.'
                        .format(self.name, rxElement.name))
        elif self.canTransport(protocol, data, txElement, rxElement, context):
            if not txElement.transmit(protocol, data, rxElement, context):
                logging.warning('{0} could not transmit {1} to {2} with {3}'
                             .format(txElement.name, data,
                                     rxElement.name, protocol))
            elif not rxElement.receive(protocol, data, txElement, context):
                logging.warning('{0} could not receive {1} from {2} with {3}'
                             .format(rxElement.name, str(data),
                                     txElement.name, protocol))
            else:
                logging.info('{0} transported {1} from {2} to {3} with {4}'
                            .format(self.name, str(data), txElement.name,
                                    rxElement.name, protocol))
                self.trigger('transport', self, protocol, data, txElement, rxElement)
                return True
        else:
            logging.warning('{0} could not transport {1} between {2} and {3} with {4}'
                         .format(self.name, str(data), txElement.name,
                                 rxElement.name, protocol))
        return False

    def deleteData(self, contract):
        """
        Deletes data for a contract.
        @param contract: the contract
        @type contract: L{Contract}
        """
        for element in self.getElements():
            for module in element.modules:
                for d in module.data[:]:
                    if (d.contract is contract
                        and module.canTransferOut(d)):
                        module.transferOut(d)

    def contract(self, demand, context):
        """
        Contracts a demand.
        @param demand: the demand to contract
        @type demand: L{Demand}
        @param context: the context
        @type context: L{Context}
        @return: L{Contract}
        """
        if self.canContract(demand, context):
            for federate in [federate for federate in self.getFederates()
                             if federate.canContract(demand, context)]:
                context.currentEvents.remove(demand)
                contract = Contract(demand)
                federate.contracts.append(contract)
                logging.info('{0} contracted for {1}'
                            .format(federate.name, demand.name))
                self.trigger('contract', federate, demand)
                return contract
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
        if self.canResolve(contract):
            for federate in [federate for federate in self.getFederates()
                             if federate.canResolve(contract)]:
                element = context.getDataElement(contract)
                value = (contract.getValue()
                         if contract.isCompleted(element.location
                                                 if element is not None
                                                 else None)
                         else contract.demand.getDefaultValue())
                federate.receiveCash(value)
                federate.contracts.remove(contract)
                context.pastEvents.append(contract.demand)
                self.deleteData(contract)
                logging.info('{0} resolved {1} for {2} cash'
                            .format(federate.name, contract.name, value))
                self.trigger('resolve', federate, contract, value)
                return True
        logging.warning('{0} could not resolve {1}.'
                    .format(self.name, contract.name))
        return False

    def canExchange(self, amount, debtor, creditor):
        """
        Checks if this federation can exchange cash between federates.
        @param amount: the amount of cash to exchange
        @type amount: L{float}
        @param debtor: the debtor federate
        @type debtor: L{Federate}
        @param creditor: the creditor federate
        @type creditor: L{Federate}
        @return: L{bool}
        """
        return (debtor in self.getFederates()
                and creditor in self.getFederates())
                #and amount > debtor.getCash())
                # removed to allow exchanges below 0 cash

    def exchange(self, amount, debtor, creditor):
        """
        Exchanges cash between two federates in this federation.
        @param amount: the amount of cash to exchange
        @type amount: L{float}
        @param debtor: the debtor federate
        @type debtor: L{Federate}
        @param creditor: the creditor federate
        @type creditor: L{Federate}
        @return: L{bool}
        """
        if debtor not in self.getFederates():
            logging.warning('{} does not control {}'
                            .format(self.name, debtor.name))
        elif creditor not in self.getFederates():
            logging.warning('{} does not control {}'
                            .format(self.name, creditor.name))
        #elif amount > debtor.getCash():
        #    logging.warning('{} exceeds {} cash.'
        #                    .format(amount, debtor.name))
        # removed warning to allow exchanges below 0 cash
        elif self.canExchange(amount, debtor, creditor):
            debtor.sendCash(amount)
            creditor.receiveCash(amount)
            logging.info('{} paid {} to {}'
                         .format(debtor.name, amount, creditor.name))
            self.trigger('exchange', self, amount, debtor, creditor)
            return True
        return False
    
    def getElementOwner(self, element):
        """
        Gets the federate owner of an element.
        @param element: the element
        @type element: L{Element}
        @return L{Federate}
        """
        for federate in self.getFederates():
            if element in federate.getElements():
                return federate
        return None
    
    def getContractOwner(self, contract):
        """
        Gets the federate owner of a contract.
        @param contract: the contract
        @type contract: L{Contract}
        @return L{Federate}
        """
        for federate in self.getFederates():
            if contract in federate.getContracts():
                return federate
        return None

class Contract(Entity):
    """
    A L{Contract} assigns responsibility to serve a demand.
    """
    def __init__(self, demand):
        """
        @param demand: the demand for this contract
        @type demand: L{Demand}
        """
        Entity.__init__(self, name='C-{0}'.format(demand.name))
        self.demand = demand
        self.elapsedTime = 0
        self._initElapsedTime = 0
        self._nextElapsedTime = 0

    def getValue(self):
        """
        Gets the current value of this contract.
        @return: L{float}
        """
        return self.demand.getValueAt(self.elapsedTime)

    def isDefaulted(self, dataLocation):
        """
        Checks if this contract is defaulted.
        @param dataLocation: the location of contracted data
        @type dataLocation: L{Location}
        @return: L{bool}
        """
        return self.demand.isDefaultedAt(self.elapsedTime) \
                or dataLocation is None

    def isCompleted(self, dataLocation):
        """
        Checks if this contract is completed.
        @param dataLocation: the location of contracted data
        @type dataLocation: L{Location}
        @return: L{bool}
        """
        return not self.isDefaulted(dataLocation) \
                and dataLocation.isSurface()

    def init(self, sim):
        """
        Initializes this contract in a simulation.
        @param sim: the simulator
        @type sim: L{Simulation}
        """
        super(Contract, self).init(sim)
        self.elapsedTime = self._initElapsedTime

    def tick(self, sim):
        """
        Ticks this contract in a simulation.
        @param sim: the simulator
        @type sim: L{Simulation}
        """
        super(Contract, self).tick(sim)
        self._nextElapsedTime += sim.timeStep

    def tock(self):
        """
        Tocks this contract in a simulation.
        """
        super(Contract, self).tock()
        self.elapsedTime = self._nextElapsedTime

class Data(object):
    """
    L{Data} models data collected in support of a contract.
    """
    def __init__(self, phenomenon, size, contract=None):
        """
        @param phenomenon: the phenomenon of this data
        @type phenomenon: L{str}
        @param size: the size of this data
        @type size: L{int}
        @param contract: the contract for this data
        @type contract: L{str}
        """
        self.phenomenon = phenomenon
        self.size = size
        self.contract = contract

    def __str__(self):
        """
        Gets the string representation of this data.
        """
        return 'd{0}'.format(self.contract)

class Federation(Controller):
    """
    A L{Federation} controls a set of federates.
    """
    def __init__(self, name=None, federates=None, operations=Operations(), priceSGL=0, priceISL=0):
        """
        @param name: the name of this federation
        @type name: L{str}
        @param federates: the federates within this federation
        @type federates: L{list}
        @param operations: the operations model of this federation
        @type operations: L{Operations}
        @param priceSGL: the price for SGL services
        @type priceSGL: L{float}
        @param priceISL: the price for ISL services
        @type priceISL: L{float}
        """
        Controller.__init__(self, name=name, operations=operations,
                            priceSGL=priceSGL, priceISL=priceISL)
        if federates is None:
            self._initFederates = []
        else:
            self._initFederates = federates
        self.federates = self._initFederates[:]

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

class Federate(Controller):
    """
    A L{Federate} can control a set of elements.
    """
    def __init__(self, name=None, initialCash=0, elements=None,
                 contracts=None, operations=Operations(), priceSGL=0, priceISL=0):
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
        @param priceSGL: the price for SGL services
        @type priceSGL: L{float}
        @param priceISL: the price for ISL services
        @type priceISL: L{float}
        """
        Controller.__init__(self, name=name, operations=operations, 
                            priceSGL=priceSGL, priceISL=priceISL)
        self.initialCash = initialCash
        self._cash = self.initialCash
        if elements is None:
            self._initElements = []
        else:
            self._initElements = elements[:]
        self.elements = self._initElements
        if contracts is None:
            self._initContracts = []
        else:
            self._initContracts = contracts[:]
        self.contracts = self._initContracts
        self.cashFlow = [self.initialCash]

    def getCash(self):
        """
        Gets the amount of cash for this federate.
        @return L{float}
        """
        return self._cash

    def receiveCash(self, amount):
        """
        Receives cash for this federate.
        @param amount: the amount of cash to receive
        @type amount: L{float}
        """
        self._cash += amount
        self.cashFlow[-1] += amount

    def sendCash(self, amount):
        """
        Sends cash for this federate.
        @param amount: the amount of cash to send
        @type amount: L{float}
        """
        self._cash -= amount
        self.cashFlow[-1] -= amount

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
        elif element.getDesignCost() > self.getCash():
            logging.warning('{0} design costs exceeds cash.'
                         .format(element.name))
        else:
            self.elements.append(element)
            cost = element.getDesignCost()
            self.sendCash(cost)
            logging.info('{0} designed {1} for {2}'
                        .format(self.name, element.name, cost))
            self.trigger('design', self, element, cost)
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
        elif element.getCommissionCost(location, context) > self.getCash():
            logging.warning('{0} commission cost exceeds cash.'
                         .format(element.name))
        elif element.commission(location, context):
            logging.info('{0} commissioned {1} for {2}.'
                        .format(self.name, element.name,
                                element.getCommissionCost(location, context)))
            cost = element.getCommissionCost(location, context)
            self.sendCash(cost)
            self.trigger('commission', self, element, location, cost)
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
            # self.receiveCash(element.getDecommissionValue())
            logging.info('{0} decommissioned {1} for {2}.'.format(
                self.name, element.name, element.getDecommissionValue()))
            self.trigger('decommission', self, element)
            return True
        return False

    def init(self, sim):
        """
        Initializes this federate in a simulation.
        @param sim: the simulator
        """
        super(Federate, self).init(sim)
        self._cash = self.initialCash
        self.cashFlow = [self.initialCash]
        self.elements = self._initElements[:]
        for element in self.elements:
            element.init(sim)
        self.contracts = self._initContracts[:]
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
        self.cashFlow.append(0)
        for element in self.elements:
            element.tock()
        for contract in self.contracts:
            contract.tock()
