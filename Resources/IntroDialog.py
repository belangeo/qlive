import wx, textwrap, sys
from constants import *
import QLiveLib

class IntroDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "QLive Intro",
                           size=wx.DefaultSize, pos=wx.DefaultPosition,
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.Bind(wx.EVT_CLOSE, self.onQuit)

        self.filepath = ""
        self.createDir = False

        sizer = wx.BoxSizer(wx.VERTICAL)

        msg = "Choose a QLive project to open or create a new one..."
        label = wx.StaticText(self, -1, msg)
        sizer.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 10)

        box = wx.BoxSizer(wx.HORIZONTAL)

        openbut = wx.Button(self, wx.ID_OPEN)
        self.Bind(wx.EVT_BUTTON, self.open, id=wx.ID_OPEN)
        box.Add(openbut, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 25)

        newbut = wx.Button(self, wx.ID_NEW)
        self.Bind(wx.EVT_BUTTON, self.new, id=wx.ID_NEW)
        box.Add(newbut, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 25)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        hsizerRecentFiles = wx.BoxSizer(wx.HORIZONTAL)

        recentFiles = QLiveLib.getRecentFiles()
        self.recentFilesLabel = wx.StaticText(self, -1, "Recent projects: ")
        self.recentFilesLabel.Disable()
        self.recentFilesChoice = wx.Choice(self, -1, choices=recentFiles,
                                           size=(350,-1))
        self.recentFilesChoice.Disable()
        self.recentFilesChoice.Bind(wx.EVT_CHOICE, self.openRecent)
        hsizerRecentFiles.Add(self.recentFilesLabel, 0,
                              wx.LEFT|wx.ALIGN_CENTER, 10)
        hsizerRecentFiles.Add(self.recentFilesChoice, 1,
                              wx.TOP|wx.BOTTOM|wx.RIGHT, 10)

        sizer.Add(hsizerRecentFiles, 0, wx.ALL|wx.EXPAND, 0)

        box = wx.BoxSizer(wx.HORIZONTAL)
        self.pathtext = wx.StaticText(self, -1, "")
        box.Add(self.pathtext, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM, 15)

        sizer.Add(box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)


        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.TOP,25)

        btnsizer = wx.StdDialogButtonSizer()

        self.okbtn = wx.Button(self, wx.ID_OK)
        self.okbtn.Disable()
        btnsizer.AddButton(self.okbtn)

        # set the most recent project as default for one click action
        if recentFiles:
            self.recentFilesLabel.Enable()
            self.recentFilesChoice.Enable()
            self.okbtn.Enable()
            self.filepath = recentFiles[0]
            self.createDir = False
            self.showPath(self.filepath)
            focusbutton = self.okbtn
            self.recentFilesChoice.SetSelection(0)
        else:
            focusbutton = openbut

        btnsizer.Realize()

        sizer.Add(btnsizer, 0,
                  wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 5)

        if PLATFORM == "darwin":
            focusbutton.SetDefault()
        else:
            focusbutton.SetFocus()

        self.SetSizer(sizer)
        sizer.Fit(self)

    def onQuit(self, evt):
        self.Destroy()
        sys.exit()

    def showPath(self, path):
        w, _ = self.GetSize()
        if PLATFORM == "darwin" or PLATFORM.startswith("linux"):
            tw, _ = self.GetTextExtent("a")
            n = w / tw
        else:
            tw, _ = self.GetTextExtent("O")
            n = w / (tw + 1)
        head = "Selected Project:\n\n"
        path = textwrap.fill(path, n)
        self.pathtext.SetLabel(head+path)

    def openRecent(self, evt):
        self.filepath = evt.GetString()
        self.createDir = False
        self.showPath(self.filepath)
        if self.filepath != "":
            self.okbtn.Enable()
        if PLATFORM == "darwin":
            self.okbtn.SetDefault()
        else:
            self.okbtn.SetFocus()

    def open(self, evt):
        dlg = wx.FileDialog(self,
                            "Open Qlive Projet",
                            os.path.expanduser("~"),
                            "",
                            "QLive Project files (*.qlp)|*.qlp",
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.recentFilesLabel.Disable()
            self.recentFilesChoice.Disable()
            self.filepath = dlg.GetPath()
            self.createDir = False
            self.showPath(self.filepath)
            if self.filepath != "":
                self.okbtn.Enable()
        dlg.Destroy()
        if PLATFORM == "darwin":
            self.okbtn.SetDefault()
        else:
            self.okbtn.SetFocus()

    def new(self, evt):
        dlg = wx.FileDialog(self,
                            "Create Qlive Projet Folder",
                            os.path.expanduser("~"),
                            "newproject",
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.recentFilesLabel.Disable()
            self.recentFilesChoice.Disable()
            self.filepath = dlg.GetPath()
            self.createDir = True
            self.showPath(self.filepath)
            if self.filepath != "":
                self.okbtn.Enable()
        dlg.Destroy()
        if PLATFORM == "darwin":
            self.okbtn.SetDefault()
        else:
            self.okbtn.SetFocus()