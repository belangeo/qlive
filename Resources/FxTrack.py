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
from constants import *
from FxBox import *
import QLiveLib

class FxTrack:
    def __init__(self, parent, id=0):
        self.id = id
        self.trackPosition = 0
        self.trackHeight = TRACK_ROW_SIZE * 2
        self.cols = 1
        self.rows = 1

        self.setFont()
        self.createButtons()

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

    def createButtons(self):
        # TODO: Buttons should be created at a position according to ther ids
        self.buttonsFxs = []
        self.buttonsInputs = []
        for i in range(self.rows):
            for j in range(self.cols):
                but = FxBox(self)
                but.setId([j,i])
                self.buttonsFxs.append(but)
            but = InputBox(self)
            but.setId([0,i])
            self.buttonsInputs.append(but)

    def createButton(self, pos):
        if pos[0] > 25 and pos[0] < 125:
            but = InputBox(self)
            but.setId([0, len(self.buttonsInputs)])
            self.buttonsInputs.append(but)
        else:
            # TODO: need to retrieve the correct id from the position
            but = FxBox(self)
            but.setId([len(self.buttonsFxs), 0])
            self.buttonsFxs.append(but)

    def deleteButton(self, but):
        if but.isInput:
            self.buttonsInputs.remove(but)
            lst = self.buttonsInputs
        else:
            self.buttonsFxs.remove(but)
            lst = self.buttonsFxs
        for i, but in enumerate(lst):
            id = but.getId()
            id[0] = i
            but.setId(id)
        but.delete()
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
        for i, button in enumerate(self.buttonsFxs):
            if i == 0: # TODO: Should be based on the id...
                button.setInput(self.buttonsInputs[i].getOutput())
            else:
                button.setInput(self.buttonsFxs[i-1].getOutput())
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

    def onPaint(self, dc, buttonBitmap, disableButtonBitmap, selectedTrack):
        gc = wx.GraphicsContext_Create(dc)

        dc.SetFont(self.font)

        # grid
        dc.SetPen(wx.Pen("#3F3F3F", 1))
        for i in range(1, self.rows+1):
            y = TRACK_ROW_SIZE * i + self.trackPosition
            dc.DrawLine(27, y, 124, y)
            dc.DrawLine(127, y, MAX_WIDTH-127, y)
        for i in range(1, MAX_WIDTH/(TRACK_COL_SIZE-1)):
            x = i * TRACK_COL_SIZE + 125
            end = self.trackPosition + self.trackHeight
            dc.DrawLine(x, self.trackPosition, x, end)

        if self.id == selectedTrack:
            r = wx.Rect(1,self.trackPosition+1,MAX_WIDTH-2,self.trackHeight-2)
            gc.SetPen(wx.Pen("#BBBBBB", 1.5))
            gc.SetBrush(wx.Brush(TRACKS_BACKGROUND_COLOUR, wx.TRANSPARENT))
            gc.DrawRoundedRectangle(r[0], r[1], r[2], r[3], 3)

        dc.SetTextForeground("#FFFFFF")
        rect = wx.Rect(0, self.trackPosition, 25, self.trackHeight)
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
        self.rows = saveDict["rows"]
        self.cols = len(saveDict["fxsValues"]) # saveDict["cols"]
        self.trackPosition = saveDict.get("trackPosition", 0)
        self.trackHeight = saveDict.get("trackHeight", TRACK_ROW_SIZE * 2)
        self.createButtons()
        for i, button in enumerate(self.buttonsFxs):
            button.setSaveDict(saveDict["fxsValues"][i])
        for i, inputBut in enumerate(self.buttonsInputs):
            inputBut.setSaveDict(saveDict["inputValues"][i])

    def cueEvent(self, evt):
        for i, button in enumerate(self.buttonsFxs):
            button.cueEvent(evt)
        for i, inputBut in enumerate(self.buttonsInputs):
            inputBut.cueEvent(evt)
