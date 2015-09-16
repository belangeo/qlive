#!/usr/bin/env python
# encoding: utf-8
import wx, os, shutil, weakref, copy
import wx.grid as gridlib
from pyo import sndinfo
from constants import *
import QLiveLib
from AutomationWindow import AutomationWindow

class SoundFileObject:
    def __init__(self, id, filename, loopmode=0, transpo=1, gain=0,
                 playing=0, directout=True, startpoint=0,
                 endpoint=-1, crossfade=5, channel=0):
        self.id = id
        self.filename = filename
        sndfolder = os.path.join(QLiveLib.getVar("projectFolder"), "sounds")        
        info = sndinfo(os.path.join(sndfolder, self.filename))
        if info is None:
            self.valid = False
            self.duration = -1
            self.sndchnls = -1
        else:
            self.valid = True
            self.duration = info[1]
            self.sndchnls = info[3]
        self.loopmode = loopmode
        self.transpo = transpo
        self.gain = gain
        self.playing = playing
        self.directout = directout
        self.startpoint = startpoint
        self.endpoint = self.duration
        self.crossfade = crossfade
        self.channel = channel
        self.transpox = 0.01
        self.gainx = 0.01

        self.showInterp = 0
        
        self.playerRef = None
        self.transpoAutoWindow = None
        self.gainAutoWindow = None

        self.currentCue = 0
        self.cues = {}
        self.saveCue()

    def setPlayerRef(self, obj):
        if obj is None:
            self.playerRef = None
        else:
            self.playerRef = weakref.ref(obj)

    def openTranspoAutomationWindow(self):
        parent = QLiveLib.getVar("MainWindow")
        title = "Transpo Automations on Soundfile %d" % (self.id+1)
        self.transpoAutoWindow = AutomationWindow(parent, title, self)

    def openGainAutomationWindow(self):
        parent = QLiveLib.getVar("MainWindow")
        title = "Gain Automations on Soundfile %d" % (self.id+1)
        self.gainAutoWindow = AutomationWindow(parent, title, self)

    def setShowInterp(self, x):
        self.showInterp = x

    def getShowInterp(self):
        return self.showInterp

    def getAttributes(self):
        return {
                ID_COL_FILENAME: self.filename, 
                ID_COL_LOOPMODE: self.loopmode, 
                ID_COL_TRANSPO: self.transpo, 
                ID_COL_GAIN: self.gain, 
                ID_COL_PLAYING: self.playing, 
                ID_COL_DIRECTOUT: self.directout,
                ID_COL_STARTPOINT: self.startpoint, 
                ID_COL_ENDPOINT: self.endpoint, 
                ID_COL_CROSSFADE: self.crossfade,
                ID_COL_CHANNEL: self.channel,
                ID_COL_TRANSPOX: self.transpox,
                ID_COL_GAINX: self.gainx
                }

    def setAttributes(self, dict):
        self.filename = dict[ID_COL_FILENAME]
        self.loopmode = dict[ID_COL_LOOPMODE]
        self.transpo = dict[ID_COL_TRANSPO]
        self.gain = dict[ID_COL_GAIN]
        self.playing = dict[ID_COL_PLAYING]
        self.directout = dict[ID_COL_DIRECTOUT]
        self.startpoint = dict[ID_COL_STARTPOINT]
        self.endpoint = dict[ID_COL_ENDPOINT]
        self.crossfade = dict[ID_COL_CROSSFADE]
        self.channel = dict[ID_COL_CHANNEL]
        self.transpox = dict.get(ID_COL_TRANSPOX, 0.01)
        self.gainx = dict.get(ID_COL_GAINX, 0.01)

    def copy(self, obj):
        self.setAttributes(copy.deepcopy(obj.getAttributes()))
        self.currentCue = obj.getCurrentCue()
        self.setCues(copy.deepcopy(obj.getCues()))

    def setCurrentCue(self, x):
        self.currentCue = x

    def getCurrentCue(self):
        return self.currentCue

    def loadCue(self, x):
        if x in self.cues:
            self.setAttributes(self.cues[x])
        else:
            c = x
            while (c >= 0):
                if c in self.cues:
                    self.setAttributes(self.cues[c])
                    break
                c -= 1
        self.currentCue = x
        if self.playerRef is not None:
            player = self.playerRef()
            player.setAttributes(self.getAttributes())

    def delCue(self, x):
        del self.cues[x]
        for i in range(x+1, len(self.cues)):
            if i in self.cues:
                self.cues[i-1] = self.cues[i]
                del self.cues[i]

    def saveCue(self):
        self.cues[self.currentCue] = self.getAttributes()

    def addCue(self, x):
        self.currentCue = x
        self.saveCue()

    def getCues(self):
        return self.cues

    def setCues(self, cues):
        self.cues = cues

    def setGlobalInterpTime(self, value, allcues):
        if allcues:
            for key in self.cues.keys():
                self.cues[key][ID_COL_TRANSPOX] = value
                self.cues[key][ID_COL_GAINX] = value
        else:
            self.cues[self.currentCue][ID_COL_TRANSPOX] = value
            self.cues[self.currentCue][ID_COL_GAINX] = value
        self.transpox = self.gainx = value

    def isValid(self):
        return self.valid

    def getChnls(self):
        return self.sndchnls

    def getId(self):
        return self.id

    def setId(self, x):
        self.id = x

    def setPlayerAttribute(self, id, value):
        if self.playerRef is not None:
            player = self.playerRef()
            player.setAttribute(id, value)
        
    def getFilename(self):
        return self.filename

    def setLoopMode(self, x):
        self.loopmode = x
        self.setPlayerAttribute(ID_COL_LOOPMODE, x)

    def getTranspo(self):
        return self.transpo
        
    def setTranspo(self, x):
        self.transpo = x
        self.setPlayerAttribute(ID_COL_TRANSPO, x)

    def getTranspox(self):
        return self.transpox
        
    def setTranspox(self, x):
        self.transpox = x
        self.setPlayerAttribute(ID_COL_TRANSPOX, x)

    def getGain(self):
        return self.gain

    def setGain(self, x):
        self.gain = x
        self.setPlayerAttribute(ID_COL_GAIN, x)

    def getGainx(self):
        return self.gainx

    def setGainx(self, x):
        self.gainx = x
        self.setPlayerAttribute(ID_COL_GAINX, x)

    def getPlaying(self):
        return self.playing

    def setPlaying(self, x):
        self.playing = x
        self.setPlayerAttribute(ID_COL_PLAYING, x)

    def getDirectOut(self):
        return self.directout

    def setDirectOut(self, x):
        self.directout = x
        self.setPlayerAttribute(ID_COL_DIRECTOUT, x)

    def getStartPoint(self):
        return self.startpoint

    def setStartPoint(self, x):
        self.startpoint = x
        self.setPlayerAttribute(ID_COL_STARTPOINT, x)

    def getEndPoint(self):
        return self.endpoint

    def setEndPoint(self, x):
        self.endpoint = x
        self.setPlayerAttribute(ID_COL_ENDPOINT, x)

    def getCrossfade(self):
        return self.crossfade

    def setCrossfade(self, x):
        self.crossfade = x
        self.setPlayerAttribute(ID_COL_CROSSFADE, x)

    def getDuration(self):
        return self.duration

    def setChannel(self, x):
        self.channel = x
        self.setPlayerAttribute(ID_COL_CHANNEL, x)

    def getChannel(self):
        return self.channel

