# encoding: utf-8
"""
Copyright 2016 (Pierre Michaud, Olivier Belanger, Tiago Bortoletto Vaz)

This file is part of QLive, a cues-based software to help the 
creation of mixed music.

QLive is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

QLive is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with QLive.  If not, see <http://www.gnu.org/licenses/>.

"""
import wx
import QLiveLib
from constants import *
from FxBox import FxBox, InputBox

class FxTrack:
    def __init__(self, parent, id=0):
        self.id = id
        self.trackPosition = 0
        self.trackHeight = TRACK_ROW_SIZE * 2
        self.cols = 1
        self.rows = 1
        self.buttonsFxs = []
        self.buttonsInputs = []
        self.setFont()

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setTrackPosition(self, x):
        self.trackPosition = x

    def getTrackPosition(self):
        return self.trackPosition

    def setTrackHeight(self, h):
        self.trackHeight = h

    def getTrackHeight(self):
        return self.trackHeight

    def setFont(self, ptsize=8):
        if PLATFORM == "darwin":
            ptsize += 3
        self.font = wx.Font(ptsize, wx.FONTFAMILY_DEFAULT, wx.NORMAL,
                            wx.FONTWEIGHT_NORMAL, face="Monospace")

    def checkTrackSize(self):
        xid = yid = 0
        if len(self.buttonsFxs):
            xid = max([but.getId()[0] for but in self.buttonsFxs])
        if len(self.buttonsInputs) or len(self.buttonsFxs):
            yid = max([but.getId()[1] for but in self.buttonsFxs] + \
                   [but.getId()[1] for but in self.buttonsInputs])

        if self.cols > (xid + 1):
            self.cols = xid + 2

        if self.rows > (yid + 1):
            self.rows = yid + 2
        elif (yid + 2) > self.rows:
            self.rows += 1
        self.trackHeight = TRACK_ROW_SIZE * self.rows

    def createButtonFromDict(self, dic, type):
        if type == "fx":
            but = FxBox(self)
            self.buttonsFxs.append(but)
        else:
            but = InputBox(self)
            self.buttonsInputs.append(but)
        but.setSaveDict(dic)

    def isIdAvailable(self, id, isInput):
        if isInput:
            for button in self.buttonsInputs:
                if button.getId() == id:
                    return False
            return True
        else:
            for button in self.buttonsFxs:
                if button.getId() == id:
                    return False
            return True

    def moveButton(self, button, pos):
        update = False
        yid = (pos[1] - self.trackPosition) / TRACK_ROW_SIZE
        if yid < 0:
            yid = 0
        if button.isInput:
            id = [0, yid]
            if self.isIdAvailable(id, isInput=True):
                button.setId(id)
                update = True
        else:
            xid = (pos[0] - INPUTS_LINE_POS) / TRACK_COL_SIZE
            if xid < 0:
                xid = 0
            id = [xid, yid]
            if self.isIdAvailable(id, isInput=False):
                button.setId(id)
                update = True

        if update:
            self.checkTrackSize()
            QLiveLib.getVar("FxTracks").drawAndRefresh()

    def createButton(self, pos):
        yid = (pos[1] - self.trackPosition) / TRACK_ROW_SIZE
        if pos[0] > SELECTION_LINE_POS and pos[0] < INPUTS_LINE_POS:
            but = InputBox(self)
            but.setId([0, yid])
            self.buttonsInputs.append(but)
        else:
            xid = (pos[0] - INPUTS_LINE_POS) / TRACK_COL_SIZE
            but = FxBox(self)
            but.setId([xid, yid])
            self.buttonsFxs.append(but)
            if (xid + 1) > self.cols:
                self.cols = xid + 2

        self.checkTrackSize()

        QLiveLib.getVar("FxTracks").drawAndRefresh()

    def deleteButton(self, but):
        if but.isInput:
            self.buttonsInputs.remove(but)
        else:
            self.buttonsFxs.remove(but)
        but.delete()
        self.checkTrackSize()
        QLiveLib.getVar("FxTracks").drawAndRefresh()

    def close(self):
        for but in self.buttonsFxs:
            but.delete()
        for but in self.buttonsInputs:
            but.delete()

    def start(self):
        self.createConnections()

    def getButtonInputs(self):
        return self.buttonsInputs

    def getButtonFxs(self):
        return self.buttonsFxs

    def createConnections(self):
        inputs = [but.getOutput() for but in self.buttonsInputs]
        insum = sum([inp for inp in inputs if inp is not None])

        for col in range(self.cols):
            accum = []
            for but in self.buttonsFxs:
                if but.getId()[0] == col:
                    but.setInput(insum)
                    if but.getOutput() is not None:
                        accum.append(but.getOutput())
            if accum != []:
                insum = sum(accum)

        self.connectAudioMixer()

    def connectAudioMixer(self):
        audioMixer = QLiveLib.getVar("AudioMixer")
        audioServer = QLiveLib.getVar("AudioServer")

        for obj in self.buttonsInputs:
            if obj.name == "AudioIn":
                inchnls = obj.getInChannels()
                ismulti = obj.getIsMultiChannels()
                channels = [audioMixer.getInputChannel(i).getOutput()
                            for i in range(NUM_INPUTS) if inchnls[i]]
                if not ismulti:
                    channels = sum(channels)
                obj.setInput(channels)
            elif obj.name == "Soundfile":
                id = obj.getSoundfileId()
                if id is not None:
                    source = audioServer.getSoundfiles()[id]
                    if source:
                        obj.setInput(source.looper)

        for i, obj in enumerate(self.buttonsFxs):
            if obj.name == "AudioOut":
                chnls = len(obj.getOutput())
                outchnls = obj.getOutChannels()
                channels = [j for j in range(NUM_OUTPUTS) if outchnls[j]]
                for j in range(chnls):
                    audioMixer.addToMixer(channels[j % len(channels)],
                                          obj.getOutput()[j])

    def checkForDeletedSoundfile(self, id):
        for obj in self.buttonsInputs:
            if obj.name == "Soundfile":
                oid = obj.getSoundfileId()
                if oid != "None":
                    if oid == id:
                        obj.setSoundfile("None")
                        if obj.view is not None:
                            obj.view.setSoundfile("None")
                    elif oid > id:
                        obj.setSoundfile(str(str(oid)))
                        if obj.view is not None:
                            obj.view.setSoundfile(str(oid))

    def onPaint(self, dc, buttonBitmap, disableButtonBitmap, selectedTrack,
                trackPosition):
        gc = wx.GraphicsContext_Create(dc)

        dc.SetFont(self.font)

        self.trackPosition = trackPosition

        # grid
        dc.SetPen(wx.Pen("#3F3F3F", 1))
        for i in range(1, self.rows+1):
            y = TRACK_ROW_SIZE * i + self.trackPosition
            dc.DrawLine(27, y, 124, y)
            dc.DrawLine(127, y, MAX_WIDTH-127, y)
        for i in range(1, MAX_WIDTH/(TRACK_COL_SIZE-1)):
            x = i * TRACK_COL_SIZE + INPUTS_LINE_POS
            end = self.trackPosition + self.trackHeight
            dc.DrawLine(x, self.trackPosition, x, end)

        if self.id == selectedTrack:
            r = wx.Rect(1,self.trackPosition+1,MAX_WIDTH-2,self.trackHeight-2)
            gc.SetPen(wx.Pen("#BBBBBB", 1.5))
            gc.SetBrush(wx.Brush(TRACKS_BACKGROUND_COLOUR, wx.TRANSPARENT))
            gc.DrawRoundedRectangle(r[0], r[1], r[2], r[3], 3)

        dc.SetTextForeground("#FFFFFF")
        rect = wx.Rect(0, self.trackPosition, SELECTION_LINE_POS, self.trackHeight)
        dc.DrawLabel(str(self.id), rect, wx.ALIGN_CENTER)

        dc.SetTextForeground(FXBOX_FOREGROUND_COLOUR)
        for i, inputBut in enumerate(self.buttonsInputs):
            rect = inputBut.getRect()
            gc.DrawBitmap(buttonBitmap, rect[0], rect[1], rect[2], rect[3])
            dc.DrawLabel(inputBut.name, rect, wx.ALIGN_CENTER)

        for i, button in enumerate(self.buttonsFxs):
            r = button.getRect()
            if button.getEnable():
                gc.DrawBitmap(buttonBitmap, r[0], r[1], r[2], r[3])
            else:
                gc.DrawBitmap(disableButtonBitmap, r[0], r[1], r[2], r[3])
            dc.DrawLabel(button.name, r, wx.ALIGN_CENTER)

        dc.SetPen(wx.Pen("#222222", 1))
        y = self.trackPosition + self.trackHeight
        dc.DrawLine(0, y, MAX_WIDTH, y)

        return self.trackHeight + self.trackPosition

    def setTrackGlobalInterpTime(self, value, allcues, meth):
        tmp = self.buttonsFxs + self.buttonsInputs
        for but in tmp:
            but.setGlobalInterpTime(value, allcues, meth)

    def getSaveDict(self):
        dict = {}
        dict["fxsValues"] = []
        for i, button in enumerate(self.buttonsFxs):
            dict["fxsValues"].append(button.getSaveDict())

        dict["inputValues"] = []
        for i, inputBut in enumerate(self.buttonsInputs):
            dict["inputValues"].append(inputBut.getSaveDict())

        dict["trackPosition"] = self.trackPosition
        dict["trackHeight"] = self.trackHeight
        dict["rows"] = self.rows
        dict["cols"] = self.cols
        return dict

    def setSaveDict(self, saveDict):
        self.buttonsFxs = []
        self.buttonsInputs = []
        self.rows = saveDict["rows"]
        self.cols = saveDict["cols"]
        self.trackPosition = saveDict.get("trackPosition", 0)
        self.trackHeight = saveDict.get("trackHeight", TRACK_ROW_SIZE * 2)
        for dic in saveDict["fxsValues"]:
            self.createButtonFromDict(dic, type="fx")
        for dic in saveDict["inputValues"]:
            self.createButtonFromDict(dic, type="input")

    def cueEvent(self, evt):
        for i, button in enumerate(self.buttonsFxs):
            button.cueEvent(evt)
        for i, inputBut in enumerate(self.buttonsInputs):
            inputBut.cueEvent(evt)
