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
import re
import sys, os
import random

from . import TloggCfg
from TermTk import *

def filtersFormLayout(win):
    '''
    This form is inspired by glogg "Filters..." form
    '''

    leftRightLayout = TTkHBoxLayout()
    leftLayout        = TTkGridLayout()
    rightLayout       = TTkGridLayout()
    bottomRightLayout = TTkGridLayout()
    leftRightLayout.addItem(leftLayout)
    leftRightLayout.addItem(rightLayout)

    frameFilters = TTkFrame(border=True, layout=TTkGridLayout())
    leftLayout.addWidget(frameFilters,0,0,1,5)

    listFilters = TTkList(parent=frameFilters)

    addButton    = TTkButton(text="+",maxWidth=3)
    removeButton = TTkButton(text="-",maxWidth=3)
    upButton     = TTkButton(text="▲",maxWidth=3)
    downButton   = TTkButton(text="▼",maxWidth=3)

    leftLayout.addWidget(addButton       ,1,0)
    leftLayout.addWidget(removeButton    ,1,1)
    leftLayout.addWidget(TTkSpacer() ,1,2)
    leftLayout.addWidget(upButton        ,1,3)
    leftLayout.addWidget(downButton      ,1,4)

    rightLayout.addWidget(TTkLabel(text="Pattern:"),0,0)
    rightLayout.addWidget(pattern:=TTkLineEdit(text='Test|Test'),0,1)
    rightLayout.addWidget(TTkLabel(text="Ignore Case:"),1,0)
    rightLayout.addWidget(ignoreCase:=TTkCheckbox(),1,1)
    rightLayout.addWidget(TTkLabel(text="FG Color:"),2,0)
    rightLayout.addWidget(fgColor := TTkColorButtonPicker(border=False, color=TTkColor.fg('#ff0000') ),2,1)
    rightLayout.addWidget(TTkLabel(text="BG Color:"),3,0)
    rightLayout.addWidget(bgColor := TTkColorButtonPicker(border=False, color=TTkColor.bg('#ffff00') ),3,1)
    rightLayout.addWidget(TTkSpacer() ,4,0,1,2)

    rightLayout.addItem(bottomRightLayout ,5,0,1,2)
    bottomRightLayout.addWidget(applyBtn  := TTkButton(text="Apply",  border=True, maxHeight=3),0,1)
    bottomRightLayout.addWidget(cancelBtn := TTkButton(text="Cancel", border=True, maxHeight=3),0,2)
    bottomRightLayout.addWidget(okBtn     := TTkButton(text="OK",     border=True, maxHeight=3),0,3)

    okBtn.clicked.connect(win.close)
    cancelBtn.clicked.connect(win.close)

    @ttk.pyTTkSlot(TTkWidget)
    def _listCallback(item):
        if filter:=item.data:
            pattern.setText(filter['pattern'])
            ignoreCase.setCheckState(TTkK.Checked if filter['ignorecase'] else TTkK.Unchecked)
            fgColor.setColor(TTkColor.bg(filter['fg']))
            bgColor.setColor(TTkColor.bg(filter['bg']))

    listFilters.itemClicked.connect(_listCallback)

    for i,filter in enumerate(TloggCfg.filters):
        # ali = TTkAbstractListItem(text=filter['pattern'],data=filter)
        listFilters.addItem(item=filter['pattern'],data=filter)

    return leftRightLayout

def preferencesForm(root=None):
    preferencesLayout = TTkGridLayout(columnMinWidth=1)
    frame = TTkFrame(parent=root, layout=preferencesLayout, border=0)

    frameFilters = TTkFrame(border=True, title="Filters...", layout=filtersFormLayout())
    preferencesLayout.addWidget(frameFilters,0,0)

    return frame