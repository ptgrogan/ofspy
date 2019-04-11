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

import sys
if sys.version_info[0] == 3:
    # python3
    from tkinter import *
else:
    # python2
    from Tkinter import *

from ofspy.ofs import OFS
from ofspy.context import Context
from ofspy.player import Federation, Federate
from ofspy.player.element import Element
from ofspy.player.module import Module

class LogOFS(Frame):
    def __init__(self, root, ofs):
        Frame.__init__(self, root, bg="black", borderwidth=0)
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow']
        self.text = Text(self, width=50, bg="black", fg='white',
                         highlightthickness=0, wrap=WORD)
        self.options = Frame(self, bg="black", borderwidth=0)
        self.showContext = BooleanVar()
        self.showContext.set(1)
        self.showFederation = BooleanVar()
        self.showFederation.set(1)
        self.showFederate = BooleanVar()
        self.showFederate.set(1)
        self.showElement = BooleanVar()
        self.showElement.set(1)
        self.showModule = BooleanVar()
        self.showModule.set(0)
        Checkbutton(self.options, text='Context',
                    bg="black", fg='white', selectcolor='black',
                    highlightbackground='black', highlightcolor='white',
                    activebackground='black', activeforeground='white',
                    variable=self.showContext,
                    highlightthickness=0).pack(side=LEFT, padx=5)
        Checkbutton(self.options, text='Federation',
                    bg="black", fg='white', selectcolor='black',
                    highlightbackground='black', highlightcolor='white',
                    activebackground='black', activeforeground='white',
                    variable=self.showFederation,
                    highlightthickness=0).pack(side=LEFT, padx=5)
        Checkbutton(self.options, text='Federate',
                    bg="black", fg='white', selectcolor='black',
                    highlightbackground='black', highlightcolor='white',
                    activebackground='black', activeforeground='white',
                    variable=self.showFederate,
                    highlightthickness=0).pack(side=LEFT, padx=5)
        Checkbutton(self.options, text='Element',
                    bg="black", fg='white', selectcolor='black',
                    highlightbackground='black', highlightcolor='white',
                    activebackground='black', activeforeground='white',
                    variable=self.showElement,
                    highlightthickness=0).pack(side=LEFT, padx=5)
        Checkbutton(self.options, text='Module',
                    bg="black", fg='white', selectcolor='black',
                    highlightbackground='black', highlightcolor='white',
                    activebackground='black', activeforeground='white',
                    variable=self.showModule,
                    highlightthickness=0).pack(side=LEFT, padx=5)
        self.options.pack(side=TOP)
        self.text.pack(side=BOTTOM, fill=BOTH, expand=1)
        self.text.config(state=DISABLED)

        self.handleContext(ofs.context)

    def handleContext(self, context):
        self.text.tag_configure(context.name, foreground='pink')
        context.on('init advance', self.contextAdvance)
        context.on('reveal', self.contextReveal)
        context.on('resolve', self.contextResolve)
        for i, federation in enumerate(context.federations):
            self.handleFederation(federation,
                                  self.colors[len(self.colors) - 1
                                              - (i % len(self.colors))])

    def handleFederation(self, federation, color):
        self.text.tag_configure(federation.name, foreground=color)
        federation.on('join', self.federationJoin)
        federation.on('quit', self.federationQuit)
        federation.on('exchange', self.federationExchange)
        federation.on('contract', self.controllerContract)
        federation.on('resolve', self.controllerResolve)
        federation.on('transport', self.controllerTransport)
        federation.on('sense', self.controllerSense)
        for i, federate in enumerate(federation.federates):
            self.handleFederate(federate, self.colors[i % len(self.colors)])

    def handleFederate(self, federate, color):
        self.text.tag_configure(federate.name, foreground=color)
        federate.on('design', self.federateDesign)
        federate.on('commission', self.federateCommission)
        federate.on('decommission', self.federateDecommission)
        federate.on('contract', self.controllerContract)
        federate.on('resolve', self.controllerResolve)
        federate.on('transport', self.controllerTransport)
        federate.on('sense', self.controllerSense)
        for element in federate.elements:
            self.handleElement(element, color)

    def handleElement(self, element, color):
        self.text.tag_configure(element.name, foreground=color)
        element.on('store', self.elementStore)
        element.on('sense', self.elementSense)
        element.on('transfer', self.elementTransfer)
        element.on('transmit', self.elementTransmit)
        element.on('receive', self.elementReceive)
        for module in element.modules:
            self.handleModule(module, color)

    def handleModule(self, module, color):
        self.text.tag_configure(module.name, foreground=color)
        module.on('store', self.moduleStore)
        module.on('sense', self.moduleSense)
        module.on('transferOut', self.moduleTransferOut)
        module.on('transferIn', self.moduleTransferIn)
        module.on('exchange', self.moduleExchange)
        module.on('transmit', self.moduleTransmit)
        module.on('receive', self.moduleReceive)

    def append(self, source, message):
        if ((isinstance(source, Context) and self.showContext.get())
             or (isinstance(source, Federation) and self.showFederation.get())
             or (isinstance(source, Federate) and self.showFederate.get())
             or (isinstance(source, Element) and self.showElement.get())
             or (isinstance(source, Module) and self.showModule.get())):
            self.text.config(state=NORMAL)
            self.text.insert(END, source.name, (source.name,))
            self.text.insert(END, ' {}'.format(message))
            self.text.config(state=DISABLED)

    def clear(self):
        self.text.config(state=NORMAL)
        self.text.delete('1.0',END)
        #for tag in self.tag_names():
        #    self.tag_delete(tag)
        self.text.config(state=DISABLED)

    def contextAdvance(self, context, time):
        self.clear()
        self.append(context, 'advanced to time {}\n'.format(time))
    def contextReveal(self, context, event):
        self.append(context, 'revealed {} in sector {}\n'.format(
            event.name, event.sector+1))
    def contextResolve(self, context, disturbance):
        self.append(context, 'resolved {} in sector {}\n'.format(
            disturbance.name, disturbance.sector+1))
    def federationJoin(self, federation, federate):
        self.append(federation, 'joined {}\n'.format(federate.name))
        self.text.handleFederate(federate, 'white') #FIXME temporary color
    def federationQuit(self, federation, federate):
        self.append(federation, 'quit {}\n'.format(federate.name))
    def federationExchange(self, federation, amount, debtor, creditor):
        self.append(federation, 'transferred {} cash from {} to {}\n'.format(
            amount, debtor.name, creditor.name))
    def federateDesign(self, federate, element, cost):
        self.append(federate, 'designed {} for {} cash\n'.format(
            element.name, cost))
    def federateCommission(self, federate, element, location, cost):
        self.append(federate, 'commissioned {} at {} for {:.0f} cash\n'.format(
            element.name, location.name, cost))
        self.handleElement(element, self.text.tag_cget(federate.name, 'foreground'))
    def federateDecommission(self, federate, element):
        self.append(federate, 'decommissioned {}\n'.format(element.name))
    def controllerContract(self, controller, demand):
        self.append(controller, 'contracted {}\n'.format(demand.name))
    def controllerResolve(self, controller, contract, value):
        self.append(controller, 'resolved {} for {} cash\n'.format(
            contract.demand.name, value))
    def controllerTransport(self, controller, protocol, data, txElement, rxElement):
        self.append(controller, 'transported {} from {} to {} using {}\n'.format(
            data.contract.demand.name, txElement.name, rxElement.name, protocol))
    def controllerSense(self, controller, contract, element):
        self.append(controller, 'sensed {} with {}\n'.format(
            contract.demand.name, element.name))
    def elementStore(self, element, data):
        self.append(element, 'stored {}\n'.format(
            data.contract.demand.name))
    def elementSense(self, element, contract):
        self.append(element, 'sensed {}\n'.format(
            contract.demand.name))
    def elementTransfer(self, element, data, origin, destination):
        self.append(element, 'transfered {} between {} and {}\n'.format(
            data.contract.demand.name, origin.name, destination.name))
    def elementTransmit(self, element, protocol, data, rxElement):
        self.append(element, 'transmitted {} to {} using {}\n'.format(
            data.contract.demand.name, rxElement.name, protocol))
    def elementReceive(self, element, protocol, data, txElement):
        self.append(element, 'received {} from {} using {}\n'.format(
            data.contract.demand.name, txElement.name, protocol))
    def moduleStore(self, module, data):
        self.append(module, 'stored {}\n'.format(
            data.contract.demand.name))
    def moduleSense(self, module, contract):
        self.append(module, 'sensed {}\n'.format(
            contract.demand.name))
    def moduleTransferOut(self, module, data):
        self.append(module, 'transferred out {}\n'.format(
            data.contract.demand.name))
    def moduleTransferIn(self, module, data):
        self.append(module, 'transferred in {}\n'.format(
            data.contract.demand.name))
    def moduleExchange(self, module, data, otherModule):
        self.append(module, 'exchanged {} with {}\n'.format(
            data.contract.demand.name, otherModule.name))
    def moduleTransmit(self, module, data, receiver):
        self.append(module, 'transmitted {} to {}\n'.format(
            data.contract.demand.name, receiver.name))
    def moduleReceive(self, module, data, transmitter):
        self.append(module, 'received {} from {}\n'.format(
            data.contract.demand.name, transmitter.name))
