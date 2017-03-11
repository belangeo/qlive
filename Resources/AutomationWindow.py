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
import QLiveLib
from Widgets import *
from pyo64 import PyoGuiGrapher

class AutomationWindow(wx.Frame):
    def __init__(self, parent, title, object=None, closeCallback=None,
                 paramCallback=None):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, title=title, size=(450,600),
                          style=style)

        closeId = wx.NewId()
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
        self.Bind(wx.EVT_MENU, mainWin.onMoveCue, id=KEY_EVENT_FIRST_ID,
                  id2=KEY_EVENT_FIRST_ID+100)

        self.Bind(wx.EVT_MENU, self.OnClose, id=closeId)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.closeCallback = closeCallback
        self.panel = AutomationPanel(self, object, paramCallback)
        self.Show()

    def getAttributes(self):
        return self.panel.getAttributes()

    def setAttributes(self, dict):
        self.panel.setAttributes(dict)

    def OnClose(self, evt):
        if self.closeCallback is not None:
            self.closeCallback()
        self.Destroy()

class AutomationPanel(wx.Panel):
    def __init__(self, parent, object=None, paramCallback=None):
        wx.Panel.__init__(self, parent, -1)
        cpstyle = wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        interpTime = QLiveLib.getVar("globalInterpTime")

        # parameter object reference
        self.object = object
        self.paramCallback = paramCallback

        # global attributes
        self.mixingMethod = 0
        self.active = 0

        # envelope follower attributes
        self.envActive = 0
        self.envInputs = [0] * NUM_INPUTS
        self.envInputsInterp = interpTime
        self.envThreshold, self.envThresholdInterp = -90, interpTime
        self.envCutoff, self.envCutoffInterp = 20, interpTime
        self.envMin, self.envMinInterp = 0.0, interpTime
        self.envMax, self.envMaxInterp = 1.0, interpTime

        # breakpoint-function attributes
        self.bpfActive = 0
        self.bpfMode = 0
        self.bpfDur, self.bpfDurInterp = 1.0, interpTime
        self.bpfMin, self.bpfMinInterp = 0.0, interpTime
        self.bpfMax, self.bpfMaxInterp = 1.0, interpTime
        self.bpfFunction = [(0, 0.0), (512, 1.0)]

        title = wx.StaticText(self, label="Automation Controls")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD))

        methodChoices = ["Added to the main value",
                         "Multiplying the main value",
                         "Added and replace main value",
                         "Times and replace main value"]
        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        methodLabel = wx.StaticText(self, -1,
                                    label="Multiple Automations Mixing Method:")
        self.method = wx.Choice(self, -1, choices=methodChoices)
        self.method.SetSelection(0)
        self.method.Bind(wx.EVT_CHOICE, self.changeMixingMethod)
        headSizer.Add(methodLabel, 0, wx.RIGHT|wx.TOP, 5)
        headSizer.Add(self.method, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Collapsible Panes - TODO: remove those we won't use in the prototype?
        id = AUTOMATION_PANEL_FIRST_ID
        self.bpfCp = wx.CollapsiblePane(self, id, label="BPF", style=cpstyle)
        self.MakeBpfPaneContent(self.bpfCp.GetPane())
        self.envCp = wx.CollapsiblePane(self, id+1, label="Envelope Follower",
                                        style=cpstyle)
        self.MakeEnvPaneContent(self.envCp.GetPane())
#        self.lfoCp = wx.CollapsiblePane(self, id+2, label="LFO", style=cpstyle)
#        self.randCp = wx.CollapsiblePane(self, id+3, label="Random",
#                                         style=cpstyle)
#        self.pitCp = wx.CollapsiblePane(self, id+4, label="Pitch Follower",
#                                        style=cpstyle)
#        self.zeroCp = wx.CollapsiblePane(self, id+5, label="Zero-Crossing",
#                                         style=cpstyle)
#        self.centCp = wx.CollapsiblePane(self, id+6, label="Centroid",
#                                         style=cpstyle)

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged,
                  id=id, id2=id+1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(headSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.bpfCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.envCp, 0, wx.ALL|wx.EXPAND, 5)
        #sizer.Add(self.lfoCp, 0, wx.ALL|wx.EXPAND, 5)
        #sizer.Add(self.randCp, 0, wx.ALL|wx.EXPAND, 5)
        #sizer.Add(self.pitCp, 0, wx.ALL|wx.EXPAND, 5)
        #sizer.Add(self.zeroCp, 0, wx.ALL|wx.EXPAND, 5)
        #sizer.Add(self.centCp, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

    def changeMixingMethod(self, evt):
        self.mixingMethod = evt.GetInt()
        self.callback()

    def OnPaneChanged(self, evt):
        self.Layout()

    def callback(self):
        if self.paramCallback is not None:
            dict = self.getAttributes()
            self.paramCallback(dict)

    def MakeEnvPaneContent(self, panel):
        interpTime = QLiveLib.getVar("globalInterpTime")
        mainbox = wx.StaticBox(panel, -1, "")
        sizer = wx.StaticBoxSizer(mainbox, wx.VERTICAL)
        sizer.AddSpacer(5)

        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        self.envActiveCheck = wx.CheckBox(panel, -1, "Active:",
                                          style=wx.ALIGN_RIGHT)
        self.envActiveCheck.Bind(wx.EVT_CHECKBOX, self.envOnActivate)
        headSizer.Add(self.envActiveCheck, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.envChannelChecks = []
        statbox = wx.StaticBox(panel, -1, "Input Selections")
        selectorSizer = wx.StaticBoxSizer(statbox, wx.HORIZONTAL)
        for i in range(NUM_INPUTS):
            check = wx.CheckBox(panel, -1, str(i+1))
            check.Bind(wx.EVT_CHECKBOX, self.envOnCheckInputs)
            if i == 0:
                check.SetValue(1)
                self.envInputs[0] = 1
            self.envChannelChecks.append(check)
            selectorSizer.Add(check, 1, wx.EXPAND|wx.ALL, 5)

        interpLabel = wx.StaticText(panel, -1,
                                label="Input Interpolation Time in Seconds: ")
        self.envInInterpCtrl = NumericCtrl(panel, value=interpTime,
                                           interp=0, size=(80, -1),
                                           callback=self.envOnInputsInterp)
        interpSizer = wx.BoxSizer(wx.HORIZONTAL)
        interpSizer.Add(interpLabel, -1,
                        wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        interpSizer.Add(self.envInInterpCtrl)

        sampleList = ["Parameter Values", "Interpolation Times"]
        interpButton = wx.RadioBox(panel, -1, "",
                                   wx.DefaultPosition,
                                   wx.DefaultSize, sampleList, 2,
                                   wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        interpButton.Bind(wx.EVT_RADIOBOX, self.envChangeParamMode)

        params = [["Threshold (dB)", -90, interpTime, self.envOnThresh],
                  ["Cutoff (Hz)", 20, interpTime, self.envOnCutoff],
                  ["Range Min", 0, interpTime, self.envOnMin],
                  ["Range Max", 1, interpTime, self.envOnMax]]
        self.envWidgets = []
        knobSizer = wx.BoxSizer(wx.HORIZONTAL)
        for param in params:
            numbox = wx.BoxSizer(wx.VERTICAL)
            label = wx.StaticText(panel, -1, label=param[0])
            ctrl = NumericCtrl(panel, value=param[1], interp=param[2],
                               size=(80, -1), callback=param[3])
            self.envWidgets.append(ctrl)
            numbox.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 2)
            numbox.Add(ctrl, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 2)
            knobSizer.Add(numbox, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        sizer.Add(headSizer, 0, wx.EXPAND)
        sizer.Add(selectorSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer.Add(interpSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(interpButton, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(knobSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        panel.SetSizer(sizer)

    def envOnActivate(self, evt):
        self.envActive = evt.GetInt()
        self.callback()

    def envOnCheckInputs(self, evt):
        state = evt.GetInt()
        obj = evt.GetEventObject()
        which = int(obj.GetLabel()) - 1
        self.envInputs[which] = state
        self.callback()

    def envOnInputsInterp(self, value, interp):
        self.envInputsInterp = value
        QLiveLib.setVar("CanProcessCueKeys", True)
        self.callback()

    def envOnThresh(self, value, interp):
        self.envThreshold, self.envThresholdInterp = value, interp
        self.callback()

    def envOnCutoff(self, value, interp):
        self.envCutoff, self.envCutoffInterp = value, interp
        self.callback()

    def envOnMin(self, value, interp):
        self.envMin, self.envMinInterp = value, interp
        self.callback()

    def envOnMax(self, value, interp):
        self.envMax, self.envMaxInterp = value, interp
        self.callback()

    def envChangeParamMode(self, evt):
        for widget in self.envWidgets:
            widget.changeMode(evt.GetInt())

    def getEnvAttributes(self):
        return {
                ID_ENV_ACTIVE: self.envActive,
                ID_ENV_INPUTS: self.envInputs,
                ID_ENV_INPUTS_INTERP: self.envInputsInterp,
                ID_ENV_THRESHOLD: self.envThreshold,
                ID_ENV_THRESHOLD_INTERP: self.envThresholdInterp,
                ID_ENV_CUTOFF: self.envCutoff,
                ID_ENV_CUTOFF_INTERP: self.envCutoffInterp,
                ID_ENV_MIN: self.envMin,
                ID_ENV_MIN_INTERP: self.envMinInterp,
                ID_ENV_MAX: self.envMax,
                ID_ENV_MAX_INTERP: self.envMaxInterp
                }

    def setEnvAttributes(self, dict):
        self.envActive = dict[ID_ENV_ACTIVE]
        self.envInputs = dict[ID_ENV_INPUTS]
        self.envInputsInterp = dict[ID_ENV_INPUTS_INTERP]
        self.envThreshold = dict[ID_ENV_THRESHOLD]
        self.envThresholdInterp = dict[ID_ENV_THRESHOLD_INTERP]
        self.envCutoff = dict[ID_ENV_CUTOFF]
        self.envCutoffInterp = dict[ID_ENV_CUTOFF_INTERP]
        self.envMin = dict[ID_ENV_MIN]
        self.envMinInterp = dict[ID_ENV_MIN_INTERP]
        self.envMax = dict[ID_ENV_MAX]
        self.envMaxInterp = dict[ID_ENV_MAX_INTERP]
        # Update graphical widgets
        self.envActiveCheck.SetValue(self.envActive)
        for i in range(NUM_INPUTS):
            self.envChannelChecks[i].SetValue(self.envInputs[i])
        self.envInInterpCtrl.setValues(self.envInputsInterp, 0)
        self.envWidgets[0].setValues(self.envThreshold, self.envThresholdInterp)
        self.envWidgets[1].setValues(self.envCutoff, self.envCutoffInterp)
        self.envWidgets[2].setValues(self.envMin, self.envMinInterp)
        self.envWidgets[3].setValues(self.envMax, self.envMaxInterp)

    def MakeBpfPaneContent(self, panel):
        interpTime = QLiveLib.getVar("globalInterpTime")
        mainbox = wx.StaticBox(panel, -1, "")
        sizer = wx.StaticBoxSizer(mainbox, wx.VERTICAL)
        sizer.AddSpacer(5)

        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        self.bpfActiveCheck = wx.CheckBox(panel, -1, "Active:",
                                          style=wx.ALIGN_RIGHT)
        self.bpfActiveCheck.Bind(wx.EVT_CHECKBOX, self.bpfOnActivate)
        headSizer.Add(self.bpfActiveCheck, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.bpfGrapher = PyoGuiGrapher(panel, 512, size=(200, 150))
        self.bpfGrapher.Bind(EVT_PYO_GUI_GRAPHER, self.bpfOnGrapher)

        modeSizer = wx.BoxSizer(wx.HORIZONTAL)
        modeText = wx.StaticText(panel, label="Playback Mode: ")
        self.bpfPlayMode = wx.Choice(panel, choices=["No Loop", "Forward",
                                                     "Backward", "Back&Forth"])
        self.bpfPlayMode.SetSelection(0)
        self.bpfPlayMode.Bind(wx.EVT_CHOICE, self.bpfOnPlayMode)
        modeSizer.Add(modeText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        modeSizer.Add(self.bpfPlayMode, 0)

        sampleList = ["Parameter Values", "Interpolation Times"]
        interpButton = wx.RadioBox(panel, -1, "",
                                   wx.DefaultPosition,
                                   wx.DefaultSize, sampleList, 2,
                                   wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        interpButton.Bind(wx.EVT_RADIOBOX, self.bpfChangeParamMode)

        params = [["Dur (sec)", 1.0, interpTime, self.bpfOnDur],
                  ["Range Min", 0, interpTime, self.bpfOnMin],
                  ["Range Max", 1, interpTime, self.bpfOnMax]]
        self.bpfWidgets = []
        knobSizer = wx.BoxSizer(wx.HORIZONTAL)
        for param in params:
            numbox = wx.BoxSizer(wx.VERTICAL)
            label = wx.StaticText(panel, -1, label=param[0])
            ctrl = NumericCtrl(panel, value=param[1], interp=param[2],
                               size=(80, -1), callback=param[3])
            self.bpfWidgets.append(ctrl)
            numbox.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 2)
            numbox.Add(ctrl, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 2)
            knobSizer.Add(numbox, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        sizer.Add(headSizer, 0, wx.EXPAND)
        sizer.Add(self.bpfGrapher, 0, wx.EXPAND)
        sizer.Add(modeSizer, 0, wx.LEFT, 5)
        sizer.Add(interpButton, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(knobSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        panel.SetSizer(sizer)

    def bpfOnActivate(self, evt):
        self.bpfActive = evt.GetInt()
        self.callback()

    def bpfOnGrapher(self, evt):
        self.bpfFunction = evt.value
        self.callback()

    def bpfOnPlayMode(self, evt):
        self.bpfMode = evt.GetInt()
        self.callback()

    def bpfOnDur(self, value, interp):
        self.bpfDur, self.bpfDurInterp = value, interp
        self.callback()

    def bpfOnMin(self, value, interp):
        self.bpfMin, self.bpfMinInterp = value, interp
        self.callback()

    def bpfOnMax(self, value, interp):
        self.bpfMax, self.bpfMaxInterp = value, interp
        self.callback()

    def bpfChangeParamMode(self, evt):
        for widget in self.bpfWidgets:
            widget.changeMode(evt.GetInt())

    def getBpfAttributes(self):
        return {
                ID_BPF_ACTIVE: self.bpfActive,
                ID_BPF_DUR: self.bpfDur,
                ID_BPF_DUR_INTERP: self.bpfDurInterp,
                ID_BPF_MIN: self.bpfMin,
                ID_BPF_MIN_INTERP: self.bpfMinInterp,
                ID_BPF_MAX: self.bpfMax,
                ID_BPF_MAX_INTERP: self.bpfMaxInterp,
                ID_BPF_FUNCTION: self.bpfFunction,
                ID_BPF_MODE: self.bpfMode
                }

    def setBpfAttributes(self, dict):
        self.bpfActive = dict[ID_BPF_ACTIVE]
        self.bpfDur = dict[ID_BPF_DUR]
        self.bpfDurInterp = dict[ID_BPF_DUR_INTERP]
        self.bpfMin = dict[ID_BPF_MIN]
        self.bpfMinInterp = dict[ID_BPF_MIN_INTERP]
        self.bpfMax = dict[ID_BPF_MAX]
        self.bpfMaxInterp = dict[ID_BPF_MAX_INTERP]
        self.bpfFunction = dict[ID_BPF_FUNCTION]
        self.bpfMode = dict[ID_BPF_MODE]
        # Update graphical widgets
        self.bpfActiveCheck.SetValue(self.bpfActive)
        self.bpfWidgets[0].setValues(self.bpfDur, self.bpfDurInterp)
        self.bpfWidgets[1].setValues(self.bpfMin, self.bpfMinInterp)
        self.bpfWidgets[2].setValues(self.bpfMax, self.bpfMaxInterp)
        self.bpfGrapher.setValues(self.bpfFunction)
        self.bpfPlayMode.SetSelection(self.bpfMode)

    # Global setter and getter
    def getAttributes(self):
        dict = {}
        dict['mixmethod'] = self.mixingMethod
        dict['env'] = self.getEnvAttributes()
        dict['bpf'] = self.getBpfAttributes()
        return dict

    def setAttributes(self, dict):
        self.mixingMethod = dict.get('mixmethod', 0)
        self.method.SetSelection(self.mixingMethod)
        maps = {'env': self.setEnvAttributes,
                'bpf': self.setBpfAttributes}
        for key in dict.keys():
            if key in maps:
                maps[key](dict[key])
