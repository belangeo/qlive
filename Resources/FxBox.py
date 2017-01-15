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
import weakref
from constants import *
from fxbox_def import *
import QLiveLib
from FxView import FxSlidersView

class BaseFxBox(object):
    def __init__(self, parent):
        self.parent = parent
        self.name = ""
        self.category = ""
        self.audioRef = None
        self.id = [0,0]
        self.enable = 1
        self.view = None
        self.cues = {}
        self.copied = {}
        self.currentCue = 0
        self.i = 50 # increment factor for 'id' of the effects categories menu

    def setAudioRef(self, obj):
        if obj is None:
            self.audioRef = None
        else:
            self.audioRef = weakref.ref(obj)

    def getEnable(self):
        return self.enable

    def setInput(self, input):
        if self.audioRef is not None:
            audio = self.audioRef()
            audio.setInput(input)

    def getOutput(self):
        if self.audioRef is not None:
            audio = self.audioRef()
            return audio.getOutput()
        return None

    def setParamValue(self, name, value, fromUser):
        interpTime = QLiveLib.getVar("globalInterpTime")
        if self.audioRef is not None:
            audio = self.audioRef()
            if "gain" in name:
                value = pow(10, value * 0.05)
            if fromUser:
                getattr(audio, name).time = interpTime
            getattr(audio, name).value = value

    def setInterpValue(self, name, value):
        if self.audioRef is not None:
            audio = self.audioRef()
            getattr(audio, name).time = value

    def setEnable(self, x, fromUser=False):
        self.enable = x
        if self.audioRef is not None:
            audio = self.audioRef()
            audio.setEnable(x)
        if not fromUser and self.view is not None:
            self.view.setEnableState(x)

    def checkInChannel(self, which, state):
        self.inChannels[which] = state

    def getInChannels(self):
        return self.inChannels

    def setIsMultiChannels(self, state):
        self.isMultiChannels = state

    def getIsMultiChannels(self):
        return self.isMultiChannels

    def checkOutChannel(self, which, state):
        self.outChannels[which] = state

    def getOutChannels(self):
        return self.outChannels

    def setSoundfile(self, snd):
        self.soundfile = snd

    def getSoundfileId(self):
        if self.soundfile == "None":
            return None
        else:
            return int(self.soundfile) - 1

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setName(self, name):
        self.name = name

    def setCategory(self, category):
        self.category = category

    def openView(self):
        if self.view is not None:
            self.view.Show()

    def openMenu(self, event):
        fxTracks = QLiveLib.getVar("FxTracks")
        menu = wx.Menu()
        id = BOX_MENU_ITEM_FIRST_ID
        if self.isInput == False:
            for fxList in self.choices:
                id_orig = id
                subMenu = wx.Menu()
                for fx in fxList[1:]:
                    id += 1
                    subMenu.Append(id, fx)
                menu.AppendMenu(id_orig, fxList[0], subMenu)
                id = id_orig + self.i
        if self.isInput == True:
            for name in self.choices:
                menu.Append(id, name)
                id += 1
        fxTracks.Bind(wx.EVT_MENU, self.select,
                      id=BOX_MENU_ITEM_FIRST_ID, id2=id)
        fxTracks.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

    def select(self, evt):
        if self.isInput == False:
            # category is the [0] of each sublist inside FX_LIST
            categoryIndex = evt.GetId() % BOX_MENU_ITEM_FIRST_ID / self.i
            fxIndex = evt.GetId() % BOX_MENU_ITEM_FIRST_ID % self.i
            categorySelected = self.choices[categoryIndex][0]
            fxSelect = self.choices[categoryIndex][fxIndex]
            self.loadModule(categorySelected, fxSelect)

        if self.isInput == True:
            inputSelect = self.choices[evt.GetId() - BOX_MENU_ITEM_FIRST_ID]
            self.loadModule("", inputSelect)


    def loadModule(self, cat, name):
        self.category = cat
        self.name = name
        self.initModule()
        self.createView()
        currentCue = QLiveLib.getVar("CuesPanel").getCurrentCue()
        self.addCue(0)
        self.addCue(currentCue)

    def initModule(self):
        self.cues = {}
        if self.name == "AudioIn":
            self.inChannels = [1] + [0] * (NUM_INPUTS - 1)
            self.isMultiChannels = 0
        if self.name == "AudioOut":
            self.outChannels = [1] + [0] * (NUM_OUTPUTS - 1)
        if self.name == "Soundfile":
            self.soundfile = "None"

    def createView(self):
        if self.name:
            if self.isInput == False:
                parameters = self.module_dict[self.category][self.name]
            if self.isInput == True:
                parameters = self.module_dict[self.name]
            self.view = FxSlidersView(QLiveLib.getVar("MainWindow"),
                                      self, parameters)

    def delete(self):
        if self.view is not None:
            self.view.Destroy()
            self.view = None

    def getParams(self):
        if self.view is not None:
            widgets = self.view.getWidgets()
            params = [widget.getValue() for widget in widgets]
            inters = [widget.getInterpValue() for widget in widgets]
            paraDict = {"values": params,
                        "interps": inters,
                        "enable": self.enable}
            return paraDict
        else:
            return None

    def setParams(self, params):
        if self.view is not None and params is not None:
            widgets = self.view.getWidgets()
            values = params["values"]
            inters = params["interps"]
            for i, widget in enumerate(widgets):
                if widget.getMidiBinding() is None:
                    widget.setInterpValue(inters[i], propagate=True)
                    widget.setValue(values[i], propagate=True)
            self.setEnable(params["enable"])

    def getCurrentValues(self):
        if self.cues:
            if self.currentCue in self.cues:
                if self.cues[self.currentCue] is not None:
                    return self.cues[self.currentCue]["values"]
        return None

    def getCurrentInterps(self):
        if self.cues:
            if self.currentCue in self.cues:
                if self.cues[self.currentCue] is not None:
                    return self.cues[self.currentCue]["interps"]
        return None

    def setGlobalInterpTime(self, value, allcues, meth):
        if self.view is None:
            return
        widgets = self.view.getWidgets()
        num = len(widgets)
        if allcues:
            for cue in self.cues.keys():
                if meth == 0:
                    self.cues[cue]["interps"] = [value] * num
                elif meth == 1:
                    for i in range(num):
                        x = self.cues[cue]["interps"][i]
                        x += value
                        if x > INTERPTIME_MAX:
                            x = INTERPTIME_MAX
                        self.cues[cue]["interps"][i] = x
                elif meth == 2:
                    for i in range(num):
                        x = self.cues[cue]["interps"][i]
                        x -= value
                        if x < INTERPTIME_MIN:
                            x = INTERPTIME_MIN
                        self.cues[cue]["interps"][i] = x
        # sets the current cue
        for i, widget in enumerate(widgets):
            if meth == 0:
                widget.setInterpValue(value, propagate=True)
            elif meth == 1:
                x = widget.getInterpValue()
                x += value
                if x > INTERPTIME_MAX:
                    x = INTERPTIME_MAX
                widget.setInterpValue(x, propagate=True)
            elif meth == 2:
                x = widget.getInterpValue()
                x -= value
                if x < INTERPTIME_MIN:
                    x = INTERPTIME_MIN
                widget.setInterpValue(x, propagate=True)

    def saveCue(self):
        self.cues[self.currentCue] = self.getParams()

    def addCue(self, x):
        self.currentCue = x
        self.saveCue()

    def delCue(self, old, new):
        del self.cues[old]
        for i in range(old+1, len(self.cues)):
            if i in self.cues:
                self.cues[i-1] = self.cues[i]
                del self.cues[i]
        self.loadCue(new)

    def getCues(self):
        return self.cues

    def loadCue(self, x):
        if x in self.cues:
            self.setParams(self.cues[x])
        else:
            c = x
            while (c >= 0):
                if c in self.cues:
                    self.setParams(self.cues[c])
                    break
                c -= 1
        self.currentCue = x

    def copyCue(self):
        self.copied = copy.deepcopy(self.getParams())

    def pasteCue(self):
        self.cues[self.currentCue] = copy.deepcopy(self.copied)
        self.setParams(self.cues[self.currentCue])

    def cueEvent(self, evt):
        tp = evt.getType()
        if tp == CUE_TYPE_DELETE:
            self.delCue(evt.getOld(), evt.getCurrent())
        elif tp == CUE_TYPE_SELECT:
            self.saveCue()
            self.loadCue(evt.getCurrent())
        elif tp == CUE_TYPE_NEW:
            self.saveCue()
            self.addCue(evt.getCurrent())
        elif tp == CUE_TYPE_SAVE:
            self.saveCue()
        elif tp == CUE_TYPE_COPY:
            self.copyCue()
        elif tp == CUE_TYPE_PASTE:
            self.pasteCue()

    def getSaveDict(self):
        self.saveCue()
        dict = {'name': self.name,
                'category': self.category,
                'id': self.id,
                'cues': self.cues}
        if self.view is not None:
            widgets = self.view.getWidgets()
            midi = [widget.getMidiBinding() for widget in widgets]
            dict["midiBindings"] = midi
        if hasattr(self, "inChannels"):
            dict["inChannels"] = self.inChannels
            dict["isMultiChannels"] = self.isMultiChannels
        if hasattr(self, "outChannels"):
            dict["outChannels"] = self.outChannels
        if hasattr(self, "soundfile"):
            dict["soundfile"] = self.soundfile
        return dict

    def setSaveDict(self, saveDict):
        self.name = saveDict["name"]
        self.category = saveDict["category"]
        self.initModule()
        self.id = saveDict["id"]
        self.cues = saveDict["cues"]
        self.createView()
        if self.view is not None:
            midi = saveDict.get("midiBindings", None)
            if midi is not None:
                [widget.setMidiBinding(midi[i]) \
                    for i, widget in enumerate(self.view.getWidgets())]
            if hasattr(self, "inChannels"):
                self.inChannels = saveDict["inChannels"]
                self.view.setInChannelChecks(self.inChannels)
                self.isMultiChannels = saveDict["isMultiChannels"]
                self.view.setIsMultiChannels(self.isMultiChannels)
            if hasattr(self, "outChannels"):
                self.outChannels = saveDict["outChannels"]
                self.view.setOutChannelChecks(self.outChannels)
            if hasattr(self, "soundfile"):
                self.soundfile = saveDict.get("soundfile", "None")
                self.view.setSoundfile(self.soundfile)
        self.loadCue(0)

class FxBox(BaseFxBox):
    def __init__(self, parent):
        BaseFxBox.__init__(self, parent)
        self.module_dict = FX_DICT
        self.choices = FX_LIST
        self.isInput = False

    def getRect(self):
        x = TRACK_COL_SIZE * self.id[0] + 120
        y = TRACK_ROW_SIZE * self.id[1]  + self.parent.trackPosition + 5
        return wx.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

class InputBox(BaseFxBox):
    def __init__(self, parent):
        BaseFxBox.__init__(self, parent)
        self.module_dict = INPUT_DICT
        self.choices = INPUT_LIST
        self.isInput = True

    def getRect(self):
        x = 30
        y = TRACK_ROW_SIZE * self.id[1] + self.parent.trackPosition + 5
        return wx.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
