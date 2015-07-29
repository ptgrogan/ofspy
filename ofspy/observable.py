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
Observable class.
"""

class Observable(object):
    def __init__(self):
        self._handlers = {}
    
    def trigger(self, events, *args):
        for event in events.split(' '):
            if event in self._handlers:
                for handler in self._handlers[event]:
                    handler(*args)
                
    def on(self, events, handler):
        for event in events.split(' '):
            if event not in self._handlers:
                self._handlers[event] = []
            self._handlers[event].append(handler)
    
    def off(self, events, handler):
        for event in events.split(' '):
            if event in self.handler:
                self._handlers[event].remove(handler)