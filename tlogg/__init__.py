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
import sys
import argparse

import os
import re
import sys
import argparse

from TermTk import *

from TermTk import TTk, TTkK, TTkLog, TTkColor
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkFrame
from TermTk import TColor, TText
from TermTk import TTkAbstractScrollArea, TTkAbstractScrollView

from .app import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Full Screen', action='store_true')
    parser.add_argument('filename', type=str, nargs='+',
                    help='the filename')
    args = parser.parse_args()

    TTkLog.use_default_file_logging()

    root = TTk(layout=TTkGridLayout())
    splitter = TTkSplitter(parent=root, orientation=TTkK.VERTICAL)
    tab = TTkTabWidget(parent=splitter, border=False)
    # tab = TTkTabWidget(parent=splitter, border=True)
    splitter.addWidget(TTkLogViewer(),3)


    fileMenu = tab.addMenu("[&File]")
    buttonOpen    = fileMenu.addMenu("Open")
    buttonClose   = fileMenu.addMenu("Close")
    fileMenu.addSpacer()
    buttonFilters = fileMenu.addMenu("&Filters...")
    fileMenu.addSpacer()
    buttonExit    = fileMenu.addMenu("Exit")
    buttonExit.menuButtonClicked.connect(lambda _: root.quit())

    def showFilters(btn):
        win = TTkWindow(title="Filters...", size=(70,20), border=True)
        win.setLayout(filtersFormLayout(win))
        TTkHelper.overlay(buttonFilters, win, 0,0)
    buttonFilters.menuButtonClicked.connect(showFilters)

    # tab.addTab(preferencesForm(), "-Setup-")

    for file in args.filename:
        tabSplitter = TTkSplitter(orientation=TTkK.VERTICAL)
        tab.addTab(tabSplitter, file)
        topFrame    = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())
        bottomFrame = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())


        # Define the bottom layout widgets
        bottomLayoutSearch = TTkHBoxLayout()
        bls_label_1  = TTkLabel(text=" Text:", maxWidth=6)
        bls_textbox  = TTkLineEdit()
        bls_label_2  = TTkLabel(text="Ignore case:", maxWidth=12)
        bls_cb_icase = TTkCheckbox(maxWidth=3)
        bls_search   = TTkButton(text="Search", maxWidth=10)

        bottomLayoutSearch.addWidget(bls_label_2)
        bottomLayoutSearch.addWidget(bls_cb_icase)
        bottomLayoutSearch.addWidget(bls_label_1)
        bottomLayoutSearch.addWidget(bls_textbox)
        bottomLayoutSearch.addWidget(bls_search)

        bottomFrame.layout().addItem(bottomLayoutSearch)

        # Define the main file Viewer
        fileBuffer = TTkFileBuffer(file, 0x1000, 0x10)
        topViewport = FileViewer(filebuffer=fileBuffer)
        topViewer = FileViewerArea(parent=topFrame, fileView=topViewport)
        fileBuffer.indexUpdated.connect(topViewport.fileIndexing)
        fileBuffer.indexed.connect(topViewport.fileIndexed)
        # Define the Search Viewer
        bottomViewport = FileViewerSearch(filebuffer=fileBuffer)
        bottomViewer = FileViewerArea(parent=bottomFrame, fileView=bottomViewport)
        bottomViewport.selected.connect(topViewport.selectAndMove)
        bottomViewport.marked.connect(topViewport.markIndexes)
        topViewport.marked.connect(bottomViewport.markIndexes)

        # Add those viewpoers to the global list to allow dynamic refresh
        # TODO: Try to get rid of this
        TloggGlbl.addRefView(topViewport)
        TloggGlbl.addRefView(bottomViewport)

        class _search:
            def __init__(self,tb,fb,cb,tvp,bvp):
                self.tb=tb
                self.fb=fb
                self.cb=cb
                self.tvp=tvp
                self.bvp=bvp
            def search(self):
                searchtext = self.tb.text()
                indexes = self.fb.searchRe(searchtext, ignoreCase=self.cb.checkState() == TTkK.Checked)
                self.bvp.searchedIndexes(indexes)
                self.tvp.searchedIndexes(indexes)
        _s = _search(bls_textbox,fileBuffer,bls_cb_icase,topViewport,bottomViewport)
        bls_search.clicked.connect(_s.search)
        bls_textbox.returnPressed.connect(_s.search)


    root.mainloop()

if __name__ == "__main__":
    main()