class GridFileDropTarget(wx.FileDropTarget):
    def __init__(self, grid):
        wx.FileDropTarget.__init__(self)
        self.grid = grid

    def OnDropFiles(self, x, y, filenames):
        x, y = self.grid.CalcUnscrolledPosition(x, y)
        col = self.grid.XToCol(x)
        row = self.grid.YToRow(y)
        if row > -1 and col == ID_COL_FILENAME:
            filename = filenames[0]
            if sndinfo(filename) is not None:
                self.grid.copyToSoundsFolder(filename)
                self.grid.setSelRow(row)
                self.grid.loadSound(os.path.basename(filename))

class SoundFileGrid(gridlib.Grid):
    def __init__(self, parent):
        super(SoundFileGrid, self).__init__(parent, style=wx.SUNKEN_BORDER)

        self.selRow = self.selCol = -1
        self.objects = []
        
        self.setInitialValuesToNone()

        self.textColour = self.GetDefaultCellTextColour()
        self.SetColLabelAlignment(wx.CENTER, wx.CENTER)
        self.SetCellHighlightColour("#CCCCCC")
        self.SetCellHighlightPenWidth(0)
        self.SetCellHighlightROPenWidth(0)
        self.SetSelectionBackground("#FFFFFF")
        self.SetSelectionForeground("#000000")
        self.font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, face="Monospace")
        self.SetRowLabelSize(50)

        dropTarget = GridFileDropTarget(self)
        self.SetDropTarget(dropTarget)

        self.CreateGrid(0, 10)

        for i, label in enumerate(LABELS):
            self.SetColMinimalWidth(i, COLSIZES[i])
            self.SetColSize(i, COLSIZES[i])
            self.SetColLabelValue(i, label)

        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnCellEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnCellEditorShown)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.GetGridWindow().Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMotion)
        self.GetGridWindow().Bind(wx.EVT_SIZE, self.OnSize)

        self.addRow()

    def setSelRow(self, row):
        self.selRow = row

    def copyToSoundsFolder(self, path):
        sndfolder = os.path.join(QLiveLib.getVar("projectFolder"), "sounds")
        shutil.copy(path, sndfolder)

    def OnSize(self, evt):
        w, _ = self.GetGridWindow().GetClientSize()
        sz = w - (sum(COLSIZES) - COLSIZES[0])
        if sz >= COLSIZES[0]:
            self.SetColSize(0, sz)
        evt.Skip()

    def setInitialValuesToNone(self):
        self.clickPosition = self.initialTranspo = self.initialGain = None
        self.initialStart = self.initialEnd = self.initialFade = None
        self.initialChannel = None

    def addRow(self, index=None):
        if index == None:
            self.AppendRows(1, True)
            row = self.GetNumberRows() - 1
        else:
            self.InsertRows(index, 1, True)
            row = index
        # Filename
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_FILENAME, attr)
        renderer = gridlib.GridCellAutoWrapStringRenderer()
        self.SetCellRenderer(row, ID_COL_FILENAME, renderer)
        self.SetCellValue(row, ID_COL_FILENAME, "Click to choose a sound")
        self.SetCellTextColour(row, ID_COL_FILENAME, "#888888")
        # Loop Mode
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_LOOPMODE, attr)
        # Transpo
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_TRANSPO, attr)
        rd = gridlib.GridCellFloatRenderer()
        rd.SetPrecision(4)
        self.SetCellRenderer(row, ID_COL_TRANSPO, rd)
        # Gain
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_GAIN, attr)
        rd = gridlib.GridCellFloatRenderer()
        rd.SetPrecision(4)
        self.SetCellRenderer(row, ID_COL_GAIN, rd)
        # Playing
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_PLAYING, attr)
        # Direct Out
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_DIRECTOUT, attr)
        # Start Point
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_STARTPOINT, attr)
        rd = gridlib.GridCellFloatRenderer()
        rd.SetPrecision(4)
        self.SetCellRenderer(row, ID_COL_STARTPOINT, rd)
        # End Point
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_ENDPOINT, attr)
        rd = gridlib.GridCellFloatRenderer()
        rd.SetPrecision(4)
        self.SetCellRenderer(row, ID_COL_ENDPOINT, rd)
        # Crossfade
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_CROSSFADE, attr)
        rd = gridlib.GridCellFloatRenderer()
        rd.SetPrecision(1)
        self.SetCellRenderer(row, ID_COL_CROSSFADE, rd)
        # Channel
        attr = gridlib.GridCellAttr()
        attr.SetReadOnly(True)
        self.SetAttr(row, ID_COL_CHANNEL, attr)
        rd = gridlib.GridCellNumberRenderer()
        self.SetCellRenderer(row, ID_COL_CROSSFADE, rd)
        
        self.SetCellAlignment(row, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        for i in range(1, len(LABELS)):
            self.SetCellAlignment(row, i, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

    def putObjectAttrOnCells(self, obj, row):
        attrs = obj.getAttributes()
        for key in sorted(attrs):
            if key == ID_COL_FILENAME:
                self.SetCellValue(row, key, attrs[key])
            elif key == ID_COL_LOOPMODE:
                self.SetCellValue(row, key, LOOPMODES[attrs[key]])
            elif key == ID_COL_PLAYING:
                self.SetCellValue(row, key, PLAYING[attrs[key]])
            elif key == ID_COL_TRANSPO:
                if obj.getShowInterp() == 0:
                    self.SetCellValue(row, key, str(attrs[key]))
            elif key == ID_COL_TRANSPOX:
                if obj.getShowInterp() == 1:
                    self.SetCellValue(row, ID_COL_TRANSPO, str(attrs[key]))
            elif key == ID_COL_GAIN:
                if obj.getShowInterp() == 0:
                    self.SetCellValue(row, key, str(attrs[key]))
            elif key == ID_COL_GAINX:
                if obj.getShowInterp() == 1:
                    self.SetCellValue(row, ID_COL_GAIN, str(attrs[key]))
            else:
                self.SetCellValue(row, key, str(attrs[key]))
        self.SetCellTextColour(row, ID_COL_FILENAME, self.textColour)

    def OnCellChange(self, evt):
        self.selRow, self.selCol = evt.GetRow(), evt.GetCol()
        val = self.GetCellValue(self.selRow, self.selCol)
        if self.selCol == ID_COL_TRANSPO:
            if self.objects[self.selRow].getShowInterp() == 0:
                self.objects[self.selRow].setTranspo(float(val))
            else:
                self.objects[self.selRow].setTranspox(float(val))
        elif self.selCol == ID_COL_GAIN:
            if self.objects[self.selRow].getShowInterp() == 0:
                self.objects[self.selRow].setGain(float(val))
            else:
                self.objects[self.selRow].setGainx(float(val))
        elif self.selCol == ID_COL_STARTPOINT:
            self.objects[self.selRow].setStartPoint(float(val))
        elif self.selCol == ID_COL_ENDPOINT:
            self.objects[self.selRow].setEndPoint(float(val))
        elif self.selCol == ID_COL_CROSSFADE:
            self.objects[self.selRow].setCrossfade(float(val))
        elif self.selCol == ID_COL_CHANNEL:
            self.objects[self.selRow].setChannel(int(val))
        evt.Skip()

    def OnLeftDown(self, evt):
        upos = self.CalcUnscrolledPosition(evt.GetPosition())
        self.selRow, self.selCol = self.XYToCell(*upos)
        if self.selRow < (self.GetNumberRows() - 1) and \
           self.selCol in [ID_COL_TRANSPO, ID_COL_GAIN, ID_COL_STARTPOINT,
                           ID_COL_ENDPOINT, ID_COL_CROSSFADE, ID_COL_CHANNEL]:
            self.clickPosition = evt.GetPosition()[1]
            self.GetGridWindow().CaptureMouse()
            if self.selCol == ID_COL_TRANSPO:
                if self.objects[self.selRow].getShowInterp() == 0:
                    self.initialTranspo = self.objects[self.selRow].getTranspo()
                else:
                    self.initialTranspo = self.objects[self.selRow].getTranspox()
            elif self.selCol == ID_COL_GAIN:
                if self.objects[self.selRow].getShowInterp() == 0:
                    self.initialGain = self.objects[self.selRow].getGain()
                else:
                    self.initialGain = self.objects[self.selRow].getGainx()
            elif self.selCol == ID_COL_STARTPOINT:
                self.initialStart = self.objects[self.selRow].getStartPoint()
            elif self.selCol == ID_COL_ENDPOINT:
                self.initialEnd = self.objects[self.selRow].getEndPoint()
            elif self.selCol == ID_COL_CROSSFADE:
                self.initialFade = self.objects[self.selRow].getCrossfade()
            elif self.selCol == ID_COL_CHANNEL:
                self.initialChannel = self.objects[self.selRow].getChannel()
        evt.Skip()

    def OnLeftUp(self, evt):
        if self.GetGridWindow().HasCapture():
            self.setInitialValuesToNone()
            self.GetGridWindow().ReleaseMouse()
        evt.Skip()

    def clip(self, x, mi, ma):
        if x < mi:
            return mi
        elif x > ma:
            return ma
        else:
            return x

    def OnMotion(self, evt):
        if self.clickPosition is not None:
            inc = {
                ID_COL_TRANSPO: [.0001,.01], ID_COL_GAIN: [.01,.1],
                ID_COL_STARTPOINT: [.0001,.01], ID_COL_ENDPOINT: [.0001,.01],
                ID_COL_CROSSFADE: [.1,1], ID_COL_CHANNEL: [1,1]
                  }[self.selCol]
            diff = self.clickPosition - evt.GetPosition()[1]
            dur = self.objects[self.selRow].getDuration()
            if evt.ShiftDown():
                fdiff = diff * inc[0]
            else:
                fdiff = diff * inc[1]
            if self.selCol == ID_COL_TRANSPO:
                val = self.clip(self.initialTranspo + fdiff, 0.0, 4.0)
                if self.objects[self.selRow].getShowInterp() == 0:
                    self.objects[self.selRow].setTranspo(val)
                else:
                    self.objects[self.selRow].setTranspox(val)
            elif self.selCol == ID_COL_GAIN:
                val = self.clip(self.initialGain + fdiff, -120.0, 24.0)
                if self.objects[self.selRow].getShowInterp() == 0:
                    self.objects[self.selRow].setGain(val)
                else:
                    self.objects[self.selRow].setGainx(val)
            elif self.selCol == ID_COL_STARTPOINT:
                val = self.clip(self.initialStart + fdiff, 0.0, dur)
                self.objects[self.selRow].setStartPoint(val)
            elif self.selCol == ID_COL_ENDPOINT:
                val = self.clip(self.initialEnd + fdiff, 0.0, dur)
                self.objects[self.selRow].setEndPoint(val)
            elif self.selCol == ID_COL_CROSSFADE:
                val = self.clip(self.initialFade + fdiff, 0.0, 50.0)
                self.objects[self.selRow].setCrossfade(val)
            elif self.selCol == ID_COL_CHANNEL:
                val = self.clip(self.initialChannel + fdiff, 0, 32)
                self.objects[self.selRow].setChannel(val)
            self.SetCellValue(self.selRow, self.selCol, str(val))
        evt.Skip()

    def OnCellEditorHidden(self, evt):
        QLiveLib.setVar("CanProcessCueKeys", True)

    def OnCellEditorShown(self, evt):
        QLiveLib.setVar("CanProcessCueKeys", False)

    def OnCellLeftClick(self, evt):
        # TODO: check and warning here...
        sndfolder = os.path.join(QLiveLib.getVar("projectFolder"), "sounds")
        self.snds = sorted([f for f in os.listdir(sndfolder)])
        if self.snds == []:
            self.OnCellRightClick(evt)
        self.selRow, self.selCol = evt.GetRow(), evt.GetCol()
        if self.selCol == ID_COL_FILENAME:
            menu = wx.Menu("Soundfiles")
            self.snds = sorted([f for f in os.listdir(sndfolder)])
            i = 0
            for i, snd in enumerate(self.snds):
                menu.Append(i+1, snd)
            menu.Bind(wx.EVT_MENU, self.selectSound, id=1, id2=i+1)
            if self.snds != []: # do not show an empty menu
                self.PopupMenu(menu, evt.GetPosition())
            menu.Destroy()
        if self.selRow != self.GetNumberRows() - 1:
            if self.selCol == ID_COL_LOOPMODE:
                menu = wx.Menu("Loop Modes")
                for i, md in enumerate(LOOPMODES):
                    menu.Append(i+1, md)
                menu.Bind(wx.EVT_MENU, self.selectLoopMode, id=1, id2=i+1)
                self.PopupMenu(menu, evt.GetPosition())
                menu.Destroy()
            elif self.selCol == ID_COL_PLAYING:
                menu = wx.Menu("Playing Modes")
                for i, md in enumerate(PLAYING):
                    menu.Append(i+1, md)
                menu.Bind(wx.EVT_MENU, self.selectPlayingMode, id=1, id2=i+1)
                self.PopupMenu(menu, evt.GetPosition())
                menu.Destroy()
            elif self.selCol == ID_COL_DIRECTOUT:
                val = self.objects[self.selRow].getDirectOut()
                val = not val
                self.objects[self.selRow].setDirectOut(val)
                self.SetCellValue(self.selRow, self.selCol, str(val))
        evt.Skip()

    def OnCellRightClick(self, evt):
        self.selRow, self.selCol = evt.GetRow(), evt.GetCol()
        if self.selCol == ID_COL_FILENAME:
            dlg = wx.FileDialog(self, 
                                "Open Soundfile...", os.path.expanduser("~"), 
                                "", AUDIO_FILE_WILDCARD, style=wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.copyToSoundsFolder(path)
                self.loadSound(os.path.basename(path))
            dlg.Destroy()
        elif self.selCol == ID_COL_TRANSPO:
            self.objects[self.selRow].openTranspoAutomationWindow()
        elif self.selCol == ID_COL_GAIN:
            self.objects[self.selRow].openGainAutomationWindow()
            
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        if evt.GetRow() < len(self.objects):
            self.selRow = evt.GetRow()
        evt.Skip()

    def OnLabelRightClick(self, evt):
        row = evt.GetRow()
        if row != -1:
            actions = [("Duplicate Row", wx.ITEM_NORMAL), 
                       ("Delete Row", wx.ITEM_NORMAL), 
                       ("Show Parameter Values", wx.ITEM_RADIO), 
                       ("Show Interpolation Times", wx.ITEM_RADIO)]
            self.selRow = row
            menu = wx.Menu()
            for i, act in enumerate(actions):
                menu.Append(i+1, act[0], kind=act[1])
                if i == 1:
                    menu.AppendSeparator()
            menu.Check(self.objects[self.selRow].getShowInterp()+3, True)

            menu.Bind(wx.EVT_MENU, self.doLabelAction, id=1, id2=i+1)
            self.PopupMenu(menu, evt.GetPosition())
            menu.Destroy()
        evt.Skip()

    def doLabelAction(self, evt):
        if evt.GetId() == 1: # Duplicate
            obj = self.objects[self.selRow]
            id = obj.getId()
            filename = obj.getFilename()
            new = SoundFileObject(id, filename)
            new.copy(obj)
            self.selRow += 1
            self.objects.insert(self.selRow, new)
            self.addRow(index=self.selRow)
            self.putObjectAttrOnCells(new, self.selRow)
            for id in [ID_COL_TRANSPO, ID_COL_GAIN, ID_COL_STARTPOINT,
                       ID_COL_ENDPOINT, ID_COL_CROSSFADE, ID_COL_CHANNEL]:
                attr = self.GetOrCreateCellAttr(self.selRow, id)
                attr.SetReadOnly(False)
        elif evt.GetId() == 2: # Delete
            QLiveLib.getVar("FxTracks").checkForDeletedSoundfile(self.selRow)
            del self.objects[self.selRow]
            self.DeleteRows(self.selRow, 1, True)
        
        if evt.GetId() >= 3: # Show parameter values/interpolation times
            self.objects[self.selRow].setShowInterp(evt.GetId() - 3)
            self.putObjectAttrOnCells(self.objects[self.selRow], self.selRow)

        for i, obj in enumerate(self.objects):
            obj.setId(i)

    def selectSound(self, evt):
        sel = self.snds[evt.GetId() - 1]
        if sel is not None:
            self.loadSound(sel)
        evt.Skip()

    def loadSound(self, sel):
        obj = SoundFileObject(self.selRow, sel)
        obj.setCurrentCue(QLiveLib.getVar("CuesPanel").getCurrentCue())
        if obj.isValid():
            if self.selRow < len(self.objects):
                self.objects[self.selRow] = obj
            else:
                self.objects.append(obj)
                self.addRow()
            self.putObjectAttrOnCells(obj, self.selRow)
            for id in [ID_COL_TRANSPO, ID_COL_GAIN, ID_COL_STARTPOINT,
                       ID_COL_ENDPOINT, ID_COL_CROSSFADE, ID_COL_CHANNEL]:
                attr = self.GetOrCreateCellAttr(self.selRow, id)
                attr.SetReadOnly(False)

    def addObject(self, id ,filename):
        self.selRow = id
        self.loadSound(filename)

    def setObjectCues(self, id, cues):
        obj = self.objects[id]
        obj.setCues(cues)
        obj.loadCue(0)

    def selectLoopMode(self, evt):
        sel = LOOPMODES[evt.GetId() - 1]
        if sel is not None:
            self.objects[self.selRow].setLoopMode(evt.GetId() - 1)
            self.SetCellValue(self.selRow, self.selCol, sel)

    def selectPlayingMode(self, evt):
        sel = PLAYING[evt.GetId() - 1]
        if sel is not None:
            self.objects[self.selRow].setPlaying(evt.GetId() - 1)
            self.SetCellValue(self.selRow, self.selCol, sel)

    def getSoundFileObjects(self):
        return self.objects
        
    def getSelectedSoundFile(self):
        if self.selRow == -1 or self.selRow >= len(self.objects):
            return None
        else:
            return self.objects[self.selRow]

    def refresh(self):
        for i in range(len(self.objects)):
            self.putObjectAttrOnCells(self.objects[i], i)

class SoundFilePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.grid = SoundFileGrid(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

    def loadCue(self, x):
        self.saveCue()
        for obj in self.getSoundFileObjects():
            obj.loadCue(x)
            self.grid.putObjectAttrOnCells(obj, obj.getId())

    def saveCue(self):
        for obj in self.getSoundFileObjects():
            obj.saveCue()

    def addCue(self, x):
        self.saveCue()
        for obj in self.getSoundFileObjects():
            obj.addCue(x)

    def delCue(self, x, cur):
        for obj in self.getSoundFileObjects():
            obj.delCue(x)
            self.loadCue(cur)

    def cueEvent(self, evt):
        tp = evt.getType()
        if tp == CUE_TYPE_DELETE:
            self.delCue(evt.getOld(), evt.getCurrent())
        elif tp == CUE_TYPE_SELECT:
            self.loadCue(evt.getCurrent())
        elif tp == CUE_TYPE_NEW:
            self.addCue(evt.getCurrent())
        elif tp == CUE_TYPE_SAVE:
            self.saveCue()

    def setSaveState(self, lst):
        for dict in lst:
            id = dict["id"]
            filename = dict["filename"]
            self.grid.addObject(id, filename)
            self.grid.setObjectCues(id, dict["cues"])
            
    def getSaveState(self):
        self.saveCue()
        l = []
        for obj in self.getSoundFileObjects():
            dict = {"id": obj.getId(), 
                    "filename": obj.getFilename(), 
                    "cues": obj.getCues()}
            l.append(dict)
        return l

    def getSoundFileObjects(self):
        return self.grid.getSoundFileObjects()

    def setGlobalInterpTime(self, value, allcues, allsnds):
        if allsnds:
            for object in self.grid.getSoundFileObjects():
                object.setGlobalInterpTime(value, allcues)
        else:
            selected = self.grid.getSelectedSoundFile()
            if selected is not None:
                selected.setGlobalInterpTime(value, allcues)
        self.grid.refresh()
