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

class TloggCfg:
    version="__VERSION__"
    name="__NAME__"
    filters=[
        #{'pattern':"Fill",    'ignorecase':False, 'fg':"#00FFFF", 'bg':"#444400" },
        {'pattern':"tempor",  'ignorecase':False, 'fg':"#FFFF00", 'bg':"#004444" },
        {'pattern':"ullamco", 'ignorecase':True,  'fg':"#00FF00", 'bg':"#440044" },
        {'pattern':"amet",    'ignorecase':False, 'fg':"#0088FF", 'bg':"#444400" },
        #{'pattern':"minim",   'ignorecase':False, 'fg':"#888800", 'bg':"#222222" },
        #{'pattern':"veniam",  'ignorecase':False, 'fg':"#aaaa00", 'bg':"#004444" },
        #{'pattern':"ipsum",   'ignorecase':False, 'fg':"#00ffff", 'bg':"#440000" },
        #{'pattern':"labore",  'ignorecase':False, 'fg':"#0000AA", 'bg':"#FFFF00" },
        {'pattern':"\.venv",  'ignorecase':False, 'fg':"#00FFFF", 'bg':"#444400" },
        {'pattern':"python",  'ignorecase':False, 'fg':"#FFFF00", 'bg':"#004444" },
        {'pattern':"deploy",  'ignorecase':False, 'fg':"#FF00FF", 'bg':"#440044" },
    ]

