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

import appdirs

from TermTk import *

from TermTk import TTk, TTkK, TTkLog, TTkColor
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkFrame
from TermTk import TColor, TText
from TermTk import TTkAbstractScrollArea, TTkAbstractScrollView

from .cfg  import *
from .glbl import *
from .about import *
from .fileviewer  import *
from .preferences import *

def main():
    TloggCfg.pathCfg = appdirs.user_config_dir("tlogg")

    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', help='Full Screen', action='store_true')
    parser.add_argument('-c', help=f'config folder (default: "{TloggCfg.pathCfg}")', default=TloggCfg.pathCfg)
    parser.add_argument('filename', type=str, nargs='+',
                    help='the filename/s')
    args = parser.parse_args()

    TTkLog.use_default_file_logging()

    TloggCfg.pathCfg = args.c
    TTkLog.debug(f"Config Path: {TloggCfg.pathCfg}")

    TloggCfg.load()

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
    buttonAbout = fileMenu.addMenu("&About...")
    fileMenu.addSpacer()
    buttonExit    = fileMenu.addMenu("Exit")
    buttonExit.menuButtonClicked.connect(lambda _: root.quit())

    def showFilters(btn):
        win = TTkWindow(title="Filters...", size=(70,20), border=True)
        win.setLayout(filtersFormLayout(win))
        TTkHelper.overlay(buttonFilters, win, 0,0)
    buttonFilters.menuButtonClicked.connect(showFilters)

    def showAbout(btn):
        TTkHelper.overlay(buttonFilters, About(), 0,0)
    buttonAbout.menuButtonClicked.connect(showAbout)

    # tab.addTab(preferencesForm(), "-Setup-")

    for file in args.filename:
        tabSplitter = TTkSplitter(orientation=TTkK.VERTICAL)
        tab.addTab(tabSplitter, file)
        topFrame    = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())
        bottomFrame = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())


        # Define the bottom layout widgets
        bottomLayoutSearch = TTkHBoxLayout()
        bls_label_1  = TTkLabel(text=" Text:", maxWidth=6)
        bls_label_2  = TTkLabel(text="Ignore case:", maxWidth=12)
        bls_cb_icase = TTkCheckbox(maxWidth=3, checked=True)
        bls_search   = TTkButton(text="Search", maxWidth=10)
        bls_searchbox  = TTkComboBox(editable=True)
        bls_searchbox.addItems(TloggCfg.searches)
        bls_searchbox.setCurrentIndex(0)

        bottomLayoutSearch.addWidget(bls_label_2)
        bottomLayoutSearch.addWidget(bls_cb_icase)
        bottomLayoutSearch.addWidget(bls_label_1)
        bottomLayoutSearch.addWidget(bls_searchbox)
        bottomLayoutSearch.addWidget(bls_search)

        bottomFrame.layout().addItem(bottomLayoutSearch)

        # Define the main file Viewer
        fileBuffer = TTkFileBuffer(file, 0x100, 0x1000)
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

        def _makeSearch():
            sb = bls_searchbox
            fb = fileBuffer
            cb = bls_cb_icase
            bwp = bottomViewport
            twp = topViewport
            def _search(_=None):
                searchtext = sb.currentText()
                TTkLog.debug(f"{searchtext=}")
                indexes = fb.searchRe(searchtext, ignoreCase=cb.checkState() == TTkK.Checked)
                bwp.searchedIndexes(indexes)
                twp.searchedIndexes(indexes)
                if TloggCfg.searches:
                    x = set(TloggCfg.searches)
                    TTkLog.debug(f"{x}")
                    TloggCfg.searches = list(x)
                    if searchtext in TloggCfg.searches:
                        TloggCfg.searches.remove(searchtext)
                TloggCfg.searches.insert(0, searchtext)
                TloggCfg.searches = TloggCfg.searches[:TloggCfg.maxsearches]
                TloggCfg.save(searches=True,filters=False)
                sb.clear()
                sb.addItems(TloggCfg.searches)
                sb.setCurrentIndex(0)
            return _search

        bls_search.clicked.connect(_makeSearch())
        bls_searchbox.editTextChanged.connect(_makeSearch())

    root.mainloop()
