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
from pyolib._wxwidgets import BACKGROUND_COLOUR
from Widgets import MeterControlSlider
from AudioMixer import *
from constants import *
import QLiveLib
from pyo import rescale

class QLiveControlSlider(MeterControlSlider):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0),
                 size=(200,16), log=False, outFunction=None, integer=False,
                 powoftwo=False, backColour=None, orient=wx.HORIZONTAL,
                 linkedObject=None):
        MeterControlSlider.__init__(self, parent, minvalue, maxvalue,
                                    init, pos, size, self.localOutFunction,
                                    False, backColour)
        self.channelobject = None
        self.midiscanning = False
        self.linkedObject = None
        self.externalOutFunction = outFunction

    def setOutFunction(self, func):
        self.externalOutFunction = func

    def localOutFunction(self, value):
        if self.linkedObject:
            self.linkedObject.SetValue(value)
        value = pow(10.0, value * 0.05)
        self.externalOutFunction(value)

    def setLinkedObject(self, obj):
        self.linkedObject = obj

    def setChannelObject(self, obj):
        self.channelobject = obj

    def revertMidiAssignation(self):
        self.midiscanning = False
        QLiveLib.getVar("MidiServer").ctlscan(None)
        self.revertMidiBackgroundColour()
        QLiveLib.getVar("MidiServer").unbind("ctls", self.midictl, self.midi)
        self.setMidiCtl(None)

    def handleMidiScan(self):
        if not self.midiscanning:
            self.midiscanning = True
            QLiveLib.getVar("MidiServer").ctlscan(self.getMidiScan)
            self.setMidiBackgroundColour(MIDILEARN_COLOUR)
        else:
            self.midiscanning = False
            QLiveLib.getVar("MidiServer").ctlscan(None)
            self.revertMidiBackgroundColour()

    def getMidiScan(self, ctlnum, midichnl):
        self.assignMidiCtl(ctlnum)
        self.revertMidiBackgroundColour()

    def assignMidiCtl(self, ctlnum):
        self.setMidiCtl(ctlnum)
        QLiveLib.getVar("MidiServer").bind("ctls", ctlnum, self.midi)

    def midi(self, value):
        self.SetValue(rescale(value, 0, 127, -90, 18))

class MixerPanel(wx.Panel):
    def __init__(self, parent, audioMixer):
        wx.Panel.__init__(self, parent, size=(800,129), style=wx.SUNKEN_BORDER)
        self.audioMixer = audioMixer
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        self.inputLinked = False
        self.outputLinked = False
        self.inputSliders = []
        self.outputSliders = []

        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)

        ### INPUT SECTION
        inputBox = wx.BoxSizer(wx.VERTICAL)
        inputSliderBox = wx.BoxSizer(wx.HORIZONTAL)
        inputBox.AddSpacer((-1,2))
        label = wx.StaticText(self, label="Input Channels")
        label.SetFont(font)
        inputBox.Add(label, 0, wx.LEFT|wx.EXPAND, 10)
        inputBox.Add(wx.StaticLine(self, size=(1, -1)), 0,
                     wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 2)
        for i in range(NUM_INPUTS):
            slide = QLiveControlSlider(self, -90, 18, 0, size=(28,100),
                                       orient=wx.VERTICAL)
            self.inputSliders.append(slide)
            inputSliderBox.Add(slide, 0, wx.ALL, 2)
        inputBox.Add(inputSliderBox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

        separator = wx.StaticLine(self, size=(1, -1), style=wx.LI_VERTICAL)

        #### OUTPUT SECTION
        outputBox = wx.BoxSizer(wx.VERTICAL)
        outputSliderBox = wx.BoxSizer(wx.HORIZONTAL)
        outputBox.AddSpacer((-1,2))
        label = wx.StaticText(self, label = "Output Channels")
        label.SetFont(font)
        outputBox.Add(label, 0, wx.LEFT|wx.EXPAND, 10)
        outputBox.Add(wx.StaticLine(self, size=(1, -1)), 0,
                      wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 2)
        for i in range(NUM_OUTPUTS):
            slide = QLiveControlSlider(self, -90, 18, 0, size=(28,100),
                                       orient=wx.VERTICAL)
            self.outputSliders.append(slide)
            outputSliderBox.Add(slide, 0, wx.ALL, 2)
        outputBox.Add(outputSliderBox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

        self.connectSliders()

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(inputBox, 1, wx.EXPAND)
        mainSizer.Add(separator, 0, wx.EXPAND|wx.LEFT, 5)
        mainSizer.Add(outputBox, 1, wx.EXPAND)
        self.SetSizer(mainSizer)

    def connectSliders(self):
        for i in range(NUM_INPUTS):
            channel = self.audioMixer.getInputChannel(i)
            self.inputSliders[i].setChannelObject(channel)
            self.inputSliders[i].setOutFunction(channel.setVolume)
            channel.setAmpCallback(self.inputSliders[i].setRms)
        for i in range(NUM_OUTPUTS):
            channel = self.audioMixer.getOutputChannel(i)
            self.outputSliders[i].setChannelObject(channel)
            self.outputSliders[i].setOutFunction(channel.setVolume)
            channel.setAmpCallback(self.outputSliders[i].setRms)

    def linkInputs(self, set=None):
        if set is not None:
            if set:
                self.inputLinked = False
            else:
                self.inputLinked = True
        if self.inputLinked == False:
            self.inputLinked = True
            for i, sl in enumerate(self.inputSliders):
                if i%2 == 0:
                    sl.setLinkedObject(self.inputSliders[i+1])
        else:
            self.inputLinked = False
            for i, sl in enumerate(self.inputSliders):
                if i%2 == 0:
                    sl.setLinkedObject(None)

    def linkOutputs(self, set=None):
        if set is not None:
            if set:
                self.outputLinked = False
            else:
                self.outputLinked = True
        if self.outputLinked == False:
            self.outputLinked = True
            for i, sl in enumerate(self.outputSliders):
                if i%2 == 0:
                    sl.setLinkedObject(self.outputSliders[i+1])
        else:
            self.outputLinked = False
            for i, sl in enumerate(self.outputSliders):
                if i%2 == 0:
                    sl.setLinkedObject(None)

    def getSaveDict(self):
        dict = {}
        inputSliderValues = []
        inputSliderCtls = []
        for slide in self.inputSliders:
            inputSliderValues.append(slide.GetValue())
            inputSliderCtls.append(slide.getMidiCtl())
        dict["inputSliderValues"] = inputSliderValues
        dict["inputSliderCtls"] = inputSliderCtls

        outputSliderValues = []
        outputSliderCtls = []
        for slide in self.outputSliders:
            outputSliderValues.append(slide.GetValue())
            outputSliderCtls.append(slide.getMidiCtl())
        dict["outputSliderValues"] = outputSliderValues
        dict["outputSliderCtls"] = outputSliderCtls
        dict["inputLinked"] = self.inputLinked
        dict["outputLinked"] = self.outputLinked

        return dict

    def setSaveDict(self, dict):
        for i, slide in enumerate(self.inputSliders):
            val = dict["inputSliderValues"][i]
            ctl = dict["inputSliderCtls"][i]
            slide.SetValue(val)
            slide.assignMidiCtl(ctl)
        for i, slide in enumerate(self.outputSliders):
            val = dict["outputSliderValues"][i]
            ctl = dict["outputSliderCtls"][i]
            slide.SetValue(val)
            slide.assignMidiCtl(ctl)
        inlink = dict.get("inputLinked", False)
        outlink = dict.get("outputLinked", False)
        self.linkInputs(set=inlink)
        self.linkOutputs(set=outlink)