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

from .entity import Entity
from .operations import Operations

class Federation(Entity):
    def __init__(self, name=None, federates=None, operations=Operations()):
        """
        @param name: the name of this federation
        @type name: L{str}
        @param federates: the federates within this federation
        @type federates: L{list}
        @param operations: the operations model of this federation
        @type operations: L{Operations}
        """
        if name is not None:
            Entity.__init__(self, name=name)
        else:
            Entity.__init__(self)
        if federates is None:
            self._initFederates = []
        else:
            self._initFederates = federates
        self.federates = self._initFederates
        self.operations = operations
    
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
            return True
        return False
    
    def canSense(self, demand, element, context):
        """
        Checks if this federation can sense a demand.
        @param demand: the demand to sense
        @type demand: L{Demand}
        @param element: the element to sense
        @type element: L{Element}
        @param context: the context
        @type context: L{Context}
        @return: L{bool}
        """
        if element not in [element for element in federate.elements
                           for federate in self.federates]:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, element.name))
        elif (canContract(demand, context)
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
        if contract not in [contract for contract in federate.contracts
                           for federate in self.federates]:
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
        if txElement not in [element for element in federate.elements
                             for federate in self.federates]:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, txElement.name))
        elif rxElement not in [element for element in federate.elements
                             for federate in self.federates]:
            logging.warning('{0} does not control {1}.'
                        .format(self.name, rxElement.name))
        elif ('p' in protocol
              and next((federate for federate in self.federates
                        if txElement in federate.elements), None)
              is not next((federate for federate in self.federates
                           if rxElement in federate.elements), None)):
            logging.warning('{0} cannot transport from {1} to {2} with proprietary {3}.'
                          .format(self.name, txElement.name, rxElement.name, protocol))
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

    def init(self, sim):
        """
        Initializes this federation in a simulation.
        @param sim: the simulator
        """
        super(Federation, self).init(sim)
        self.federates = self._initFederates
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