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
import wx, time, os, pprint, copy, codecs, shutil, psutil
from constants import *
import QLiveLib
from AudioServer import AudioServer, MidiServer
from AudioMixer import AudioMixer
from FxTracks import FxTracks
from CuesPanel import ControlPanel, CuesPanel, InterpTimeFrame
from MixerPanel import MixerPanel
from IntroDialog import IntroDialog
from SoundFilePanel import SoundFilePanel
from PreferencePanel import PreferenceFrame
from CurrentCuePanel import CurrentCuePanel

class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, pos=pos, size=size)

        self.SetMinSize((600, 400))
        self.SetTitle("QLive Session")

        # Status bar, the third field is unused yet.
        self.status = self.CreateStatusBar(3)
        self.status.SetStatusWidths([100, 150, -1])
        self.status.SetStatusText("CPU: 0.0 %", 0)
        self.status.SetStatusText("MEM: 0.00 Mb", 1)

        # Retrieve the current process
        self.process = psutil.Process()

        # Start a timer to update CPU and memory usage
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updateUsage, self.timer)
        self.timer.Start(1000)

        # Query & load available Audio and MIDI drivers
        QLiveLib.queryAudioMidiDrivers()

        self.audioServer = AudioServer()
        QLiveLib.setVar("AudioServer", self.audioServer)
        self.midiServer = MidiServer()
        QLiveLib.setVar("MidiServer", self.midiServer)

        self.saveState = None

        menubar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(wx.ID_NEW, "New\tCtrl+N")
        self.Bind(wx.EVT_MENU, self.onNew, id=wx.ID_NEW)
        menu1.Append(wx.ID_OPEN, "Open\tCtrl+O")
        self.Bind(wx.EVT_MENU, self.onLoad, id=wx.ID_OPEN)
        self.submenu1 = wx.Menu()
        ID_OPEN_RECENT = 2000
        recentFiles = QLiveLib.getRecentFiles()
        if recentFiles:
            for file in recentFiles:
                self.submenu1.Append(ID_OPEN_RECENT, file)
                self.Bind(wx.EVT_MENU, self.openRecent, id=ID_OPEN_RECENT)
                ID_OPEN_RECENT += 1
        menu1.AppendMenu(1999, "Open Recent...", self.submenu1)
        menu1.AppendSeparator()
        menu1.Append(wx.ID_CLOSE, "Close\tCtrl+W")
        self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_CLOSE)
        menu1.Append(wx.ID_SAVE, "Save\tCtrl+S")
        self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
        menu1.Append(wx.ID_SAVEAS, "Save As...\tShift+Ctrl+S")
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=wx.ID_SAVEAS)
        menu1.Append(EXPORT_MEI_ID, "Export MEI...\tShift+Ctrl+M")
        self.Bind(wx.EVT_MENU, self.onExportMEI, id=EXPORT_MEI_ID)
        if not PYMEI:
            menu1.Enable(EXPORT_MEI_ID, False)
        if PLATFORM != "darwin":
            menu1.AppendSeparator()
        prefItem = menu1.Append(wx.ID_PREFERENCES, "Preferences...\tCtrl+;")
        self.Bind(wx.EVT_MENU, self.openPrefs, prefItem)
        if PLATFORM != "darwin":
            menu1.AppendSeparator()
        quitItem = menu1.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)
        menubar.Append(menu1, 'File')

        menu4 = wx.Menu()
        menu4.Append(CUE_CUT_ID, "Cut Cue\tCtrl+X")
        self.Bind(wx.EVT_MENU, self.onCueCut, id=CUE_CUT_ID)
        menu4.Append(CUE_COPY_ID, "Copy Cue\tCtrl+C")
        self.Bind(wx.EVT_MENU, self.onCueCopy, id=CUE_COPY_ID)
        menu4.Append(CUE_PASTE_ID, "Paste Cue\tCtrl+V")
        self.Bind(wx.EVT_MENU, self.onCuePaste, id=CUE_PASTE_ID)
        menubar.Append(menu4, 'Cues')

        menu2 = wx.Menu()
        menu2.Append(NEW_TRACK_ID, "Add Track\tCtrl+T")
        self.Bind(wx.EVT_MENU, self.onNewTrack, id=NEW_TRACK_ID)
        menu2.Append(DELETE_TRACK_ID, "Delete Track\tShift+Ctrl+D")
        self.Bind(wx.EVT_MENU, self.onDeleteTrack, id=DELETE_TRACK_ID)
        menubar.Append(menu2, 'Tracks')

        menu3 = wx.Menu()
        menu3.AppendCheckItem(MIDI_LEARN_ID, "Midi Learn Mode\tShift+Ctrl+M")
        self.Bind(wx.EVT_MENU, self.onMidiLearn, id=MIDI_LEARN_ID)
        menu3.AppendSeparator()
        menu3.Append(INTERP_TIME_ID, "Set Global Interpolation Time\tCtrl+G")
        self.Bind(wx.EVT_MENU, self.onNewInterpTime, id=INTERP_TIME_ID)
        menu3.AppendSeparator()
        menu3.AppendCheckItem(VIEW_CUE_WINDOW_ID,
                              "Show Current Cue Window\tShift+Ctrl+C")
        self.Bind(wx.EVT_MENU, self.onViewCurrentCue, id=VIEW_CUE_WINDOW_ID)
        menu3.AppendSeparator()
        menu3.AppendCheckItem(LINK_STEREO_ID, "Link Mixer Sliders\tCtrl+L")
        self.Bind(wx.EVT_MENU, self.onLinkSliders, id=LINK_STEREO_ID)
        menubar.Append(menu3, 'Actions')

        self.SetMenuBar(menubar)

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
        accel_tbl = wx.AcceleratorTable(
                            [(wx.ACCEL_NORMAL,  wx.WXK_TAB, tabId),
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

        self.Bind(wx.EVT_MENU, self.onTabulate, id=tabId)
        self.Bind(wx.EVT_MENU, self.onMoveCue, id=KEY_EVENT_FIRST_ID,
                  id2=KEY_EVENT_FIRST_ID+100)

        self.mainPanel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.mainPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        self.audioMixer = AudioMixer()
        QLiveLib.setVar("AudioMixer", self.audioMixer)

        self.controlPanel = ControlPanel(self.mainPanel)
        QLiveLib.setVar("ControlPanel", self.controlPanel)
        csize = self.controlPanel.GetSize()

        self.cues = CuesPanel(self.mainPanel, size=(csize[0], 1000))
        QLiveLib.setVar("CuesPanel", self.cues)

        self.currentCueWindow = CurrentCuePanel(self)
        QLiveLib.setVar("CurrentCueWindow", self.currentCueWindow)

        splitter = wx.SplitterWindow(self.mainPanel,
                                     style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)

        self.soundfiles = SoundFilePanel(splitter)
        QLiveLib.setVar("Soundfiles", self.soundfiles)

        self.tracks = FxTracks(splitter)
        QLiveLib.setVar("FxTracks", self.tracks)

        splitter.SetMinimumPaneSize(60)
        splitter.SplitHorizontally(self.tracks, self.soundfiles, 350)

        self.mixer = MixerPanel(self.mainPanel, self.audioMixer)
        QLiveLib.setVar("MixerPanel", self.mixer)

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlSizer.Add(self.controlPanel, 0)
        self.controlSizer.Add(self.cues, 1, wx.EXPAND)
        self.rightSizer.Add(splitter, 1, wx.EXPAND, 5)
        self.rightSizer.Add(self.mixer, 0, wx.EXPAND, 5)
        self.mainSizer.Add(self.controlSizer, 0)
        self.mainSizer.AddSizer(self.rightSizer, 2, wx.EXPAND, 5)
        self.mainPanel.SetSizer(self.mainSizer)

        wx.CallAfter(self.showIntro)

    def updateUsage(self, evt):
        cpu = self.process.cpu_percent()
        self.status.SetStatusText("CPU: %.1f %%" % cpu, 0)
        mem = self.process.memory_info()[0] / float(2 ** 20)
        self.status.SetStatusText("MEM: %.2f Mb" % mem, 1)

    def showIntro(self):
        dlg = IntroDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.filepath
            createDir = dlg.createDir
            if createDir:
                self.createProjectFolder(filepath)
            else:
                self.loadFile(filepath)
        dlg.Destroy()
        self.Show()

    def onTabulate(self, evt):
        QLiveLib.getVar("FxTracks").setSelectedTrack()

    def onMoveCue(self, evt):
        if QLiveLib.getVar("CanProcessCueKeys"):
            cues = QLiveLib.getVar("CuesPanel")
            current = cues.getCurrentCue()
            if evt.GetId() == self.prevId:
                cues.onCueSelection(current - 1)
            elif evt.GetId() == self.nextId:
                cues.onCueSelection(current + 1)
            elif evt.GetId() == self.cueZeroId:
                cues.onCueSelection(0)
            elif evt.GetId() >= self.cue1Id and evt.GetId() <= self.cue10Id:
                which = evt.GetId() - self.cue1Id + 1
                cues.onCueSelection(which)
        else:
            evt.Skip()

    def createProjectFolder(self, filepath):
        fil = os.path.basename(filepath)
        fld = os.path.splitext(fil)[0]
        dir = os.path.dirname(filepath)
        fldpath = os.path.join(dir, fld)
        if os.path.isdir(fldpath):
            shutil.rmtree(fldpath)
        os.mkdir(fldpath)
        os.mkdir(os.path.join(fldpath, "doc"))
        os.mkdir(os.path.join(fldpath, "sounds"))
        os.mkdir(os.path.join(fldpath, "bounce"))
        flpath = os.path.join(fldpath, fld+".qlp")
        shutil.copy(NEW_FILE_PATH, flpath)
        self.loadFile(flpath)

    def getCurrentState(self):
        dictSave = {}
        dictSave["tracks"] = self.tracks.getSaveDict()
        dictSave["cues"] = self.cues.getSaveDict()
        dictSave["mixer"] = self.mixer.getSaveDict()
        dictSave["soundfiles"] = self.soundfiles.getSaveState()
        dictSave["control"] = self.controlPanel.getSaveState()
        #dictSave["server"] = self.audioServer.getSaveState()
        return dictSave

    def saveFile(self, path):
        QLiveLib.getVar("CuesPanel").onSaveCue()
        dictSave = self.getCurrentState()
        self.saveState = copy.deepcopy(dictSave)
        QLiveLib.setVar("currentProject", path)
        QLiveLib.setVar("projectFolder", os.path.dirname(path))
        with open(path, "w") as f:
            f.write(QLIVE_MAGIC_LINE)
            f.write("### %s ###\n" % APP_VERSION)
            f.write("dictSave = %s" % pprint.pformat(dictSave, indent=4))

    def saveMEI(self, path):
        QLiveLib.saveMEI(path)

    def loadFile(self, path):
        with open(path, "r") as f:
            magicline = f.readline()
        if magicline != QLIVE_MAGIC_LINE:
            print "The file loaded is not a valid QLive file."
            return
        self.tracks.close()
        execfile(path, globals())
        if path == NEW_FILE_PATH:
            QLiveLib.setVar("currentProject", "")
            QLiveLib.setVar("projectFolder", "")
        else:
            QLiveLib.setVar("currentProject", path)
            QLiveLib.setVar("projectFolder", os.path.dirname(path))
            self.newRecent(path)
        self.saveState = copy.deepcopy(dictSave)
        self.soundfiles.setSaveState(self.saveState.get("soundfiles", []))
        self.tracks.setSaveState(self.saveState["tracks"])
        self.cues.setSaveDict(self.saveState["cues"])
        self.mixer.setSaveDict(self.saveState["mixer"])
        self.controlPanel.setSaveState(self.saveState.get("control", {}))
        #self.audioServer.setSaveState(self.saveState.get("server", {}))
        linkMenuItem = self.GetMenuBar().FindItemById(LINK_STEREO_ID)
        linkMenuItem.Check(dictSave["mixer"].get("inputLinked", False))

    def askForSaving(self):
        state = True
        if self.saveState != self.getCurrentState():
            if not QLiveLib.getVar("currentProject"):
                fname = "Untitled"
            else:
                fname = QLiveLib.getVar("currentProject")
            msg = 'file "%s" has been modified. Do you want to save?' % fname
            dlg = wx.MessageDialog(None, msg, 'Warning!',
                                   wx.YES|wx.NO|wx.CANCEL)
            but = dlg.ShowModal()
            if but == wx.ID_YES:
                self.onSave(None)
            elif but == wx.ID_CANCEL:
                state = False
            dlg.Destroy()
        return state

    def onNew(self, evt):
        if self.askForSaving():
            QLiveLib.getVar("Soundfiles").cleanUpSoundsFolder()
            self.Hide()
            self.showIntro()

    def onLoad(self, evt):
        if not self.askForSaving():
            return
        if QLiveLib.getVar("currentProject"):
            filepath = os.path.split(QLiveLib.getVar("currentProject"))[0]
        else:
            filepath = os.path.expanduser("~")
        dlg = wx.FileDialog(self, "Open Qlive Projet", filepath, "",
                            "QLive Project files (*.qlp)|*.qlp", style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.loadFile(path)
        dlg.Destroy()

    def openRecent(self, event):
        menu = self.GetMenuBar()
        id = event.GetId()
        file = menu.FindItemById(id).GetLabel()
        if self.askForSaving():
            self.loadFile(file)

    def newRecent(self, file):
        filename = QLiveLib.ensureNFD(OPEN_RECENT_PATH)
        try:
            f = codecs.open(filename, "r", encoding="utf-8")
            lines = [line.replace("\n", "") for line in f.readlines()]
            f.close()
        except:
            lines = []
        if not file in lines:
            f = codecs.open(filename, "w", encoding="utf-8")
            lines.insert(0, file)
            if len(lines) > 20:
                lines = lines[0:20]
            for line in lines:
                f.write(line + '\n')
            f.close()
        subId = 2000
        if lines != []:
            for item in self.submenu1.GetMenuItems():
                self.submenu1.DeleteItem(item)
            for file in lines:
                self.submenu1.Append(subId, QLiveLib.toSysEncoding(file))
                subId += 1

    def onClose(self, evt):
        self.onNew(None)

    def onSave(self, evt):
        if not QLiveLib.getVar("currentProject"):
            self.onSaveAs(None)
        else:
            self.saveFile(QLiveLib.getVar("currentProject"))

    def onSaveAs(self, evt):
        if QLiveLib.getVar("currentProject"):
            filepath = os.path.split(QLiveLib.getVar("currentProject"))
        else:
            filepath = os.path.join(os.path.expanduser("~"),
                                    "qlive_project.qlp")
            filepath = os.path.split(filepath)
        dlg = wx.FileDialog(self, "Save Qlive Projet",
                            filepath[0], filepath[1],
                            "QLive Project files (*.qlp)|*.qlp",
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.saveFile(path)
        dlg.Destroy()

    def onExportMEI(self, evt):
        if QLiveLib.getVar("currentProject"):
            filepath = os.path.split(QLiveLib.getVar("currentProject"))
        else:
            filepath = os.path.join(os.path.expanduser("~"),
                                    "qlive_project.mei")
            filepath = os.path.split(filepath)
        dlg = wx.FileDialog(self, "Export Qlive Projet in MEI format",
                            filepath[0], os.path.splitext(filepath[1])[0]+".mei",
                            "MEI files (*.mei)|*.mei",
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.saveMEI(path)
        dlg.Destroy()


    def onNewTrack(self, evt):
        self.tracks.addTrack()

    def onDeleteTrack(self, evt):
        self.tracks.removeTrack()

    def onMidiLearn(self, evt):
        QLiveLib.setVar("MidiLearnMode", evt.GetInt())
        if evt.GetInt():
            QLiveLib.getVar("MixerPanel").SetBackgroundColour(MIDILEARN_COLOUR)
            QLiveLib.setVar("CanProcessCueKeys", False)
        else:
            QLiveLib.getVar("MixerPanel").SetBackgroundColour(BACKGROUND_COLOUR)
            QLiveLib.setVar("CanProcessCueKeys", True)

    def onNewInterpTime(self, evt):
        self.globalInterpTimeWindow = InterpTimeFrame(self,
                                                      self.setGlobalInterpTime)

    def setGlobalInterpTime(self, cue, track, snd, value, meth):
        #print cue, track, snd, value, meth
        if track < 2:
            self.tracks.setTracksGlobalInterpTime(value, cue, track, meth)
        if snd < 2:
            self.soundfiles.setGlobalInterpTime(value, cue, snd, meth)

    def onLinkSliders(self, evt):
        QLiveLib.getVar("MixerPanel").linkInputs(evt.GetInt())
        QLiveLib.getVar("MixerPanel").linkOutputs(evt.GetInt())

    def onCueCut(self, evt):
        cues = QLiveLib.getVar("CuesPanel")
        current = cues.getCurrentCue()
        if current == 0:
            QLiveLib.PRINT("Can't cut cue number 0.")
            return
        cues.onCopyCue()
        cues.onDelCue()

    def onCueCopy(self, evt):
        cues = QLiveLib.getVar("CuesPanel")
        current = cues.getCurrentCue()
        if current == 0:
            QLiveLib.PRINT("Can't copy cue number 0.")
            return
        cues.onCopyCue()

    def onCuePaste(self, evt):
        cues = QLiveLib.getVar("CuesPanel")
        current = cues.getCurrentCue()
        if current == 0:
            QLiveLib.PRINT("Can't paste on cue number 0.")
            return
        cues.onPasteCue()

    def onViewCurrentCue(self, evt):
        if evt.GetInt() == 1:
            self.currentCueWindow.Show()
        if evt.GetInt() == 0:
            self.currentCueWindow.Hide()

    def openPrefs(self, evt):
        self.prefs = PreferenceFrame(self)
        self.prefs.Show()
        self.prefs.Center()

    def OnQuit(self, evt):
        self.timer.Stop()
        if not self.askForSaving():
            return
        self.currentCueWindow.Destroy()
        if self.audioServer.isStarted():
            self.audioServer.stop()
            time.sleep(0.25)
        if self.audioServer.isBooted():
            self.audioServer.shutdown()
            time.sleep(0.25)
        QLiveLib.getVar("Soundfiles").cleanUpSoundsFolder()
        QLiveLib.saveVars()
        self.tracks.close()
        self.Destroy()