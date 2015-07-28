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

from Tkinter import *
from PIL import ImageTk, Image
import math
import sys,os
# add ofspy to system path
sys.path.append(os.path.abspath('..'))

from ofspy.ofs import OFS
from ofspy.context import Context

class OFS_GUI(Canvas):
    def __init__(self, root, ofs=None):
        self.WIDTH = 800
        self.HEIGHT = 800
        Canvas.__init__(self, root, width=self.WIDTH, height=self.HEIGHT,
                        bg="black", highlightthickness=0)
        self.scale = 1.0
        
        self.ofs = ofs
        self.context = ofs.context
        self.pack(fill=BOTH, expand=YES)
        
        root.bind("<Escape>", self.init)
        root.bind("<space>", self.advance)
        
        #image = Image.open('resources/background.jpg')
        #image = image.resize((int(self.WIDTH*self.scale),
        #                      int(self.HEIGHT*self.scale)), Image.ANTIALIAS)
        #self.backgroundImage = ImageTk.PhotoImage(image)
        
    def advance(self, event):
        self.ofs.sim.advance()
        self.draw()
        
    def init(self, event):
        self.ofs.sim.init()        
        self.draw()
        
    def draw(self):
        self.delete('all')
        #self.create_image(0, 0, image=self.backgroundImage, anchor=NW)
        center = (self.winfo_reqwidth()/2, self.winfo_reqheight()/2)
        textOffset = 5
        
        self.create_text(center[0], textOffset,
                         text='Round {}'.format(self.context.time),
                         fill='white', font='-weight bold', anchor='n')
        
        landSize = int(500*self.scale)
        atmosphereSize = int(520*self.scale)
        orbitSize = int(650*self.scale)
        
        self.create_oval(center[0] - orbitSize/2,
                         center[1] - orbitSize/2,
                         center[0] + orbitSize/2,
                         center[1] + orbitSize/2,
                         outline='white')
        self.create_oval(center[0] - atmosphereSize/2,
                         center[1] - atmosphereSize/2,
                         center[0] + atmosphereSize/2,
                         center[1] + atmosphereSize/2,
                         fill='blue')
        self.create_oval(center[0] - landSize/2,
                         center[1] - landSize/2,
                         center[0] + landSize/2,
                         center[1] + landSize/2,
                         fill='green')
        
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple']
        federates = [federate for federation in self.context.federations
                     for federate in federation.federates]
        
        locationSize = int(50*self.scale)
        for i in range(6):
            theta = -math.pi/3+i*math.pi/3
            surfaceOffset = landSize/2 - 30*self.scale - locationSize/2
            self.create_oval(center[0] + int(surfaceOffset*math.cos(theta)-locationSize/2),
                             center[1] + int(surfaceOffset*math.sin(theta)-locationSize/2),
                             center[0] + int(surfaceOffset*math.cos(theta)+locationSize/2),
                             center[1] + int(surfaceOffset*math.sin(theta)+locationSize/2),
                             width=0.0, fill='white')
            stationSize = locationSize
            textOffset = 5
            for e in [e for federate in federates
                      for e in federate.elements
                      if e.location is not None
                      and e.location.isSurface()
                      and e.location.sector==i]:
                color = colors[federates.index(next(f for f in federates
                                                    if e in f.elements))]
                self.create_oval(center[0] + int(surfaceOffset*math.cos(theta)-stationSize/2),
                                 center[1] + int(surfaceOffset*math.sin(theta)-stationSize/2),
                                 center[0] + int(surfaceOffset*math.cos(theta)+stationSize/2),
                                 center[1] + int(surfaceOffset*math.sin(theta)+stationSize/2),
                                 width=0.0, fill=color)
                self.create_text(center[0] + int(surfaceOffset*math.cos(theta)),
                                 center[1] + int(surfaceOffset*math.sin(theta)
                                           + stationSize/2+textOffset),
                                 text=e.name, fill='black', anchor='n')
                self.create_text(center[0] + int(surfaceOffset*math.cos(theta)),
                                 center[1] + int(surfaceOffset*math.sin(theta)),
                                 text=' '.join([m.name[:m.name.index('_')] for m in e.modules]),
                                 fill='white', width=stationSize)
                data = [d for m in e.modules for d in m.data]
                for d_i, d in enumerate(data):
                    dTheta = d_i*2*math.pi/len(data)-math.pi/2
                    dCenter = (center[0] + int(surfaceOffset*math.cos(theta)),
                               center[1] + int(surfaceOffset*math.sin(theta)))
                    dotSize = self.scale*8
                    self.create_rectangle(
                        dCenter[0] + int(math.cos(dTheta)*stationSize*7./16) - dotSize/2,
                        dCenter[1] + int(math.sin(dTheta)*stationSize*7./16) - dotSize/2,
                        dCenter[0] + int(math.cos(dTheta)*stationSize*7./16) + dotSize/2,
                        dCenter[1] + int(math.sin(dTheta)*stationSize*7./16) + dotSize/2,
                        fill= 'purple' if d.phenomenon == 'SAR' else 'cyan')
            for e in [e for e in self.context.currentEvents
                      if e.sector == i and e.isDemand()]:
                demandSize = self.scale*40
                demandOffset = landSize/4 - demandSize/2
                for t in range(8):
                    self.create_arc(center[0] + int(demandOffset*math.cos(theta)-demandSize/2),
                                     center[1] + int(demandOffset*math.sin(theta)-demandSize/2),
                                     center[0] + int(demandOffset*math.cos(theta)+demandSize/2),
                                     center[1] + int(demandOffset*math.sin(theta)+demandSize/2),
                                     start=(1-t)*360./8, extent=360./8,
                                     fill= 'green' if e.getValueAt(t)==e.getValueAt(0)
                                     else 'yellow' if e.getValueAt(t) > 0 else 'red')
                self.create_oval(center[0] + int(demandOffset*math.cos(theta)-demandSize/4),
                                 center[1] + int(demandOffset*math.sin(theta)-demandSize/4),
                                 center[0] + int(demandOffset*math.cos(theta)+demandSize/4),
                                 center[1] + int(demandOffset*math.sin(theta)+demandSize/4),
                                 fill= 'white')
                dataSize = self.scale*8
                self.create_rectangle(
                    center[0] + int(demandOffset*math.cos(theta)-dataSize/2),
                    center[1] + int(demandOffset*math.sin(theta)-dataSize/2),
                    center[0] + int(demandOffset*math.cos(theta)+dataSize/2),
                    center[1] + int(demandOffset*math.sin(theta)+dataSize/2),
                    fill= 'purple' if e.phenomenon == 'SAR' else 'cyan')
                self.create_text(center[0] + int(demandOffset*math.cos(theta)),
                                 center[1] + int(demandOffset*math.sin(theta)
                                           + demandSize/2+textOffset),
                                 text=e.name, fill='black', anchor='n')
                
            self.create_line(center[0] - atmosphereSize/2*math.cos(theta+math.pi/6),
                             center[1] - atmosphereSize/2*math.sin(theta+math.pi/6),
                             center[0] + atmosphereSize/2*math.cos(theta+math.pi/6),
                             center[1] + atmosphereSize/2*math.sin(theta+math.pi/6),
                             fill='black')
            
            orbitExtent = 45.0
            self.create_arc(center[0] - orbitSize/2,
                            center[1] - orbitSize/2,
                            center[0] + orbitSize/2,
                            center[1] + orbitSize/2,
                            outline='purple',
                            width=20,
                            style=ARC,
                            start=0 - theta*180/math.pi - orbitExtent/2,
                            extent=orbitExtent)
            
            smallSatelliteSize = locationSize
            mediumSatelliteSize = locationSize*1.4
            largeSatelliteSize = locationSize*1.8
            satellites = [e for federate in federates
                      for e in federate.elements
                      if e.location is not None
                      and e.location.isOrbit()
                      and e.location.sector==i]
            for e_i, e in enumerate(satellites):
                color = colors[federates.index(next(f for f in federates
                                                    if e in f.elements))]
                satelliteSize = (smallSatelliteSize if e.capacity == 2
                                 else mediumSatelliteSize if e.capacity == 4
                                 else largeSatelliteSize)
                deltaTheta = (0 if e_i == 0 and len(satellites) == 1
                              else -math.pi/24 if e_i == 0 and len(satellites) == 2
                              else math.pi/24 if e_i == 1 and len(satellites) == 2
                              else -math.pi/12 if e_i == 0 and len(satellites) == 3
                              else 0 if e_i == 1 and len(satellites) == 3
                              else math.pi/12 if e_i == 2 and len(satellites) == 3
                              else 0)
                self.create_oval(center[0] + int(orbitSize*math.cos(theta+deltaTheta)/2-satelliteSize/2),
                                 center[1] + int(orbitSize*math.sin(theta+deltaTheta)/2-satelliteSize/2),
                                 center[0] + int(orbitSize*math.cos(theta+deltaTheta)/2+satelliteSize/2),
                                 center[1] + int(orbitSize*math.sin(theta+deltaTheta)/2+satelliteSize/2),
                                 width=0.0, fill=color)
                self.create_text(center[0] + int(orbitSize*math.cos(theta+deltaTheta)/2),
                                 center[1] + int(orbitSize*math.sin(theta+deltaTheta)/2
                                           + satelliteSize/2+textOffset),
                                 text=e.name, fill='white', anchor='n')
                self.create_text(center[0] + int(orbitSize*math.cos(theta+deltaTheta)/2),
                                 center[1] + int(orbitSize*math.sin(theta+deltaTheta)/2),
                                 text=' '.join([m.name[:m.name.index('_')] for m in e.modules]),
                                 fill='white', width=satelliteSize)
                data = [d for m in e.modules for d in m.data]
                for d_i, d in enumerate(data):
                    dTheta = d_i*2*math.pi/len(data)-math.pi/2
                    dCenter = (center[0] + int(orbitSize*math.cos(theta+deltaTheta)/2),
                               center[1] + int(orbitSize*math.sin(theta+deltaTheta)/2))
                    dotSize = self.scale*8
                    self.create_rectangle(
                        dCenter[0] + int(math.cos(dTheta)*satelliteSize*7./16) - dotSize/2,
                        dCenter[1] + int(math.sin(dTheta)*satelliteSize*7./16) - dotSize/2,
                        dCenter[0] + int(math.cos(dTheta)*satelliteSize*7./16) + dotSize/2,
                        dCenter[1] + int(math.sin(dTheta)*satelliteSize*7./16) + dotSize/2,
                        fill= 'purple' if d.phenomenon == 'SAR' else 'cyan')
        
        for i, player in enumerate([federate for federation in self.context.federations
                                    for federate in federation.federates]):
            playerOffset = int(5*self.scale)
            textOffset = int(5*self.scale)
            playerSize = (int(180*self.scale), int(100*self.scale))
            text = '{} Cash: {:>8.0f}'.format(player.name, player.cash)
            self.create_rectangle(playerOffset if i==0 or i==2
                                  else self.winfo_reqwidth()-playerOffset-playerSize[0],
                                  playerOffset if i==0 or i==1
                                  else self.winfo_reqheight()-playerOffset-playerSize[1],
                                  playerOffset+playerSize[0] if i==0 or i==2
                                  else self.winfo_reqwidth()-playerOffset,
                                  playerOffset+playerSize[1] if i==0 or i==1
                                  else self.winfo_reqheight()-playerOffset,
                                  fill='black', outline=colors[i])
            self.create_text(playerOffset+textOffset if i==0 or i==2
                             else self.winfo_reqwidth()-playerOffset-playerSize[0]+textOffset,
                             playerOffset+textOffset if i==0 or i==1
                             else self.winfo_reqheight()-playerOffset-playerSize[1]+textOffset,
                             text=text,
                             anchor='nw', width=playerSize[0]-2*textOffset,
                             fill='white', font='-weight bold')

            for c_i, c in enumerate(player.contracts):
                contractSize = self.scale*40
                contractOffset = 5
                cCenter = ((2*c_i+1)*(contractOffset/2+contractSize/2) +
                    (playerOffset if i==0 or i==2
                     else self.winfo_reqwidth()-playerOffset-playerSize[0]),
                    -contractSize/2 - contractOffset - 20 +
                    (playerOffset+playerSize[1] if i==0 or i==1
                     else self.winfo_reqheight()-playerOffset))
                for t in range(c.elapsedTime, 8):
                    self.create_arc(cCenter[0] - contractSize/2,
                                     cCenter[1] - contractSize/2,
                                     cCenter[0] + contractSize/2,
                                     cCenter[1] + contractSize/2,
                                     start=(1-t)*360./8, extent=360./8,
                                     fill='green' if c.demand.getValueAt(t)==c.demand.getValueAt(0)
                                     else 'yellow' if c.demand.getValueAt(t) > 0 else 'red')
                self.create_oval(cCenter[0] - demandSize/4,
                                 cCenter[1] - demandSize/4,
                                 cCenter[0] + demandSize/4,
                                 cCenter[1] + demandSize/4,
                                 fill= 'white')
                dataSize = self.scale*8
                self.create_rectangle(cCenter[0] - dataSize/2,
                                      cCenter[1] - dataSize/2,
                                      cCenter[0] + dataSize/2,
                                      cCenter[1] + dataSize/2,
                                      fill= 'purple' if c.demand.phenomenon == 'SAR' else 'cyan')
                self.create_text(cCenter[0] + int(contractOffset*math.cos(theta)),
                                 cCenter[1] + int(contractOffset*math.sin(theta)
                                           + demandSize/2+textOffset),
                                 text=e.name, fill='black', anchor='n')
                self.create_text(cCenter[0],
                                 cCenter[1] + demandSize/2+textOffset,
                                 text=c.demand.name, fill='white', anchor='n')
                
if __name__ == '__main__':
    elements = '1.MediumSat@MEO6,VIS,SAR,oSGL,oISL 1.MediumSat@MEO5,VIS,SAR,oSGL,oISL 1.LargeSat@MEO4,VIS,SAR,DAT,oSGL,oISL 1.GroundSta@SUR1,oSGL'
    ofs = OFS(elements.split(' '),
        numPlayers=2, ops='n', fops='d6,50,1', initialCash=0, numTurns=None)
    ofs.sim.init()
    
    root = Tk()
    frame = Frame(root)
    frame.pack(fill=BOTH, expand=YES)
    canvas = OFS_GUI(root, ofs)
    canvas.draw()
    
    root.title("Orbital Federates Simulation")
    root.resizable(0,0)
    root.mainloop()