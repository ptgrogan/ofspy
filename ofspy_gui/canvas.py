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

import math
import pkg_resources
from Tkinter import *
from PIL import ImageTk, Image

from ofspy.ofs import OFS
from ofspy.context import Context

class CanvasOFS(Canvas):
    def __init__(self, root, ofs=None):
        self.WIDTH = 800
        self.HEIGHT = 800
        Canvas.__init__(self, root, width=self.WIDTH, height=self.HEIGHT,
                        bg="black", highlightthickness=0)
        self.scale = 1.0
        
        self.ofs = ofs
        self.context = ofs.context
        for federation in self.context.federations:
            self.handleFederation(federation)
        
        self.pack(fill=BOTH, expand=YES)
        self.padding = 5
        
        self.landRadius = int(250*self.scale)
        self.demandRadius = int(100*self.scale)
        self.surfaceRadius = int(200*self.scale)
        self.atmosphereRadius = int(260*self.scale)
        self.orbitRadius = int(325*self.scale)
        self.dataSize = int(self.scale*8)
        self.locationSize = int(60*self.scale)
        self.elementSizes = {
            'GroundSta': self.locationSize*5./6,
            'SmallSat': self.locationSize*5./6,
            'MediumSat': int(self.locationSize*7./6),
            'LargeSat': int(self.locationSize*9./6),
            '': 0
        }
        self.demandSize = int(self.scale*40)
        self.federateSize = (int(180*self.scale), int(100*self.scale))
        
        self.colors = {}
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow']
        for i, federate in enumerate([f for federation in self.context.federations
                                      for f in federation.federates]):
            self.colors[federate.name] = colors[i % len(colors)]
        
        root.bind("<Escape>", self.init)
        root.bind("<space>", self.advance)
        
        self.animating = False
        self.numFrames = 10
        self.frameRate = 20
        
        image = Image.open(pkg_resources.resource_filename(
            __name__, 'resources/background.jpg'))
        image = image.resize((int(self.WIDTH*self.scale),
                              int(self.HEIGHT*self.scale)), Image.ANTIALIAS)
        self.backgroundImage = ImageTk.PhotoImage(image)
    
    def handleFederation(self, federation):
        federation.on('join', self.federationJoin)
        federation.on('quit', self.federationQuit)
        federation.on('exchange', self.federationExchange)
        federation.on('transport', self.controllerTransport)
        federation.on('sense', self.controllerSense)
        for federate in federation.federates:
            self.handleFederate(federate)
    def handleFederate(self, federate):
        federate.on('design', self.federateDesign)
        federate.on('commission', self.federateCommission)
        federate.on('decommission', self.federateDecommission)
        federate.on('contract', self.federateContract)
        federate.on('resolve', self.federateResolve)
        federate.on('transport', self.controllerTransport)
        federate.on('sense', self.controllerSense)
        for element in federate.elements:
            self.handleElement(element)
    def handleElement(self, element):
        element.on('store', self.elementStore)
        element.on('sense', self.elementSense)
        element.on('transfer', self.elementTransfer)
        element.on('transmit', self.elementTransmit)
        element.on('receive', self.elementReceive)
        for module in element.modules:
            self.handleModule(module)
    def handleModule(self, module):
        module.on('store', self.moduleStore)
        module.on('sense', self.moduleSense)
        module.on('transferOut', self.moduleTransferOut)
        module.on('transferIn', self.moduleTransferIn)
        module.on('exchange', self.moduleExchange)
        module.on('transmit', self.moduleTransmit)
        module.on('receive', self.moduleReceive)
    
    def federationJoin(self, federation, federate):
        print '{} joined {}'.format(
            federate.name, federation.name)
        self.handleFederate(federate)
    def federationQuit(self, federation, federate):
        print '{} quit {}'.format(
            federate.name, federation.name)
    def federationExchange(self, federation, amount, debtor, creditor):
        print '{} paid {} to {}'.format(
            debtor.name, amount, creditor.name)
    def federateDesign(self, federate, element):
        print '{} designed {}'.format(
            federate.name, element.name)
    def federateCommission(self, federate, element):
        print '{} commissioned {}'.format(
            federate.name, element.name)
        self.handleElement(element)
    def federateDecommission(self, federate, element):
        print '{} decommissioned {}'.format(
            federate.name, element.name)
    def federateContract(self, federate, demand):
        print '{} contracted {}'.format(
            federate.name, demand.name)
    def federateResolve(self, federate, contract, value):
        print '{} resolved {} for {}'.format(
            federate.name, contract.name, value)
    def controllerTransport(self, controller, protocol, data, txElement, rxElement):
        print '{} transported {} from {} to {} using {}'.format(
            controller.name, data, txElement.name, rxElement.name, protocol)
    def controllerSense(self, controller, contract, element):
        print '{} sensed {} using {}'.format(
            controller.name, contract.demand.name, element.name)
    def elementStore(self, element, data):
        print '{} stored {}'.format(
            element.name, data)
    def elementSense(self, element, contract):
        print '{} sensed {}'.format(
            element.name, contract.name)
    def elementTransfer(self, element, data, origin, destination):
        print '{} transfered {} from {} to {}'.format(
            element.name, data, origin.name, destination.name)
    def elementTransmit(self, element, protocol, data, rxElement):
        print '{} transmitted {} to {} using {}'.format(
            element.name, data, protocol, rxElement.name)
    def elementReceive(self, element, protocol, data, txElement):
        print '{} received {} from {} using {}'.format(
            element.name, data, protocol, txElement.name)
    def moduleStore(self, module, data):
        print '{} stored {}'.format(
            module.name, data)
    def moduleSense(self, module, contract):
        print '{} sensed {}'.format(
            module.name, contract.name)
    def moduleTransferOut(self, module, data):
        print '{} transferred out {}'.format(
            module.name, data)
    def moduleTransferIn(self, module, data):
        print '{} transferred in {}'.format(
            module.name, data)
    def moduleExchange(self, module, data, otherModule):
        print '{} exchanged {} with {}'.format(
            module.name, data, otherModule.name)
    def moduleTransmit(self, module, data, receiver):
        print '{} transmitted {} to {}'.format(
            module.name, data, receiver.name)
    def moduleReceive(self, module, data, transmitter):
        print '{} received {} from {}'.format(
            module.name, data, transmitter.name)
    
    def advance(self, event):
        if not self.animating:
            self.animate(0)
    
    def animate(self, frame):
        if frame < self.numFrames:
            self.animating = True
            self.draw(frame)
            self.after(self.frameRate, self.animate, frame+1)
        else:
            self.animating = False
            self.ofs.sim.advance()
            self.draw()
        
    def init(self, event):
        if not self.animating:
            self.ofs.sim.init()
            self.draw()
            
    def rotate(self, location, center, angle):
        r = math.hypot(location[0]-center[0], location[1]-center[1])
        theta = math.atan2(location[1]-center[1], location[0]-center[0])
        return (center[0] + r*math.cos(theta+angle),
                center[1] + r*math.sin(theta+angle))
        
    def drawFederate(self, federate, bbox, tags=()):
        text = '{} Cash: {:>8.0f}'.format(federate.name, federate.cash)
        self.create_rectangle(bbox,
                              fill='black',
                              outline=self.colors[federate.name])
        self.create_text(bbox[0]+self.padding,
                         bbox[1]+self.padding,
                         text=text,
                         anchor='nw',
                         width=self.federateSize[0]-2*self.padding,
                         fill='white', font='-weight bold')

        for i, c in enumerate(federate.contracts):
            self.drawContract(
                c, (bbox[0] + (2*i+1)*(self.padding/2+self.demandSize/2),
                    bbox[3] - self.demandSize/2 - self.padding - 20))
    
    def getElementLocation(self, element, frame=0):
        center = (self.winfo_reqwidth()/2., self.winfo_reqheight()/2.)
        theta = (element.location.sector - 1)*math.pi/3
        federates = [federate for federation in self.context.federations
                     for federate in federation.federates]
        if element.isGround():
            return (int(center[0] + self.surfaceRadius*math.cos(theta)),
                    int(center[1] + self.surfaceRadius*math.sin(theta)))
        elif element.isSpace():
            satellites = [e for federate in federates
                      for e in federate.elements
                      if e.location is not None
                      and e.location.isOrbit()
                      and e.location.sector==element.location.sector]
            e_i = satellites.index(element)
            deltaTheta = (0 if e_i == 0 and len(satellites) == 1
                          else -math.pi/24 if e_i == 0 and len(satellites) == 2
                          else math.pi/24 if e_i == 1 and len(satellites) == 2
                          else -math.pi/12 if e_i == 0 and len(satellites) == 3
                          else 0 if e_i == 1 and len(satellites) == 3
                          else math.pi/12 if e_i == 2 and len(satellites) == 3
                          else 0)
            location = (center[0] + int(self.orbitRadius*math.cos(theta+deltaTheta)),
                        center[1] + int(self.orbitRadius*math.sin(theta+deltaTheta)))
            return self.rotate(location, center, math.pi/(3*self.numFrames)*frame)
        
    def drawElement(self, element, location, tags=()):
        center = (self.winfo_reqwidth()/2, self.winfo_reqheight()/2)
        size = self.elementSizes['GroundSta' if element.isGround()
                                 else 'SmallSat' if element.isSpace()
                                 and element.capacity == 2
                                 else 'MediumSat' if element.isSpace()
                                 and element.capacity == 4
                                 else 'LargeSat' if element.isSpace()
                                 and element.capacity == 6
                                 else '']
        color = self.colors[self.context.getElementOwner(element).name]
        tags = tags + ('element',
                       'satellite' if element.isSpace() else 'station',
                       element.name)
        self.create_oval(location[0]-size/2,
                         location[1]-size/2,
                         location[0]+size/2,
                         location[1]+size/2,
                         width=0.0,
                         fill=color,
                         tags=tags + ('shape',))
        self.create_text(location[0],
                         location[1] + size/2 + self.padding,
                         text=element.name,
                         fill='black' if element.isGround() else 'white',
                         anchor='n',
                         tags=tags + ('label',))
        self.create_text(location[0],
                         location[1],
                         text=' '.join([m.name[:m.name.index('_')]
                                        for m in element.modules]),
                         fill='white',
                         justify=CENTER,
                         width=size,
                         tags=tags + ('modules',))
        data = [d for m in element.modules for d in m.data]
        for i, d in enumerate(data):
            theta = i*2*math.pi/len(data)-math.pi/2
            self.drawData(d, (location[0] + int(math.cos(theta)*size*7./16),
                              location[1] + int(math.sin(theta)*size*7./16)),
                          tags=tags)
        
    def drawData(self, data, location, tags=()):
        color = 'purple' if data.phenomenon == 'SAR' else 'cyan'
        size = self.dataSize
        tags = tags + ('data',)
        self.create_rectangle(
            location[0] - size/2,
            location[1] - size/2,
            location[0] + size/2,
            location[1] + size/2,
            fill=color,
            tags=tags)
        
    def drawContract(self, contract, location, tags=()):
        self.drawDemand(contract.demand, location, tags, contract.elapsedTime)
    
    def drawDisturbance(self, disturbance, location, tags=()):
        size = self.demandSize
        self.create_oval(location[0] - size/4,
                         location[1] - size/4,
                         location[0] + size/4,
                         location[1] + size/4,
                         fill= 'white',
                         outline='red', width=2.0)
        self.create_text(location[0],
                         location[1] + size/2+self.padding,
                         text=disturbance.name,
                         fill='black',
                         anchor='n')
    
    def drawDemand(self, demand, location, tags=(), elapsedTime=None):
        size = self.demandSize
        for t in range(0 if elapsedTime==None else elapsedTime,8):
            self.create_arc(location[0] - size/2,
                             location[1] - size/2,
                             location[0] + size/2,
                             location[1] + size/2,
                             start=(1-t)*360./8,
                             extent=360./8,
                             fill='green' if demand.getValueAt(t)==demand.getValueAt(0)
                             else 'yellow' if demand.getValueAt(t) > 0 else 'red')
        self.create_oval(location[0] - size/4,
                         location[1] - size/4,
                         location[0] + size/4,
                         location[1] + size/4,
                         fill= 'white')
        self.create_text(location[0],
                         location[1] + size/2+self.padding,
                         text=demand.name,
                         fill='black' if elapsedTime is None else 'white',
                         anchor='n')
        self.drawData(demand.generateData(), location)
    
    def drawContext(self):
        self.create_image(0, 0, image=self.backgroundImage, anchor=NW)
        center = (self.winfo_reqwidth()/2, self.winfo_reqheight()/2)
        
        self.create_text(center[0], self.padding,
                         text='Round {}'.format(self.context.time),
                         fill='white', font='-weight bold', anchor='n')
        
        self.create_oval(center[0] - self.orbitRadius,
                         center[1] - self.orbitRadius,
                         center[0] + self.orbitRadius,
                         center[1] + self.orbitRadius,
                         outline='white')
        self.create_oval(center[0] - self.atmosphereRadius,
                         center[1] - self.atmosphereRadius,
                         center[0] + self.atmosphereRadius,
                         center[1] + self.atmosphereRadius,
                         fill='blue')
        self.create_oval(center[0] - self.landRadius,
                         center[1] - self.landRadius,
                         center[0] + self.landRadius,
                         center[1] + self.landRadius,
                         fill='green')
        
        for i in range(6):
            theta = (i-1)*math.pi/3
            self.create_oval(center[0] + int(self.surfaceRadius*math.cos(theta)-self.locationSize/2),
                             center[1] + int(self.surfaceRadius*math.sin(theta)-self.locationSize/2),
                             center[0] + int(self.surfaceRadius*math.cos(theta)+self.locationSize/2),
                             center[1] + int(self.surfaceRadius*math.sin(theta)+self.locationSize/2),
                             width=0.0, fill='white')
            
            orbitExtent = 45.0
            self.create_arc(center[0] - self.orbitRadius,
                            center[1] - self.orbitRadius,
                            center[0] + self.orbitRadius,
                            center[1] + self.orbitRadius,
                            outline='purple',
                            width=20,
                            style=ARC,
                            start=0 - theta*180/math.pi - orbitExtent/2,
                            extent=orbitExtent)
            self.create_line(center[0] - self.atmosphereRadius*math.cos(theta+math.pi/6),
                             center[1] - self.atmosphereRadius*math.sin(theta+math.pi/6),
                             center[0] + self.atmosphereRadius*math.cos(theta+math.pi/6),
                             center[1] + self.atmosphereRadius*math.sin(theta+math.pi/6),
                             fill='black')
        
    def draw(self, frame=0):
        self.delete(ALL)
        center = (self.winfo_reqwidth()/2, self.winfo_reqheight()/2)
        federates = [federate for federation in self.context.federations
                     for federate in federation.federates]
        
        self.drawContext()
        for i in range(6):
            theta = (i-1)*math.pi/3
            for e in [e for federate in federates
                      for e in federate.elements
                      if e.location is not None
                      and e.location.sector==i]:
                self.drawElement(e, self.getElementLocation(e, frame))
            if frame <= 0:
                for e in [e for e in self.context.currentEvents
                          if e.sector == i]:
                    if e.isDemand():
                        self.drawDemand(
                            e, (center[0] + int(self.demandRadius*math.cos(theta)),
                                center[1] + int(self.demandRadius*math.sin(theta))))
                    elif e.isDisturbance():
                        self.drawDisturbance(
                            e, (center[0] + int(self.demandRadius*math.cos(theta)),
                                center[1] + int(self.demandRadius*math.sin(theta))))
        
        for i, f in enumerate(federates):
            self.drawFederate(
                f, (self.padding if i==0 or i==2
                    else self.winfo_reqwidth()-self.padding-self.federateSize[0],
                    self.padding if i==0 or i==1
                    else self.winfo_reqheight()-self.padding-self.federateSize[1],
                    self.padding+self.federateSize[0] if i==0 or i==2
                    else self.winfo_reqwidth()-self.padding,
                    self.padding+self.federateSize[1] if i==0 or i==1
                    else self.winfo_reqheight()-self.padding))