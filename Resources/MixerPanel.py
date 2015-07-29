#!/usr/bin/env python
# encoding: utf-8
import wx
from pyolib._wxwidgets import BACKGROUND_COLOUR
from Widgets import MeterControlSlider
from AudioMixer import *
from constants import *
import QLiveLib

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
        self.midiscan = MidiLearn(self.getMidiScan)
        self.Bind(wx.EVT_RIGHT_DOWN, self.MouseRightDown)
 
    def localOutFunction(self, value):
        if self.linkedObject:
            self.linkedObject.SetValue(value)
        value = pow(10.0, value * 0.05)
        self.externalOutFunction(value)

    def setLinkedObject(self, obj):
        self.linkedObject = obj

    def setChannelObject(self, obj):
        self.channelobject = obj

    def MouseRightDown(self, evt):
        if evt.ShiftDown():
            self.setMidiCtl(None)
            self.channelobject.stopMidiCtl()
            return
        if not self.midiscanning:
            self.midiscanning = True
            self.midiscan.scan()
            self.setMidiBackgroundColour(MIDILEARN_COLOUR)
        else:
            self.midiscanning = False
            self.midiscan.stop()
            self.revertMidiBackgroundColour()
            
    def getMidiScan(self, ctlnum, midichnl):
        self.setMidiCtl(ctlnum)
        self.channelobject.setMidiCtl(ctlnum)
        self.revertMidiBackgroundColour()
        
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
            channel = self.audioMixer.getInputChannel(i)
            slide = QLiveControlSlider(self, -60, 18, 0, size=(28,100), 
                                       orient=wx.VERTICAL, 
                                       outFunction=channel.setVolume)
            slide.setChannelObject(channel)
            channel.setMidiCallback(slide.SetValue)
            self.inputSliders.append(slide)
            channel.setAmpCallback(slide.setRms)
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
            channel = self.audioMixer.getOutputChannel(i)            
            slide = QLiveControlSlider(self, -60, 18, 0, size=(28,100), 
                                       orient=wx.VERTICAL, 
                                       outFunction=channel.setVolume)
            slide.setChannelObject(channel)
            channel.setMidiCallback(slide.SetValue)
            self.outputSliders.append(slide)
            channel.setAmpCallback(slide.setRms)
            outputSliderBox.Add(slide, 0, wx.ALL, 2)
        outputBox.Add(outputSliderBox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(inputBox, 1, wx.EXPAND)
        mainSizer.Add(separator, 0, wx.EXPAND|wx.LEFT, 5)
        mainSizer.Add(outputBox, 1, wx.EXPAND)
        self.SetSizer(mainSizer)

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
            slide.setMidiCtl(ctl)
            self.audioMixer.getInputChannel(i).setMidiCtl(ctl)
            self.audioMixer.getInputChannel(i).setMidiCtlValue(val)
        for i, slide in enumerate(self.outputSliders):
            val = dict["outputSliderValues"][i]
            ctl = dict["outputSliderCtls"][i]
            slide.SetValue(val)
            slide.setMidiCtl(ctl)
            self.audioMixer.getOutputChannel(i).setMidiCtl(ctl)
            self.audioMixer.getOutputChannel(i).setMidiCtlValue(val)
        inlink = dict.get("inputLinked", False)
        outlink = dict.get("outputLinked", False)
        self.linkInputs(set=inlink)
        self.linkOutputs(set=outlink)

if __name__ == "__main__":
    from pyo64 import *
    class TestWindow(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None)
            self.Bind(wx.EVT_CLOSE, self.onClose)
            self.server = Server().boot().start()
            self.server.amp = 0.1
            self.mixer = AudioMixer()
            self.panel = MixerPanel(self, self.mixer)
            self.SetSize(self.panel.GetBestSize())
        def onClose(self, evt):
            self.server.stop()
            self.Destroy()
    app = wx.App()
    frame = TestWindow()
    frame.Show()
    app.MainLoop()
