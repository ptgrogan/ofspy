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

import os
import pkg_resources
from Tkinter import *
from PIL import Image, ImageTk

from .canvas import CanvasOFS


class FrameOFS(Frame):
    def __init__(self, root, ofs=None):
        Frame.__init__(self, root)
        self.pack(fill=BOTH, expand=YES)
        
        canvas = CanvasOFS(root, ofs)
        canvas.draw()
        
        root.title("Orbital Federates Simulation")
        if "nt" == os.name:
            root.wm_iconbitmap(
                bitmap = pkg_resources.resource_filename(
                    __name__, 'resources/ofs.ico'))
        else:
            root.wm_iconbitmap(
                bitmap = pkg_resources.resource_filename(
                    __name__, '@resources/ofs.xbm'))
        root.resizable(0,0)