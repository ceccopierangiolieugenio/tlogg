#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import yaml

class TloggCfg:
    version="__VERSION__"
    name="__NAME__"
    pathCfg="."
    filters=[]
    maxsearches=200
    searches=[]

    @staticmethod
    def save(searches=True,filters=True):
        os.makedirs(TloggCfg.pathCfg, exist_ok=True)
        filtersPath  = os.path.join(TloggCfg.pathCfg,'filters.yaml')
        searchesPath = os.path.join(TloggCfg.pathCfg,'searches.yaml')
        if filters:
            with open(filtersPath, 'w') as f:
                yaml.dump(TloggCfg.filters, f, sort_keys=False, default_flow_style=False)
        if searches:
            with open(searchesPath, 'w') as f:
                yaml.dump(TloggCfg.searches, f, sort_keys=False, default_flow_style=False)

    @staticmethod
    def load():
        filtersPath = os.path.join(TloggCfg.pathCfg,'filters.yaml')
        searchesPath = os.path.join(TloggCfg.pathCfg,'searches.yaml')
        if not os.path.exists(filtersPath): return
        with open(filtersPath) as f:
            TloggCfg.filters = yaml.load(f, Loader=yaml.SafeLoader)
        if not os.path.exists(searchesPath): return
        with open(searchesPath) as f:
            TloggCfg.searches = yaml.load(f, Loader=yaml.SafeLoader)
