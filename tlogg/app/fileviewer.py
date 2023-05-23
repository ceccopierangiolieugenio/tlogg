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

from TermTk import *

from TermTk import TTkK
from TermTk import TTkLog
from TermTk import TTkColor
from TermTk import TTkString
from TermTk import TTk
from TermTk import TTkFileBuffer
from TermTk import TTkFrame
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkAbstractScrollArea
from TermTk import TTkAbstractScrollView

from . import TloggCfg

class FileViewer(TTkAbstractScrollView):
    __slots__ = (
        '_fileBuffer', '_indexesMark', '_indexesSearched', '_selected', '_indexing', '_searchRe',
        # Signals
        'selected', 'marked')
    def __init__(self, *args, **kwargs):
        self._indexesMark = []
        self._indexesSearched = []
        self._indexing = None
        self._selected = -1
        self._searchRe = ""
        # Signals
        self.selected = pyTTkSignal(int)
        self.marked = pyTTkSignal(list)
        TTkAbstractScrollView.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'FileViewer' )
        self._fileBuffer = kwargs.get('filebuffer')
        self.viewChanged.connect(self._viewChangedHandler)
        self.setFocusPolicy(TTkK.ClickFocus)


    @pyTTkSlot()
    def _viewChangedHandler(self):
        self.update()

    @pyTTkSlot(float)
    def fileIndexing(self, percentage):
        self._indexing = percentage
        self.viewChanged.emit()

    @pyTTkSlot()
    def fileIndexed(self):
        self._indexing = None
        self.viewChanged.emit()

    def markIndexes(self, indexes):
        self._indexesMark = indexes
        self.viewChanged.emit()

    def searchedIndexes(self, indexes):
        self._indexesSearched = indexes
        self.viewChanged.emit()

    def searchRe(self, searchRe):
        self._searchRe = searchRe
        self.update()

    def viewFullAreaSize(self) -> (int, int):
        w = 10+self._fileBuffer.getWidth()
        h = self._fileBuffer.getLen()
        return ( w , h )

    def viewDisplayedSize(self) -> (int, int):
        return self.size()

    def mousePressEvent(self, evt):
        x,y = evt.x, evt.y
        ox,oy = self.getViewOffsets()
        index = oy+y
        if oy+y<self._fileBuffer.getLen():
            if x<3:
                if index in self._indexesMark:
                    self._indexesMark.pop(self._indexesMark.index(index))
                else:
                    self._indexesMark.append(index)
                self.marked.emit(self._indexesMark)
            else:
                self._selected = index
                self.selected.emit(self._selected)
            self.update()
            return True
        return False

    @pyTTkSlot(int)
    def selectAndMove(self, line):
        self._selected = line
        ox,_ = self.getViewOffsets()
        self.viewMoveTo(ox, max(0,line-self.height()//2))
        self.update()

    def getLen(self):
        return self._fileBuffer.getLen()

    def getLine(self, num) -> str:
        return self._fileBuffer.getLine(num)

    def getLineNum(self, num) -> int:
        return num

    def paintEvent(self, canvas):
        ox,oy = self.getViewOffsets()
        bufferLen = self.getLen()
        for i in range(min(self.height(),bufferLen-oy)):
            line = TTkString(self.getLine(i+oy).replace('\n','')).tab2spaces()
            lineNum = self.getLineNum(i+oy)
            if lineNum in self._indexesMark:
                symbolcolor = TTkColor.fg("#00ffff")
                numberColor = TTkColor.bg("#444444")
                symbol='❥'
            elif lineNum in self._indexesSearched:
                symbolcolor = TTkColor.fg("#ff0000")
                numberColor = TTkColor.bg("#444444")
                symbol='●'
            else:
                symbolcolor = TTkColor.fg("#0000ff")
                numberColor = TTkColor.bg("#444444")
                symbol='○'

            if i+oy == self._selected:
                selectedColor = TTkColor.bg("#008844")
                searchedColor = TTkColor.fg("#FFFF00")+TTkColor.bg("#004400")
                line = line.setColor(selectedColor)
            else:
                selectedColor = TTkColor.RST
                searchedColor = TTkColor.fg("#000000")+TTkColor.bg("#AAAAAA")
                # Check in the filters a matching color
                for color in TloggCfg.colors:
                    #TTkLog.debug(f"{color['pattern']} - {line}")
                    if m := line.findall(regexp=color['pattern']):
                        selectedColor = TTkColor.fg(color['fg'])+TTkColor.bg(color['bg'])
                        searchedColor = TTkColor.fg(color['bg'])+TTkColor.bg(color['fg'])
                        line = line.setColor(selectedColor)
                        break
            if self._searchRe:
                if m := line.findall(regexp=self._searchRe, ignoreCase=True):
                    for match in m:
                        line = line.setColor(searchedColor, match=match)

            # Add Line Number
            lenLineNumber = len(str(self.getLineNum(bufferLen-1)))
            lineNumber = TTkString() + numberColor + str(lineNum).rjust(lenLineNumber) + TTkColor.RST + ' '
            # Compose print line
            printLine = TTkString() + symbolcolor + symbol + TTkColor.RST + ' ' + lineNumber + line.substring(ox)
            canvas.drawText(pos=(0,i), text=printLine, color=selectedColor, width=self.width(), )

        # Draw the loading banner
        if self._indexing is not None:
            canvas.drawText(pos=(0,0), text=f" [ Indexed: {int(100*self._indexing)}% ] ")

class FileViewerSearch(FileViewer):
    __slots__ = ('_indexes')
    def __init__(self, *args, **kwargs):
        self._indexes = []
        FileViewer.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'FileViewerSearch' )

    def markIndexes(self, indexes):
        self._indexesMark = indexes
        self._indexes = [i for i in sorted(set(self._indexesSearched+self._indexesMark))]
        ox,oy = self.getViewOffsets()
        self.viewMoveTo(ox,oy)
        self.update()

    def searchedIndexes(self, indexes):
        # Get the current lineSelected to be used to scroll
        # the search viewer to the similar to previous position
        lineSelected = -1
        if self._selected > -1:
            lineSelected = self._indexes[self._selected]

        self._indexesSearched = indexes
        self._indexes = [i for i in sorted(set(self._indexesSearched+self._indexesMark))]
        ox,_ = self.getViewOffsets()

        lineToMove = 0
        if lineSelected > -1:
            for i, lineNum in enumerate(self._indexes):
                if lineNum >= lineSelected:
                   if lineNum == lineSelected:
                       self._selected = i
                   else:
                       self._selected = -1
                   # Try to keep the  selected area at the center of the widget
                   lineToMove = i if i <= self.height()/2 else int(i-self.height()/2)
                   break

        self.viewMoveTo(ox, lineToMove)
        self.update()

    def viewFullAreaSize(self) -> (int, int):
        if self._indexes is None:
            w = 2+self._fileBuffer.getWidth()
            h = self._fileBuffer.getLen()
        else:
            w = 2+self._fileBuffer.getWidth(self._indexes)
            h = len(self._indexes)
        return w , h

    def mousePressEvent(self, evt):
        x,y = evt.x, evt.y
        ox,oy = self.getViewOffsets()
        index = oy+y
        if index<len(self._indexes):
            if x<3:
                index = self._indexes[oy+y]
                if index in self._indexesMark:
                    self._indexesMark.pop(self._indexesMark.index(index))
                else:
                    self._indexesMark.append(index)
                self.markIndexes(self._indexesMark)
                self.marked.emit(self._indexesMark)
            else:
                self._selected = index
                self.selected.emit(self._indexes[self._selected])
            self.update()
            return True
        return False

    def getLen(self):
        return len(self._indexes)

    def getLine(self, num) -> str:
        return self._fileBuffer.getLine(self._indexes[num])

    def getLineNum(self, num) -> int:
        return self._indexes[num]

class FileViewerArea(TTkAbstractScrollArea):
    __slots__ = ('_fileView')
    def __init__(self, *args, **kwargs):
        TTkAbstractScrollArea.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'FileViewer' )
        if 'parent' in kwargs: kwargs.pop('parent')
        self._fileView = kwargs.get('fileView')
        self.setFocusPolicy(TTkK.ClickFocus)
        self.setViewport(self._fileView)
