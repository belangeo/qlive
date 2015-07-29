import wx, textwrap
from constants import *

class IntroDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "QLive Intro", 
                           size=wx.DefaultSize, pos=wx.DefaultPosition, 
                           style=wx.DEFAULT_DIALOG_STYLE)

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

        box = wx.BoxSizer(wx.HORIZONTAL)
        self.pathtext = wx.StaticText(self, -1, "")
        box.Add(self.pathtext, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.BOTTOM, 25)

        sizer.Add(box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line,0,wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP,25)

        btnsizer = wx.StdDialogButtonSizer()

        self.okbtn = wx.Button(self, wx.ID_OK)
        btnsizer.AddButton(self.okbtn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, 
                  wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def showPath(self, path):
        w, _ = self.GetSize()
        tw, _ = self.GetTextExtent("O")
        n = w / (tw + 1)
        head = "Selected Project:\n\n"
        path = textwrap.fill(path, n) 
        self.pathtext.SetLabel(head+path)

    def open(self, evt):
        dlg = wx.FileDialog(self, 
                            "Open Qlive Projet", 
                            os.path.expanduser("~"), 
                            "",
                            "QLive Project files (*.qlp)|*.qlp", 
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()
            self.createDir = False
            self.showPath(self.filepath)
        dlg.Destroy()
        self.okbtn.SetFocus()
    
    def new(self, evt):
        dlg = wx.FileDialog(self, 
                            "Create Qlive Projet Folder", 
                            os.path.expanduser("~"), 
                            "newproject", 
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()
            self.createDir = True
            self.showPath(self.filepath)
        dlg.Destroy()
        self.okbtn.SetFocus()

if __name__ == "__main__":
    class TestWindow(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, pos=(350,500), size=(1000,250))
            dlg = IntroDialog(self)
            dlg.ShowModal()
            dlg.Destroy()
    app = wx.App()
    frame = TestWindow()
    frame.Show()
    app.MainLoop()