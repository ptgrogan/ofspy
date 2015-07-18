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
Data class.
"""

class Data(object):
    def __init__(self, phenomenon, size, contract=None):
        """
        @param phenomenon: the phenomenon of this data
        @type phenomenon: L{string}
        @param size: the size of this data
        @type size: L{int}
        @param contractId: the contract for this data
        @type contractId: L{string}
        """
        self.phenomenon = phenomenon
        self.size = size
        self.contract = contract