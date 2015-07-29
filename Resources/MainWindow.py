import wx, time, os, pprint, copy, codecs, shutil, psutil
from constants import *
import QLiveLib
from AudioServer import AudioServer
from AudioMixer import AudioMixer
from FxTracks import FxTracks
from CuesPanel import ControlPanel, CuesPanel
from MixerPanel import MixerPanel
from IntroDialog import IntroDialog
from SoundFilePanel import SoundFilePanel

class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, pos=pos, size=size)
        
        self.SetMinSize((600, 400))
        self.SetTitle("QLive Session")

        # Status bar, the third field is unused yet.
        self.status = self.CreateStatusBar(3)
        self.status.SetStatusWidths([100, 100, -1])
        self.status.SetStatusText("CPU: 0.0 %", 0)
        self.status.SetStatusText("MEM: 0.00 Mb", 1)

        # Retrieve the current process
        self.process = psutil.Process()

        # Start a timer to update CPU and memory usage
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updateUsage, self.timer)
        self.timer.Start(1000)

        self.audioServer = AudioServer()
        QLiveLib.setVar("AudioServer", self.audioServer)

        self.saveState = None

        menubar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(wx.ID_NEW, "New\tCtrl+N")
        self.Bind(wx.EVT_MENU, self.onNew, id=wx.ID_NEW)        
        menu1.Append(wx.ID_OPEN, "Open\tCtrl+O")
        self.Bind(wx.EVT_MENU, self.onLoad, id=wx.ID_OPEN)
        self.submenu1 = wx.Menu()
        ID_OPEN_RECENT = 2000
        recentFiles = []
        filename = QLiveLib.ensureNFD(OPEN_RECENT_PATH)
        if os.path.isfile(filename):
            f = codecs.open(filename, "r", encoding="utf-8")
            for line in f.readlines():
                recentFiles.append(line.replace("\n", ""))
            f.close()
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
        if PLATFORM != "darwin":
            menu1.AppendSeparator()
        prefItem = menu1.Append(wx.ID_PREFERENCES, "Preferences...\tCtrl+;")
        self.Bind(wx.EVT_MENU, self.openPrefs, prefItem)
        if PLATFORM != "darwin":
            menu1.AppendSeparator()
        quitItem = menu1.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self.Bind(wx.EVT_MENU, self.OnClose, quitItem)
        menubar.Append(menu1, 'File')

        menu2 = wx.Menu()
        menu2.Append(NEW_TRACK_ID, "Add Track\tCtrl+T")
        self.Bind(wx.EVT_MENU, self.onNewTrack, id=NEW_TRACK_ID)        
        menu2.Append(DELETE_TRACK_ID, "Delete Track\tShift+Ctrl+D")
        self.Bind(wx.EVT_MENU, self.onDeleteTrack, id=DELETE_TRACK_ID)        
        menubar.Append(menu2, 'Tracks')

        menu3 = wx.Menu()
        menu3.AppendCheckItem(LINK_STEREO_ID, "Link Mixer Sliders\tCtrl+L")
        self.Bind(wx.EVT_MENU, self.onLinkSliders, id=LINK_STEREO_ID)        
        menubar.Append(menu3, 'Mixer')

        self.SetMenuBar(menubar)

        tabId = wx.NewId()
        self.prevId = wx.NewId()
        self.nextId = wx.NewId()
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL,  wx.WXK_TAB, tabId),
                                        (wx.ACCEL_NORMAL,  wx.WXK_LEFT, self.prevId),
                                        (wx.ACCEL_NORMAL,  wx.WXK_RIGHT, self.nextId)])
        self.SetAcceleratorTable(accel_tbl)
        
        self.Bind(wx.EVT_MENU, self.onTabulate, id=tabId)
        self.Bind(wx.EVT_MENU, self.onMoveCue, id=self.prevId, id2=self.nextId)

        self.mainPanel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.mainPanel.SetBackgroundColour(BACKGROUND_COLOUR)

        self.audioMixer = AudioMixer()
        QLiveLib.setVar("AudioMixer", self.audioMixer)

        self.controlPanel = ControlPanel(self.mainPanel)
        QLiveLib.setVar("ControlPanel", self.controlPanel)
        csize = self.controlPanel.GetSize()
        
        self.cues = CuesPanel(self.mainPanel, size=(csize[0], 1000))
        QLiveLib.setVar("CuesPanel", self.cues)

        splitter = wx.SplitterWindow(self.mainPanel, 
                                     style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)
        
        self.tracks = FxTracks(splitter)
        QLiveLib.setVar("FxTracks", self.tracks)

        self.soundfiles = SoundFilePanel(splitter)
        QLiveLib.setVar("Soundfiles", self.soundfiles)

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
        mem = self.process.get_memory_info()[0] / float(2 ** 20)
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
        else:
            if LOAD_DEFAULT_FILE:
                self.loadFile(NEW_FILE_PATH)
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

    def createProjectFolder(self, filepath):
        fil = os.path.basename(filepath)
        fld = os.path.splitext(fil)[0]
        dir = os.path.dirname(filepath)
        os.mkdir(os.path.join(dir, fld))
        os.mkdir(os.path.join(dir, fld, "doc"))
        os.mkdir(os.path.join(dir, fld, "sounds"))
        os.mkdir(os.path.join(dir, fld, "bounce"))
        flpath = os.path.join(dir, fld, fld+".qlp")
        shutil.copy(NEW_FILE_PATH, flpath)
        self.loadFile(flpath)

    def getCurrentState(self):
        dictSave = {}
        dictSave["tracks"] = self.tracks.getSaveDict()
        dictSave["cues"] = self.cues.getSaveDict()
        dictSave["mixer"] = self.mixer.getSaveDict()
        dictSave["soundfiles"] = self.soundfiles.getSaveState()
        dictSave["server"] = self.audioServer.getSaveState()
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
        self.tracks.setSaveState(self.saveState["tracks"])
        self.cues.setSaveDict(self.saveState["cues"])
        self.mixer.setSaveDict(self.saveState["mixer"])
        self.audioServer.setSaveState(self.saveState.get("server", {}))
        if "soundfiles" in self.saveState:
            self.soundfiles.setSaveState(self.saveState["soundfiles"])
        linkMenuItem = self.GetMenuBar().FindItemById(LINK_STEREO_ID)
        linkMenuItem.Check(dictSave["mixer"].get("inputLinked", False))

    def askForSaving(self):
        state = True
        if self.saveState != self.getCurrentState():
            if not QLiveLib.getVar("currentProject"):
                filename = "Untitled"
            else:
                filename = QLiveLib.getVar("currentProject")
            msg = 'file "%s" has been modified. Do you want to save?' % filename
            dlg = wx.MessageDialog(None, msg, 'Warning!', wx.YES | wx.NO | wx.CANCEL)
            but = dlg.ShowModal()
            if but == wx.ID_YES:
                self.onSave(None)
            elif but == wx.ID_CANCEL:
                state = False
            dlg.Destroy()
        return state
        
    def onNew(self, evt):
        if self.askForSaving():
            self.loadFile(NEW_FILE_PATH)

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
            filepath = os.path.join(os.path.expanduser("~"), "qlive_project.qlp")
            filepath = os.path.split(filepath)
        dlg = wx.FileDialog(self, "Save Qlive Projet", 
                            filepath[0], filepath[1],
                            "QLive Project files (*.qlp)|*.qlp",
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.saveFile(path)
        dlg.Destroy()
        
    def onNewTrack(self, evt):
        self.tracks.addTrack()

    def onDeleteTrack(self, evt):
        self.tracks.removeTrack()

    def onLinkSliders(self, evt):
        QLiveLib.getVar("MixerPanel").linkInputs(evt.GetInt())
        QLiveLib.getVar("MixerPanel").linkOutputs(evt.GetInt())

    def openPrefs(self, evt):
        print "Popup Preferences Windows..."

    def OnClose(self, evt):
        self.timer.Stop()
        if not self.askForSaving():
            return
        if self.audioServer.isStarted():
            self.audioServer.stop()
            time.sleep(0.25)
        if self.audioServer.isBooted():
            self.audioServer.shutdown()
            time.sleep(0.25)
        self.tracks.close()
        self.Destroy()
