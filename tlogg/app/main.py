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

from TermTk import TTk, TTkK, TTkLog, TTkColor, TTkTheme
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkFrame
from TermTk import TTkAbstractScrollArea, TTkAbstractScrollView
from TermTk import TTkFileDialogPicker
from TermTk import TTkFileTree

from .cfg  import *
from .glbl import *
from .about import *
from .fileviewer  import *
from .filetree import FileTree
from .options import optionsFormLayout, optionsLoadTheme
from .highlighters import highlightersFormLayout
from .predefinedfilters import PredefinedFiltersFormWindow, PredefinedFilters

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

    '''
        ┌──────────────────[Main Splitter]─────────┐
        │┌──────────╥────[File Tab Splitter]──────┐│
        ││ F.Tree   ║       Tab                   ││
        ││ Controls ╟─────────────────────────────┤│
        │├──────────╢┌───────────────────────────┐││
        ││ File     ║│   File Viewer             │││
        ││ Tree     ║│                           │││
        ││          ║╞═══════════════════════════╡││
        ││          ║│   Search Widget           │││
        ││          ║│                           │││
        ││          ║└───────────────────────────┘││
        │└──────────╨─────────────────────────────┘│
        ╞══════════════════════════════════════════╡
        │ Logger,Debug View                        │
        └──────────────────────────────────────────┘
    '''
    if 'theme' not in TloggCfg.options:
        TloggCfg.options['theme'] = 'UTF8'
    optionsLoadTheme(TloggCfg.options['theme'])

    root = TTk(layout=TTkGridLayout(), title="tlogg")
    mainSplitter    = TTkSplitter(parent=root, orientation=TTkK.VERTICAL)
    fileTabSplitter = TTkSplitter(parent=mainSplitter, orientation=TTkK.HORIZONTAL)
    fileTree = FileTree(parent=fileTabSplitter)
    tab      = TTkTabWidget(parent=fileTabSplitter, border=False)
    fileTabSplitter.setSizes([20,100])
    # tab = TTkTabWidget(parent=fileTabSplitter, border=True)
    mainSplitter.addWidget(TTkLogViewer(),3)


    fileMenu = tab.addMenu("&File")
    buttonOpen    = fileMenu.addMenu("Open")
    buttonClose   = fileMenu.addMenu("Close")
    fileMenu.addSpacer()
    buttonColors  = fileMenu.addMenu("&Colors...")
    buttonFilters = fileMenu.addMenu("&Filters...")
    buttonOptions = fileMenu.addMenu("&Options...")
    fileMenu.addSpacer()
    buttonAbout = fileMenu.addMenu("&About...")
    fileMenu.addSpacer()
    buttonExit    = fileMenu.addMenu("Exit")
    buttonExit.menuButtonClicked.connect(lambda _: root.quit())

    openedFiles = []

    def _tabChanged(index):
        fileTree.follow(openedFiles[index])

    tab.currentChanged.connect(_tabChanged)

    def openFile(file):
        openedFiles.append(file)
        tabSplitter = TTkSplitter(orientation=TTkK.VERTICAL)
        tab.addTab(tabSplitter, os.path.basename(file))
        tab.setCurrentWidget(tabSplitter)
        topFrame    = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())
        bottomFrame = TTkFrame(parent=tabSplitter, border=False, layout=TTkVBoxLayout())


        # Define the bottom layout widgets
        bottomLayoutSearch = TTkHBoxLayout()
        btn_filters   = TTkButton(text="Filters ^", maxWidth=11)
        bls_label_1   = TTkLabel(text=" Txt:", maxWidth=5)
        bls_cb_icase  = TTkCheckbox(text="Aa", maxWidth=5, checked=True)
        bls_search    = TTkButton(text="Search", maxWidth=10)
        bls_searchbox = TTkComboBox(editable=True)
        bls_searchbox.addItems(TloggCfg.searches)
        bls_searchbox.setCurrentIndex(0)

        bottomLayoutSearch.addWidget(btn_filters)
        bottomLayoutSearch.addWidget(bls_label_1)
        bottomLayoutSearch.addWidget(bls_searchbox)
        bottomLayoutSearch.addWidget(bls_cb_icase)
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
                searchtext = str(sb.currentText())
                TTkLog.debug(f"{searchtext=}")
                indexes = fb.searchRe(searchtext, ignoreCase=cb.checkState() == TTkK.Checked)
                bwp.searchedIndexes(indexes)
                bwp.searchRe(searchtext)
                twp.searchedIndexes(indexes)
                twp.searchRe(searchtext)
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

        def _openPredefinedFilters():
            TTkHelper.overlay(btn_filters, PredefinedFilters(bls_searchbox), -2, 1)
        btn_filters.clicked.connect(_openPredefinedFilters)

    for file in args.filename:
        openFile(file)

    fileTree.fileActivated.connect(lambda x: openFile(x.path()))

    def openFileCallback(btn):
        filePicker = TTkFileDialogPicker(
                        pos = (3,3), size=(90,30),
                        caption="Open a File", path=".",
                        filter="All Files (*);;Text Files (*.txt);;Log Files (*.log)")
        filePicker.filePicked.connect(openFile)
        TTkHelper.overlay(tab, filePicker, 2, 1, modal=True)
    buttonOpen.menuButtonClicked.connect(openFileCallback)

    def showColors(btn):
        win = TTkWindow(title="Highlighters...", size=(70,20), border=True)
        win.setLayout(highlightersFormLayout(win))
        TTkHelper.overlay(buttonColors, win, 0,0, modal=True)
    buttonColors.menuButtonClicked.connect(showColors)

    def showFilters(btn):
        win = PredefinedFiltersFormWindow(title="Predefined Filters...", size=(70,20), border=True)
        TTkHelper.overlay(buttonColors, win, 0,0, modal=True)
    buttonFilters.menuButtonClicked.connect(showFilters)

    def showOptions(btn):
        win = TTkWindow(title="Options...", size=(70,20), border=True)
        win.setLayout(optionsFormLayout(win))
        TTkHelper.overlay(buttonOptions, win, 0,0, modal=True)
    buttonOptions.menuButtonClicked.connect(showOptions )

    def showAbout(btn):
        TTkHelper.overlay(buttonColors, About(), 0,0)
    buttonAbout.menuButtonClicked.connect(showAbout)

    # tab.addTab(highlightersForm(), "-Setup-")

    root.mainloop()
