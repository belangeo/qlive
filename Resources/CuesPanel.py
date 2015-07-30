#!/usr/bin/env python
# encoding: utf-8
import wx
import wx.lib.scrolledpanel as scrolled
from constants import *
import QLiveLib
from Widgets import TransportButtons, CueButton, QLiveControlKnob

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
        self.newButton.SetToolTip(wx.ToolTip('Add a new cue'))
        self.newAddSizer.Add(self.newButton, 1)

        bmp = wx.Bitmap(ICON_DELETE, wx.BITMAP_TYPE_PNG)
        self.delButton = wx.BitmapButton(self, wx.ID_ANY, bmp)
        self.delButton.Bind(wx.EVT_BUTTON, self.onDelCue)
        self.newAddSizer.Add(self.delButton, 1)

        self.mainSizer.Add(self.newAddSizer, 0, wx.EXPAND|wx.ALL, 5)

        self.upbmp = wx.Bitmap(ICON_ARROW_UP, wx.BITMAP_TYPE_PNG)
        self.upmidbmp = wx.Bitmap(ICON_ARROW_UP_MIDI, wx.BITMAP_TYPE_PNG)
        self.upButton = wx.BitmapButton(self, wx.ID_ANY, self.upbmp)
        self.upButton.Bind(wx.EVT_BUTTON, self.onMoveCueUp)
        self.upButton.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        self.upTooltip = wx.ToolTip("")
        self.upButton.SetToolTip(self.upTooltip)
        self.upDownSizer.Add(self.upButton, 1)

        self.downbmp = wx.Bitmap(ICON_ARROW_DOWN, wx.BITMAP_TYPE_PNG)
        self.downmidbmp = wx.Bitmap(ICON_ARROW_DOWN_MIDI, wx.BITMAP_TYPE_PNG)
        self.downButton = wx.BitmapButton(self, wx.ID_ANY, self.downbmp)
        self.downButton.Bind(wx.EVT_BUTTON, self.onMoveCueDown)
        self.downButton.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        self.downTooltip = wx.ToolTip("")
        self.downButton.SetToolTip(self.downTooltip)
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

    def moveCueFromMidi(self, which):
        if which == "up":
            wx.CallAfter(QLiveLib.getVar("CuesPanel").onMoveCueUp)
        elif which == "down":
            wx.CallAfter(QLiveLib.getVar("CuesPanel").onMoveCueDown)

    def midiLearn(self, evt):
        obj = evt.GetEventObject()
        if self.learnButton is not None and self.learnButton != obj:
            if self.learnButton == self.upButton:
                wx.CallAfter(self.learnButton.SetBitmapLabel, self.upbmp)
            elif self.learnButton == self.downButton:
                wx.CallAfter(self.learnButton.SetBitmapLabel, self.downbmp)
        server = QLiveLib.getVar("AudioServer")
        if self.learnButton == obj:
            if obj == self.upButton:
                obj.SetBitmapLabel(self.upbmp)
            elif obj == self.downButton:
                obj.SetBitmapLabel(self.downbmp)
            self.learnButton = None
            server.stopCueMidiLearn()
        else:
            if obj == self.upButton:
                obj.SetBitmapLabel(self.upmidbmp)
            elif obj == self.downButton:
                obj.SetBitmapLabel(self.downmidbmp)
            self.learnButton = obj
            if obj == self.upButton:
                which = "up"
            elif obj == self.downButton:
                which = "down"
            server.setCueMidiLearnState(which)
            server.startCueMidiLearn()

    def setButtonTooltip(self, which, tip):
        if which == "up":
            self.upTooltip.SetTip(tip)
        elif which == "down":
            self.downTooltip.SetTip(tip)
        
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
        self.setSelectedCue(0)

    def getSaveDict(self):
        dict = {}
        dict["numberOfCues"] = len(self.cueButtons)
        return dict
