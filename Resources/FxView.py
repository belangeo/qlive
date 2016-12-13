#!/usr/bin/python
# encoding: utf-8
import os
import wx
from pyolib._wxwidgets import BACKGROUND_COLOUR, Grapher
from constants import *
from Widgets import *
import QLiveLib

class SliderWidget(wx.Panel):
    def __init__(self, parent, parameters, fxbox):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.fromUser = False
        self.midiscanning = False
        self.parameters = parameters
        self.fxbox = fxbox
        self.name = parameters[0]
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.slider = QLiveControlKnob(self, parameters[2], parameters[3],
                                       parameters[1], label=parameters[0],
                                       log=parameters[5],
                                       outFunction=self.outputValue,
                                       editFunction=self.onEditFunction)
        self.sizer.Add(self.slider, 0, wx.ALL, 5)

        self.interpKnob = QLiveControlKnob(self,
                                INTERPTIME_MIN,
                                INTERPTIME_MAX, interpTime,
                                label=parameters[0], log=True,
                                outFunction=self.outputInterpValue,
                                outOnShiftFunction=self.onChangeAllInterp,
                                backColour=CONTROLSLIDER_BACK_COLOUR_INTERP)
        self.sizer.Add(self.interpKnob, 0, wx.ALL, 5)

        self.slider.Bind(wx.EVT_RIGHT_DOWN, self.MouseRightDown)

        self.interpKnob.Hide()
        self.SetSizer(self.sizer)

    def MouseRightDown(self, evt):
        if evt.ShiftDown():
            QLiveLib.getVar("MidiServer").unbind("ctls", self.slider.midictl,
                                                 self.midi)
            self.slider.setMidiCtl(None)
            return
        if not self.midiscanning:
            self.midiscanning = True
            QLiveLib.getVar("MidiServer").ctlscan(self.getMidiScan)
            self.slider.setMidiLearn(True)
        else:
            self.midiscanning = False
            QLiveLib.getVar("MidiServer").ctlscan(None)
            self.slider.setMidiLearn(False)

    def getMidiScan(self, ctlnum, midichnl):
        self.assignMidiCtl(ctlnum)
        self.slider.setMidiLearn(False)

    def assignMidiCtl(self, ctlnum):
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.slider.setMidiCtl(ctlnum)
        QLiveLib.getVar("MidiServer").bind("ctls", ctlnum, self.midi)
        self.setInterpValue(interpTime, True)

    def midi(self, value):
        v = rescale(value, 0, 127, self.parameters[2], self.parameters[3],
                    ylog=self.parameters[5])
        self.slider.SetValue(v, True)

    def getMidiBinding(self):
        return self.slider.midictl

    def setMidiBinding(self, ctlnum):
        if ctlnum is not None:
            self.assignMidiCtl(ctlnum)

    def onEditFunction(self, state):
        self.GetParent().GetParent().onEditButton(self, state)

    def setAutoPlay(self, state):
        self.slider.setAutoPlay(state)
        self.interpKnob.setAutoPlay(state)

    def setShowEdit(self, state):
        self.slider.setShowEdit(state)
        self.interpKnob.setShowEdit(state)

    def outputValue(self, value):
        self.fxbox.setParamValue(self.name, value, self.fromUser)
        self.fromUser = True

    def setValue(self, value, propagate=False):
        self.fromUser = False
        self.slider.SetValue(value, propagate)

    def getValue(self):
        return self.slider.GetValue()

    def outputInterpValue(self, value):
        self.fxbox.setInterpValue(self.name, value)

    def onChangeAllInterp(self, value):
        self.GetParent().GetParent().onChangeAllInterp(value)

    def setInterpValue(self, value, propagate=False):
        self.interpKnob.SetValue(value, propagate)

    def getInterpValue(self):
        return self.interpKnob.GetValue()

    def setShowMorph(self, bool):
        if bool:
            self.slider.Hide()
            self.interpKnob.Show()
        else:
            self.slider.Show()
            self.interpKnob.Hide()
        self.Layout()

