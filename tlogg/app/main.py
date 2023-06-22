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

from TermTk import TTk, TTkK, TTkLog
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkFrame

from tlogg import TloggHelper, tloggProxy

from .cfg  import *
from .glbl import *
from .about import *
from .loggwidget import LoggWidget
from .options import optionsFormLayout, optionsLoadTheme
from .highlighters import highlightersFormLayout
from .predefinedfilters import PredefinedFiltersFormWindow


class TLOGG(TTkGridLayout):
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
    __slots__ = ('_kodeTab', '_tloggProxy')
    def __init__(self, tloggProxy, *args, **kwargs) -> None:
        self._tloggProxy = tloggProxy

        super().__init__(*args, **kwargs)

        self._tloggProxy.setOpenFile(self.openFile)

        self.addWidget(mainSplitter := TTkSplitter(orientation=TTkK.VERTICAL))

        menuFrame = TTkFrame(border=False, maxHeight=1)

        self._kodeTab      = TTkKodeTab(border=False, closable=True)

        fileMenu = menuFrame.newMenubarTop().addMenu("&File")
        buttonOpen    = fileMenu.addMenu("Open")
        buttonClose   = fileMenu.addMenu("Close")
        fileMenu.addSpacer()
        buttonColors  = fileMenu.addMenu("&Colors...")
        buttonFilters = fileMenu.addMenu("&Filters...")
        buttonOptions = fileMenu.addMenu("&Options...")
        fileMenu.addSpacer()
        buttonExit    = fileMenu.addMenu("Exit")
        buttonExit.menuButtonClicked.connect(TTkHelper.quit)

        helpMenu = menuFrame.newMenubarTop().addMenu("&Help", alignment=TTkK.RIGHT_ALIGN)
        helpMenu.addMenu("About ...").menuButtonClicked.connect(self.showAbout)
        helpMenu.addMenu("About tlogg").menuButtonClicked.connect(self.showAboutTlogg)

        def _tabChanged(_,__,widget,data):
            tloggProxy.tloggFocussed.emit(None, data)

        self._kodeTab.currentChanged.connect(_tabChanged)

        # fileTree.fileActivated.connect(lambda x: self.openFile(x.path()))

        buttonOpen.menuButtonClicked.connect(self.openFileCallback)
        buttonColors.menuButtonClicked.connect(self.showColors)
        buttonFilters.menuButtonClicked.connect(self.showFilters)
        buttonOptions.menuButtonClicked.connect(self.showOptions )

        # Defining the layout based on the plugin widget placement
        if (placement:=TloggHelper._getPluginPlacements()) == ttk.TTkK.NONE:
            # If no plugin require a specific placement
            # define a basic layout without side panels
            fileControlLayout = TTkVBoxLayout()
            fileControlLayout.addWidget(menuFrame)
            fileControlLayout.addWidget(self._kodeTab)

            mainSplitter.addWidget(fileControlLayout)
            mainSplitter.addWidget(TTkLogViewer(),3)
        else:
            fileTabSplitter = TTkSplitter(orientation=TTkK.HORIZONTAL)
            fileTabSplitterSizes = []
            fileControlLayout = TTkVBoxLayout()
            fileControlLayout.addWidget(menuFrame)

            # Add left placed plugin first in the splitter
            for mod in TloggHelper._getPlacedPlugins(ttk.TTkK.LEFT):
                if fileControlLayout:
                    fileControlLayout.addWidget(mod.widget)
                    fileTabSplitter.addItem(fileControlLayout)
                    fileControlLayout = None
                else:
                    fileTabSplitter.addWidget(mod.widget)
                fileTabSplitterSizes.append(40)

            fileTabSplitter.addWidget(self._kodeTab)
            fileTabSplitterSizes.append(None)

            # Add left placed plugins at the end in the splitter
            for mod in TloggHelper._getPlacedPlugins(ttk.TTkK.RIGHT):
                if fileControlLayout:
                    fileControlLayout.addWidget(mod.widget)
                    fileTabSplitter.addItem(fileControlLayout)
                    fileControlLayout = None
                else:
                    fileTabSplitter.addWidget(mod.widget)
                fileTabSplitterSizes.append(50)

            fileTabSplitter.setSizes(fileTabSplitterSizes)

            mainSplitter.addWidget(fileTabSplitter)
            mainSplitter.addWidget(TTkLogViewer(),3)


    def openFileCallback(self, btn=None):
        filePicker = TTkFileDialogPicker(
                        pos = (3,3), size=(90,30),
                        caption="Open a File", path=".",
                        filter="All Files (*);;Text Files (*.txt);;Log Files (*.log)")
        filePicker.filePicked.connect(self.openFile)
        TTkHelper.overlay(btn, filePicker, 10, 2, modal=True)

    def showColors(self, btn=None):
        win = TTkWindow(title="Highlighters...", size=(70,20), border=True)
        win.setLayout(highlightersFormLayout(win))
        TTkHelper.overlay(btn, win, 10,2, modal=True)

    def showFilters(self, btn=None):
        win = PredefinedFiltersFormWindow(title="Predefined Filters...", size=(70,20), border=True)
        TTkHelper.overlay(btn, win, 10,2, modal=True)

    def showOptions(self, btn=None):
        win = TTkWindow(title="Options...", size=(70,20), border=True)
        win.setLayout(optionsFormLayout(win))
        TTkHelper.overlay(btn, win, 10,2, modal=True)

        # tab.addTab(highlightersForm(), "-Setup-")
    def showAbout(self, btn=None):
        TTkHelper.overlay(btn, TTkAbout(), 20,5)

    def showAboutTlogg(self, btn=None):
        TTkHelper.overlay(btn, About(), 20,5)

    def openFile(self, file):
        # openedFiles.append(file)
        loggWidget = LoggWidget(file)
        self._kodeTab.addTab(widget=loggWidget, label=os.path.basename(file), data=file)
        self._kodeTab.setCurrentWidget(loggWidget)

def main():
    TloggCfg.pathCfg = appdirs.user_config_dir("tlogg")

    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', help='Full Screen', action='store_true')
    parser.add_argument('-c', help=f'config folder (default: "{TloggCfg.pathCfg}")', default=TloggCfg.pathCfg)
    parser.add_argument('filename', type=str, nargs='*',
                    help='the filename/s')
    args = parser.parse_args()

    # TTkLog.use_default_file_logging()

    TloggCfg.pathCfg = args.c
    TTkLog.debug(f"Config Path: {TloggCfg.pathCfg}")

    TloggCfg.load()

    if 'theme' not in TloggCfg.options:
        TloggCfg.options['theme'] = 'UTF8'
    optionsLoadTheme(TloggCfg.options['theme'])

    TloggHelper._loadPlugins()

    root = TTk(layout=(tlogg:=TLOGG(tloggProxy=tloggProxy)), title="tlogg")

    TloggHelper._runPlugins()

    for file in args.filename:
        tlogg.openFile(file)

    root.mainloop()
