#!/usr/bin/env python
# encoding: utf-8
import wx
import wx.lib.scrolledpanel as scrolled
from constants import *
import QLiveLib
from Widgets import TransportButtons, CueButton, QLiveControlKnob, QLiveTooltip

# TODO: This class needs revision... 
class SetInterpTimeDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, size = (200, 120))
        panel = wx.Panel(self)

        knob = QLiveControlKnob(self, 0.01, 300, pos = (5,5))
        
        button = wx.Button(self,label="set All" , pos = (60, 65))
        button.Bind(wx.EVT_BUTTON, self.onSetAll)

    def onSetAll(self, e):
        value = knob.GetValue()
        if QLiveLib.getVar("MainWindow") != None:
            pass
#            QLiveLib.getVar("FxTracks").cueEvent(value)
        self.Close()

class CueEvent:
    def __init__(self, type, current, old, total):
        self.type = type
        self.current = current
        self.old = old
        self.total = total

    def getType(self):
        return self.type

    def getCurrent(self):
        return self.current

    def getOld(self):
        return self.old

    def getTotal(self):
        return self.total

class ControlPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(95, -1), style=wx.SUNKEN_BORDER)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.newAddSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.upDownSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.learnButton = None
        self.midiBindings = {}

        server = QLiveLib.getVar("AudioServer")
        self.buttons = TransportButtons(self, 
                                        playCallback=server.start,
                                        recordCallback=server.record)
        self.mainSizer.Add(self.buttons, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.mainSizer.Add(wx.StaticLine(self, size=(1, 1)), 0, 
                           wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)        

        title = wx.StaticText(self, label="-- CUES --")
        self.mainSizer.Add(title, 0, wx.ALIGN_CENTER, 5)

        #button = wx.Button(self,wx.ID_OK, label="Interp Time" )
        #self.mainSizer.Add(button, 0, wx.ALIGN_CENTER, 5)
        #button.Bind(wx.EVT_BUTTON, self.onSetInterpTime)

        bmp = wx.Bitmap(ICON_ADD, wx.BITMAP_TYPE_PNG)
        self.newButton = wx.BitmapButton(self, wx.ID_ANY, bmp)
        self.newButton.Bind(wx.EVT_BUTTON, self.onNewCue)
        self.newButton.SetToolTip(QLiveTooltip('Add a new cue'))
        self.newAddSizer.Add(self.newButton, 1)

        bmp = wx.Bitmap(ICON_DELETE, wx.BITMAP_TYPE_PNG)
        self.delButton = wx.BitmapButton(self, wx.ID_ANY, bmp)
        self.delButton.Bind(wx.EVT_BUTTON, self.onDelCue)
        self.delButton.SetToolTip(QLiveTooltip('Remove current cue'))
        self.newAddSizer.Add(self.delButton, 1)

        self.mainSizer.Add(self.newAddSizer, 0, wx.EXPAND|wx.ALL, 5)

        self.upbmp = wx.Bitmap(ICON_ARROW_UP, wx.BITMAP_TYPE_PNG)
        self.upmidbmp = wx.Bitmap(ICON_ARROW_UP_MIDI, wx.BITMAP_TYPE_PNG)
        self.upButton = wx.BitmapButton(self, wx.ID_ANY, self.upbmp)
        self.upButton.Bind(wx.EVT_BUTTON, self.onMoveCueUp)
        self.upButton.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        self.upButton.SetToolTip(QLiveTooltip('Move cue up'))
        self.upDownSizer.Add(self.upButton, 1)

        self.downbmp = wx.Bitmap(ICON_ARROW_DOWN, wx.BITMAP_TYPE_PNG)
        self.downmidbmp = wx.Bitmap(ICON_ARROW_DOWN_MIDI, wx.BITMAP_TYPE_PNG)
        self.downButton = wx.BitmapButton(self, wx.ID_ANY, self.downbmp)
        self.downButton.Bind(wx.EVT_BUTTON, self.onMoveCueDown)
        self.downButton.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        self.downButton.SetToolTip(QLiveTooltip('Move cue down'))
        self.upDownSizer.Add(self.downButton, 1)

        self.mainSizer.Add(self.upDownSizer, 0, 
                           wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        self.SetSizerAndFit(self.mainSizer)

    def onDelCue(self, evt):
        QLiveLib.getVar("CuesPanel").onDelCue()

    def onNewCue(self, evt):
        QLiveLib.getVar("CuesPanel").onNewCue()

    def onMoveCueUp(self, evt):
        QLiveLib.getVar("CuesPanel").onMoveCueUp()

    def onMoveCueDown(self, evt):
        QLiveLib.getVar("CuesPanel").onMoveCueDown()

    def midi(self, pitch, vel):
        which = self.midiBindings[pitch]
        if which == "up":
            wx.CallAfter(QLiveLib.getVar("CuesPanel").onMoveCueUp)
        elif which == "down":
            wx.CallAfter(QLiveLib.getVar("CuesPanel").onMoveCueDown)

    def getMidiScan(self, num, midichnl):
        if num != -1:
            if self.learnButton == self.upButton:
                which = "up"
            elif self.learnButton == self.downButton:
                which = "down"
            self.assignMidiCtl(num, which)
        self.resetCueButtonBackgroundColour()

    def assignMidiCtl(self, num, which):
        self.midiBindings[num] = which
        if which == "up":
            self.upButton.SetToolTip(QLiveTooltip("Midi key: %d" % num))
        elif which == "down":
            self.downButton.SetToolTip(QLiveTooltip("Midi key: %d" % num))
        QLiveLib.getVar("MidiServer").bind("noteon", num, self.midi)

    def midiLearn(self, evt):
        obj = evt.GetEventObject()
        midi = QLiveLib.getVar("MidiServer")
        # remove current binding
        if evt.ShiftDown():
            num = -1
            if obj == self.upButton:
                search, bitmap = "up", self.upbmp
            elif obj == self.downButton:
                search, bitmap = "down", self.downbmp
            for key, val in self.midiBindings.items():
                if val == search:
                    num = key
                    break
            obj.SetBitmapLabel(bitmap)
            obj.SetToolTip(QLiveTooltip(""))
            midi.noteonscan(None)
            self.learnButton = None
            if num != -1:
                midi.unbind("noteon", num)
        # stop midi learn
        elif self.learnButton == obj:
            if obj == self.upButton:
                obj.SetBitmapLabel(self.upbmp)
            elif obj == self.downButton:
                obj.SetBitmapLabel(self.downbmp)
            self.learnButton = None
            midi.noteonscan(None)
        # start midi learn
        else:
            if obj == self.upButton:
                obj.SetBitmapLabel(self.upmidbmp)
            elif obj == self.downButton:
                obj.SetBitmapLabel(self.downmidbmp)
            midi.noteonscan(self.getMidiScan)
            self.learnButton = obj
        
    def resetCueButtonBackgroundColour(self):
        if self.learnButton is not None:
            if self.learnButton == self.upButton:
                wx.CallAfter(self.learnButton.SetBitmapLabel, self.upbmp)
            elif self.learnButton == self.downButton:
                wx.CallAfter(self.learnButton.SetBitmapLabel, self.downbmp)
            self.learnButton = None
        
    def onSetInterpTime(self, e):
        panel = SetInterpTimeDialog()
        panel.ShowModal()

    def getSaveState(self):
        return {"midiBindings": self.midiBindings}

    def setSaveState(self, state):
        if state:
            self.midiBindings = {}
            for key, val in state["midiBindings"].items():
                self.assignMidiCtl(key, val)

class CuesPanel(scrolled.ScrolledPanel):
    def __init__(self, parent=None, size=(95, 500)):
        scrolled.ScrolledPanel.__init__(self, parent, size=size, 
                                        style=wx.SUNKEN_BORDER)

        self.currentCue = 0
        self.cueButtons = []

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)

        self.appendCueButton()

    def setSelectedCue(self, number):
        if number >= 0 and number < len(self.cueButtons):
            if self.currentCue < len(self.cueButtons):
                self.cueButtons[self.currentCue].select(False)
            self.cueButtons[number].select(True)
            self.currentCue = number
            self.SetupScrolling(scroll_x=False, scrollToTop=False)
            self.mainSizer.Layout()
            self.ScrollChildIntoView(self.cueButtons[self.currentCue])
            return True
        else:
            return False
        
    def clearButtons(self):
        for button in self.cueButtons:
            self.mainSizer.Remove(button)
            button.Destroy()
        self.cueButtons = []
        self.mainSizer.Layout()

    def appendCueButton(self):
        number = len(self.cueButtons)
        butHeight = self.GetTextExtent("9")[1] + 8
        but = CueButton(self, size=(50, butHeight), number=number, 
                        evtHandler=self.onCueSelection)
        self.mainSizer.Add(but, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        self.cueButtons.append(but)
        self.setSelectedCue(number)

    def sendCueEvent(self, evt):
        if QLiveLib.getVar("MainWindow") != None:
            QLiveLib.getVar("FxTracks").cueEvent(evt)
            QLiveLib.getVar("Soundfiles").cueEvent(evt)

    def onCueSelection(self, x):
        old = self.currentCue
        if self.setSelectedCue(x):
            evt = CueEvent(type=CUE_TYPE_SELECT, current=self.currentCue, 
                           old=old, total=len(self.cueButtons))
            self.sendCueEvent(evt)

    def loadCurrentCue(self):
            evt = CueEvent(type=CUE_TYPE_SELECT, current=self.currentCue, 
                           old=None, total=len(self.cueButtons))
            self.sendCueEvent(evt)
        
    def onDelCue(self):
        button = self.cueButtons.pop(self.currentCue)
        button.Destroy()
        self.mainSizer.Layout()
        if len(self.cueButtons) == 0:
            self.appendCueButton()
        for i, but in enumerate(self.cueButtons):
            but.setNumber(i)
        deletedCue = self.currentCue
        if self.currentCue > 0:
            selection = self.currentCue - 1
        else:
            selection = 0
        if self.setSelectedCue(selection):
            evt = CueEvent(type=CUE_TYPE_DELETE, current=self.currentCue, 
                           old=deletedCue, total=len(self.cueButtons))
            self.sendCueEvent(evt)

    def onSaveCue(self):
        evt = CueEvent(type=CUE_TYPE_SAVE, current=self.currentCue, 
                       old=None, total=len(self.cueButtons))
        self.sendCueEvent(evt)
        
    def onNewCue(self):
        old = self.currentCue
        self.appendCueButton()
        evt = CueEvent(type=CUE_TYPE_NEW, current=self.currentCue, 
                       old=old, total=len(self.cueButtons))
        self.sendCueEvent(evt)
        
    def getNumberOfCues(self):
        return len(self.cueButtons)
        
    def getCurrentCue(self):
        return self.currentCue
        
    def onMoveCueUp(self):
        self.onCueSelection(self.currentCue - 1)

    def onMoveCueDown(self):
        self.onCueSelection(self.currentCue + 1)

    def setSaveDict(self, dict):
        self.clearButtons()
        for i in range(dict["numberOfCues"]):
            self.appendCueButton()
        if "buttons" in dict:
            for i, d in enumerate(dict["buttons"]):
                self.cueButtons[i].setSaveDict(d)
        self.setSelectedCue(0)

    def getSaveDict(self):
        dict = {}
        dict["numberOfCues"] = len(self.cueButtons)
        dict["buttons"] = [but.getSaveDict() for but in self.cueButtons]
        return dict
