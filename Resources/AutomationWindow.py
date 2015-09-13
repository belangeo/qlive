import wx
from constants import *
import QLiveLib
from Widgets import *

class AutomationWindow(wx.Frame):
    def __init__(self, parent, title):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, title=title, style=style)
        panel = AutomationPanel(self)
        self.Show()

class AutomationPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        cpstyle = wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        self.mixingMethod = 0

        title = wx.StaticText(self, label="Automation Controls")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                              wx.FONTWEIGHT_BOLD))

        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        methodLabel = wx.StaticText(self, -1, label="Multiple Automations Mixing Method:")
        self.method = wx.Choice(self, -1, choices=["Addition", "Multiplication", "Average"])
        self.method.SetSelection(0)
        self.method.Bind(wx.EVT_CHOICE, self.changeMixingMethod)
        headSizer.Add(methodLabel, 0, wx.RIGHT|wx.TOP, 5)
        headSizer.Add(self.method, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Collapsible Panes
        id = AUTOMATION_PANEL_FIRST_ID
        self.bpfCp = wx.CollapsiblePane(self, id, label="BPF", style=cpstyle)
        self.lfoCp = wx.CollapsiblePane(self, id+1, label="LFO", style=cpstyle)
        self.randCp = wx.CollapsiblePane(self, id+2, label="Random", style=cpstyle)
        self.envCp = wx.CollapsiblePane(self, id+3, label="Envelope Follower", style=cpstyle)
        self.MakeEnvPaneContent(self.envCp.GetPane())
        self.pitCp = wx.CollapsiblePane(self, id+4, label="Pitch Follower", style=cpstyle)
        self.zeroCp = wx.CollapsiblePane(self, id+5, label="Zero-Crossing", style=cpstyle)
        self.centCp = wx.CollapsiblePane(self, id+6, label="Centroid", style=cpstyle)

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, id=id, id2=id+6)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(headSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.bpfCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.lfoCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.randCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.envCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.pitCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.zeroCp, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.centCp, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

    def changeMixingMethod(self, evt):
        self.mixingMethod = evt.GetInt()

    def OnPaneChanged(self, evt):
        self.Layout()
        
    def MakeEnvPaneContent(self, panel):
        mainbox = wx.StaticBox(panel, -1, "")
        sizer = wx.StaticBoxSizer(mainbox, wx.VERTICAL)
        sizer.AddSpacer(5)

        headSizer = wx.BoxSizer(wx.HORIZONTAL)
        headSizer.AddStretchSpacer(1)
        self.active = wx.CheckBox(panel, -1, "Active:", style=wx.ALIGN_RIGHT)
        self.active.Bind(wx.EVT_CHECKBOX, self.activateEnv)
        headSizer.Add(self.active, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.envChannelChecks = []
        statbox = wx.StaticBox(panel, -1, "Input Selections")
        selectorSizer = wx.StaticBoxSizer(statbox, wx.HORIZONTAL)
        for i in range(NUM_INPUTS):
            check = wx.CheckBox(panel, -1, str(i))
            #check.Bind(wx.EVT_CHECKBOX, self.onCheckEnvInSelect)
            if i == 0:
                check.SetValue(1)
            self.envChannelChecks.append(check)
            selectorSizer.Add(check, 1, wx.EXPAND|wx.ALL, 5)

        interpLabel = wx.StaticText(panel, -1, label="Input Interpolation Time in Seconds: ")
        self.envSpin = wx.SpinCtrlDouble(panel, value='0.010', min=INTERPTIME_MIN, 
                                            max=INTERPTIME_MAX, inc=0.001, size=(100,-1))
        self.envSpin.SetDigits(3)
        interpSizer = wx.BoxSizer(wx.HORIZONTAL)
        interpSizer.Add(interpLabel, -1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        interpSizer.Add(self.envSpin)

        sampleList = ["Parameter Values", "Interpolation Times"]
        interpButton = wx.RadioBox(panel, -1, "", 
                                   wx.DefaultPosition,
                                   wx.DefaultSize, sampleList, 2, 
                                   wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        interpButton.Bind(wx.EVT_RADIOBOX, self.envChangeParamMode)

        params = [["Cutoff (Hz)", 20, 0.01], 
                  ["Range Min", 0, 0.01],
                  ["Range Max", 1, 0.01]]
        self.envWidgets = []
        knobSizer = wx.BoxSizer(wx.HORIZONTAL)
        for param in params:
            numbox = wx.BoxSizer(wx.VERTICAL)
            label = wx.StaticText(panel, -1, label=param[0])
            ctrl = NumericCtrl(panel, value=param[1], interp=param[2])
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

    def activateEnv(self, evt):
        print evt.GetInt()

    def envChangeParamMode(self, evt):
        for widget in self.envWidgets:
            widget.changeMode(evt.GetInt())
        
if __name__ == "__main__":
    app = wx.App()
    f = AutomationWindow(None, title="Test Automation Window")
    app.MainLoop()