class FxSlidersView(wx.Frame):
    def __init__(self, parent, fxbox, parameters):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, style=style)
        self.parent = parent
        self.fxbox = fxbox
        self.parameters = parameters
        self.last_enable = 1
        self.graph_object = None

        closeId = wx.NewId()

        tabId = wx.NewId()

        self.prevId = KEY_EVENT_FIRST_ID
        self.nextId = KEY_EVENT_FIRST_ID + 1
        self.cueZeroId = KEY_EVENT_FIRST_ID + 2
        self.cue1Id = KEY_EVENT_FIRST_ID + 3
        self.cue2Id = KEY_EVENT_FIRST_ID + 4
        self.cue3Id = KEY_EVENT_FIRST_ID + 5
        self.cue4Id = KEY_EVENT_FIRST_ID + 6
        self.cue5Id = KEY_EVENT_FIRST_ID + 7
        self.cue6Id = KEY_EVENT_FIRST_ID + 8
        self.cue7Id = KEY_EVENT_FIRST_ID + 9
        self.cue8Id = KEY_EVENT_FIRST_ID + 10
        self.cue9Id = KEY_EVENT_FIRST_ID + 11
        self.cue10Id = KEY_EVENT_FIRST_ID + 12
        accel_tbl = wx.AcceleratorTable([
                            (wx.ACCEL_CTRL, ord('W'), closeId),
                            (wx.ACCEL_NORMAL,  wx.WXK_TAB, tabId),
                            (wx.ACCEL_NORMAL,  wx.WXK_LEFT, self.prevId),
                            (wx.ACCEL_NORMAL,  wx.WXK_RIGHT, self.nextId),
                            (wx.ACCEL_NORMAL,  wx.WXK_ESCAPE, self.cueZeroId),
                            (wx.ACCEL_NORMAL,  ord("1"), self.cue1Id),
                            (wx.ACCEL_NORMAL,  ord("2"), self.cue2Id),
                            (wx.ACCEL_NORMAL,  ord("3"), self.cue3Id),
                            (wx.ACCEL_NORMAL,  ord("4"), self.cue4Id),
                            (wx.ACCEL_NORMAL,  ord("5"), self.cue5Id),
                            (wx.ACCEL_NORMAL,  ord("6"), self.cue6Id),
                            (wx.ACCEL_NORMAL,  ord("7"), self.cue7Id),
                            (wx.ACCEL_NORMAL,  ord("8"), self.cue8Id),
                            (wx.ACCEL_NORMAL,  ord("9"), self.cue9Id),
                            (wx.ACCEL_NORMAL,  ord("0"), self.cue10Id)])
        self.SetAcceleratorTable(accel_tbl)

        mainWin = QLiveLib.getVar("MainWindow")
        self.Bind(wx.EVT_MENU, mainWin.onTabulate, id=tabId)
        self.Bind(wx.EVT_MENU, mainWin.onMoveCue, id=KEY_EVENT_FIRST_ID,
                  id2=KEY_EVENT_FIRST_ID+100)

        self.Bind(wx.EVT_MENU, self.onClose, id=closeId)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetTitle("%s Parameter Controls" % self.fxbox.name)

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(BACKGROUND_COLOUR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Head
        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        self.enable = wx.CheckBox(self.panel, -1, "Enable FX:",
                                  style=wx.ALIGN_RIGHT)
        self.enable.SetValue(1)
        self.enable.Bind(wx.EVT_CHECKBOX, self.enableFx)
        headSizer.Add(self.enable, 0, wx.TOP|wx.RIGHT, 5)
        self.sizer.Add(headSizer, 0, wx.EXPAND)

        self.sizer.Add(wx.StaticLine(self.panel, -1), 0, wx.ALL|wx.EXPAND, 5)

        # Selection boxes
        if "inselect" in self.parameters:
            self.inChannelChecks = []
            statbox = wx.StaticBox(self.panel, -1, "Input Selections")
            selectorSizer = wx.StaticBoxSizer(statbox, wx.HORIZONTAL)
            labels = self.parameters["inselect"]
            for i in range(len(labels)):
                check = wx.CheckBox(self.panel, -1, labels[i])
                check.Bind(wx.EVT_CHECKBOX, self.onCheckInSelect)
                if i == 0:
                    check.SetValue(1)
                self.inChannelChecks.append(check)
                selectorSizer.Add(check, 1, wx.EXPAND|wx.ALL, 5)
            self.sizer.Add(selectorSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)


            sampleList = ["Mono Track", "Multi-Channel Track"]
            self.chnlsButton = wx.RadioBox(self.panel, -1, "",
                                           wx.DefaultPosition,
                                           wx.DefaultSize, sampleList, 2,
                                           wx.RA_SPECIFY_COLS | wx.NO_BORDER)
            self.chnlsButton.Bind(wx.EVT_RADIOBOX, self.onChnlsRadioBox)
            self.sizer.Add(self.chnlsButton, 0, wx.LEFT, 5)

            self.sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)

        if "outselect" in self.parameters:
            self.outChannelChecks = []
            statbox = wx.StaticBox(self.panel, -1, "Output Selections")
            selectorSizer = wx.StaticBoxSizer(statbox, wx.HORIZONTAL)
            labels = self.parameters["outselect"]
            for i in range(len(labels)):
                check = wx.CheckBox(self.panel, -1, labels[i])
                check.Bind(wx.EVT_CHECKBOX, self.onCheckOutSelect)
                if i == 0:
                    check.SetValue(1)
                self.outChannelChecks.append(check)
                selectorSizer.Add(check, 1, wx.EXPAND|wx.ALL, 5)
            self.sizer.Add(selectorSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)

        if "select" in self.parameters:
            self.selectedSoundfile = "None"
            soundfiles = QLiveLib.getVar("Soundfiles").getSoundFileObjects()
            choices = ["None"] + [str(snd.getId()+1) for snd in soundfiles]
            popupSizer = wx.BoxSizer(wx.HORIZONTAL)
            popupTitle = wx.StaticText(self.panel, -1, "Choose a Soundfile:")
            popupSizer.Add(popupTitle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
            self.soundfilesPopup = wx.Choice(self.panel, -1, choices=choices)
            self.soundfilesPopup.SetSelection(0)
            self.soundfilesPopup.Bind(wx.EVT_CHOICE, self.chooseSoundfile)
            popupSizer.Add(self.soundfilesPopup, 0, wx.ALL, 5)
            self.sizer.Add(popupSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)

        # Controller box
        if "ctrls" in self.parameters:
            knobSizer = wx.BoxSizer(wx.HORIZONTAL)
            sampleList = ["Slider Values", "Interpolation Times"]
            self.interpButton = wx.RadioBox(self.panel, -1, "",
                                            wx.DefaultPosition,
                                            wx.DefaultSize, sampleList, 2,
                                            wx.RA_SPECIFY_COLS | wx.NO_BORDER)
            self.interpButton.Bind(wx.EVT_RADIOBOX, self.showMorphEvent)
            self.sizer.Add(self.interpButton, 0, wx.LEFT, 5)

            self.widgets = []
            for param in self.parameters["ctrls"]:
                slider = SliderWidget(self.panel, param, fxbox)
                self.widgets.append(slider)
                knobSizer.Add(slider,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,5)
            self.sizer.Add(knobSizer, 0, wx.EXPAND)

        self.graph = Grapher(self.panel, xlen=256, yrange=(0, 1),
                             init=[(0,0), (0.5,0.5), (1,0)],
                             mode=0, outFunction=None)
        self.graph.SetSize((500, 200))
        self.graph.Hide()
        self.sizer.Add(self.graph, 1, wx.EXPAND|wx.ALL, 5)

        self.panel.SetSizer(self.sizer)

        self.frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.frameSizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizerAndFit(self.frameSizer)

        self.Bind(wx.EVT_ENTER_WINDOW, self.getFocus)
        self.SetMinSize((500, -1))
        self.SetSize((500, -1))

    def getFocus(self, evt):
        if "select" in self.parameters:
            soundfiles = QLiveLib.getVar("Soundfiles").getSoundFileObjects()
            choices = ["None"] + [str(snd.getId()+1) for snd in soundfiles]
            self.soundfilesPopup.SetItems(choices)
            self.soundfilesPopup.SetStringSelection(self.selectedSoundfile)

    def chooseSoundfile(self, evt):
        self.selectedSoundfile = evt.GetEventObject().GetStringSelection()
        self.fxbox.setSoundfile(self.selectedSoundfile)

    def setSoundfile(self, snd):
        self.selectedSoundfile = snd
        self.soundfilesPopup.SetStringSelection(snd)

    def onChangeAllInterp(self, value):
        for slider in self.widgets:
            slider.setInterpValue(value, True)

    def onEditButton(self, obj, state):
        gsz = self.graph.GetSize()
        sz = self.GetSize()
        if self.graph_object is not None:
            if self.graph_object is not obj:
                self.graph_object.setShowEdit(False)
        if state:
            self.graph_object = obj
            if not self.graph.IsShown():
                self.graph.Show()
                self.SetSize((sz[0], sz[1] + gsz[1]))
        else:
            self.graph_object = None
            self.graph.Hide()
            self.SetSize((sz[0], sz[1] - gsz[1]))

    def setInChannelChecks(self, lst):
        for i, check in enumerate(self.inChannelChecks):
            check.SetValue(lst[i])

    def setIsMultiChannels(self, state):
        self.chnlsButton.SetSelection(state)

    def onChnlsRadioBox(self, evt):
        self.fxbox.setIsMultiChannels(evt.GetInt())

    def setOutChannelChecks(self, lst):
        for i, check in enumerate(self.outChannelChecks):
            check.SetValue(lst[i])

    def showMorphEvent(self, evt):
        for widget in self.widgets:
            if isinstance(widget, SliderWidget):
                widget.setShowMorph(evt.GetInt())

    def enableFx(self, evt):
        self.fxbox.setEnable(evt.GetInt(), fromUser=True)
        QLiveLib.getVar("FxTracks").drawAndRefresh()

    def setEnableState(self, x):
        self.enable.SetValue(x)
        if x != self.last_enable:
            self.last_enable = x
            QLiveLib.getVar("FxTracks").drawAndRefresh()

    def onCheckInSelect(self, evt):
        state = evt.GetInt()
        obj = evt.GetEventObject()
        which = int(obj.GetLabel()) - 1
        self.fxbox.checkInChannel(which, state)

    def onCheckOutSelect(self, evt):
        state = evt.GetInt()
        obj = evt.GetEventObject()
        which = int(obj.GetLabel()) - 1
        self.fxbox.checkOutChannel(which, state)

    def getWidgets(self):
        return self.widgets

    def onClose(self, evt):
        self.Hide()