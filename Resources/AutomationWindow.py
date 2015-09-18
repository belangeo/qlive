import wx
from constants import *
import QLiveLib
from Widgets import *

# TODO: Need to handle cues from keys here.

class AutomationWindow(wx.Frame):
    def __init__(self, parent, title, object=None, closeCallback=None):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Frame.__init__(self, parent, -1, title=title, style=style)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.closeCallback = closeCallback
        self.panel = AutomationPanel(self, object)
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
    def __init__(self, parent, object=None):
        wx.Panel.__init__(self, parent, -1)
        cpstyle = wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE
        self.SetBackgroundColour(BACKGROUND_COLOUR)

        # parameter object reference
        self.object = object

        # global attributes
        self.mixingMethod = 0
        
        # envelope follower attributes
        self.envActive = 0
        self.envInputs = [0] * NUM_INPUTS
        self.envInputsInterp = 0.01
        self.envThreshold, self.envThresholdInterp = -90, 0.01
        self.envCutoff, self.envCutoffInterp = 20, 0.01
        self.envMin, self.envMinInterp = 0.0, 0.01
        self.envMax, self.envMaxInterp = 1.0, 0.01
        

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
        self.envActiveCheck = wx.CheckBox(panel, -1, "Active:", style=wx.ALIGN_RIGHT)
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

        interpLabel = wx.StaticText(panel, -1, label="Input Interpolation Time in Seconds: ")
        self.envInInterpSpin = wx.SpinCtrlDouble(panel, value='0.010', min=INTERPTIME_MIN, 
                                            max=INTERPTIME_MAX, inc=0.001, size=(100,-1))
        self.envInInterpSpin.SetDigits(3)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.envOnInputsInterp, self.envInInterpSpin)
        interpSizer = wx.BoxSizer(wx.HORIZONTAL)
        interpSizer.Add(interpLabel, -1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        interpSizer.Add(self.envInInterpSpin)

        sampleList = ["Parameter Values", "Interpolation Times"]
        interpButton = wx.RadioBox(panel, -1, "", 
                                   wx.DefaultPosition,
                                   wx.DefaultSize, sampleList, 2, 
                                   wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        interpButton.Bind(wx.EVT_RADIOBOX, self.envChangeParamMode)

        params = [["Threshold (dB)", -90, 0.01, self.envOnThresh],
                  ["Cutoff (Hz)", 20, 0.01, self.envOnCutoff], 
                  ["Range Min", 0, 0.01, self.envOnMin],
                  ["Range Max", 1, 0.01, self.envOnMax]]
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

    def envOnCheckInputs(self, evt):
        state = evt.GetInt()
        obj = evt.GetEventObject()
        which = int(obj.GetLabel()) - 1
        self.envInputs[which] = state

    def envOnInputsInterp(self, evt):
        self.envInputsInterp = self.envInInterpSpin.GetValue()

    def envOnThresh(self, value, interp):
        self.envThreshold, self.envThresholdInterp = value, interp

    def envOnCutoff(self, value, interp):
        self.envCutoff, self.envCutoffInterp = value, interp

    def envOnMin(self, value, interp):
        self.envMin, self.envMinInterp = value, interp

    def envOnMax(self, value, interp):
        self.envMax, self.envMaxInterp = value, interp

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
        self.envInInterpSpin.SetValue(self.envInputsInterp)
        self.envWidgets[0].setValues(self.envThreshold, self.envThresholdInterp)
        self.envWidgets[1].setValues(self.envCutoff, self.envCutoffInterp)
        self.envWidgets[2].setValues(self.envMin, self.envMinInterp)
        self.envWidgets[3].setValues(self.envMax, self.envMaxInterp)

    def getAttributes(self):
        dict = {}
        dict['mixmethod'] = self.mixingMethod
        dict['env'] = self.getEnvAttributes()
        return dict
        
    def setAttributes(self, dict):
        self.mixingMethod = dict.get('mixmethod', 0)
        self.method.SetSelection(self.mixingMethod)
        maps = {'env': self.setEnvAttributes}
        for key in dict.keys():
            if key in maps:
                maps[key](dict[key])

if __name__ == "__main__":
    app = wx.App()
    f = AutomationWindow(None, title="Test Automation Window")
    app.MainLoop()
