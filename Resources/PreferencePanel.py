# encoding: utf-8

import wx
import QLiveLib
from constants import *

class GeneralPrefsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.tooltipsCheckBox = wx.CheckBox(self, -1, "Use tooltips", style=wx.ALIGN_RIGHT)
        self.tooltipsCheckBox.SetValue(QLiveLib.getVar("useTooltips"))
        self.Bind(wx.EVT_CHECKBOX, self.enableTooltips, self.tooltipsCheckBox)

        box = wx.StaticBox(self, -1, "General settings")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL, )
        bsizer.Add(self.tooltipsCheckBox, 0, wx.TOP|wx.LEFT, 10)

        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(border)

    def enableTooltips(self, state):
        QLiveLib.setVar("useTooltips", state.GetEventObject().GetValue())

#TODO: needs better GUI design
class AudioPrefsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.reinit_server = False

        # Setting audio driver
        audioDriverDefault = QLiveLib.getVar("audio")
        audioDriverLabel = wx.StaticText(self, -1, "Audio driver:")
        self.audioDriverCB = wx.ComboBox(self, -1, audioDriverDefault, wx.DefaultPosition,
                         wx.DefaultSize, AUDIO_DRIVERS, wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.audioDriverCB.Bind(wx.EVT_COMBOBOX, self.setAudioDriver, self.audioDriverCB)

        # Portaudio: Audio Input devices
        self.inputDeviceLabel = wx.StaticText(self, -1, "Audio Input (portaudio):")

        availableAudioIns = []
        for d in QLiveLib.getVar("availableAudioInputs"):
            availableAudioIns.append(QLiveLib.ensureNFD(d))
        initInput = QLiveLib.ensureNFD(QLiveLib.getVar("audioInput"))
        self.inputDeviceCB = wx.ComboBox(self, -1, initInput, wx.DefaultPosition,
                         wx.DefaultSize, availableAudioIns, wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.inputDeviceCB.Bind(wx.EVT_COMBOBOX, self.setInputDevice, self.inputDeviceCB)

        # Portaudio: Audio Output devices
        self.outputDeviceLabel = wx.StaticText(self, -1, "Audio Output (portaudio):")
        availableAudioOuts = []
        for d in QLiveLib.getVar("availableAudioOutputs"):
            availableAudioOuts.append(QLiveLib.ensureNFD(d))
        initOutput = QLiveLib.ensureNFD(QLiveLib.getVar("audioOutput"))
        self.outputDeviceCB = wx.ComboBox(self, -1, initOutput, wx.DefaultPosition,
                         wx.DefaultSize, availableAudioOuts, wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.outputDeviceCB.Bind(wx.EVT_COMBOBOX, self.setOutputDevice, self.outputDeviceCB)

        # First physical input device
        self.firstPhysicalInputLabel = wx.StaticText(self, -1, "First Physical Input:")

        initPysicalInput = QLiveLib.ensureNFD(str(QLiveLib.getVar("defaultFirstInput")))
        self.firstPhysicalInputCB = wx.ComboBox(self, -1, initPysicalInput, wx.DefaultPosition,
                         wx.DefaultSize, [str(x) for x in range(36)], wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.firstPhysicalInputCB.Bind(wx.EVT_COMBOBOX, self.setFirstPhysicalInput, self.firstPhysicalInputCB)

        # First physical output device
        self.firstPhysicalOutputLabel = wx.StaticText(self, -1, "First Physical Output:")

        initPysicalOutput = QLiveLib.ensureNFD(str(QLiveLib.getVar("defaultFirstOutput")))
        self.firstPhysicalOutputCB = wx.ComboBox(self, -1, initPysicalOutput, wx.DefaultPosition,
                         wx.DefaultSize, [str(x) for x in range(36)], wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.firstPhysicalOutputCB.Bind(wx.EVT_COMBOBOX, self.setFirstPhysicalOutput, self.firstPhysicalOutputCB)

        # Setting buffer size
        bufferSizeDefault = QLiveLib.getVar("bufferSize")
        bufferSizeLabel = wx.StaticText(self, -1, "Buffer size:")
        self.bufferSizeCB = wx.ComboBox(self, -1, bufferSizeDefault, wx.DefaultPosition,
                         wx.DefaultSize, BUFFER_SIZES, wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.bufferSizeCB.Bind(wx.EVT_COMBOBOX, self.setBufferSize, self.bufferSizeCB)

        # Setting sampling rate
        samplingRateDefault = QLiveLib.getVar("sr")
        samplingRateLabel = wx.StaticText(self, -1, "Sampling rate:")
        self.samplingRateCB = wx.ComboBox(self, -1, samplingRateDefault, wx.DefaultPosition,
                         wx.DefaultSize, SAMPLE_RATES, wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.samplingRateCB.Bind(wx.EVT_COMBOBOX, self.setSamplingRate, self.samplingRateCB)

        # Setting duplex True/False
        duplexDefault = QLiveLib.getVar("duplex")
        duplexLabel = wx.StaticText(self, -1, "Duplex:")
        self.duplexCB = wx.CheckBox(self, -1, "", style=wx.ALIGN_LEFT)
        self.duplexCB.SetValue(bool(int(QLiveLib.getVar("duplex"))))
        self.duplexCB.Bind(wx.EVT_CHECKBOX, self.setDuplex, self.duplexCB)

        # Main box
        box = wx.StaticBox(self, -1, "Audio settings")

        # Sizers
        vsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        hsizerAudioDriver = wx.BoxSizer(wx.HORIZONTAL)
        hsizerInputDevice = wx.BoxSizer(wx.HORIZONTAL)
        hsizerOutputDevice = wx.BoxSizer(wx.HORIZONTAL)
        hsizerFirstPhysicalInput = wx.BoxSizer(wx.HORIZONTAL)
        hsizerFirstPhysicalOutput = wx.BoxSizer(wx.HORIZONTAL)
        hsizerBufferSize  = wx.BoxSizer(wx.HORIZONTAL)
        hsizerSamplingRate  = wx.BoxSizer(wx.HORIZONTAL)
        hsizerDuplex  = wx.BoxSizer(wx.HORIZONTAL)

        hsizerAudioDriver.Add(audioDriverLabel, -1, wx.ALL|wx.ALIGN_CENTER, 3)
        hsizerAudioDriver.Add(self.audioDriverCB, -1, wx.ALL, 3)

        hsizerInputDevice.Add(self.inputDeviceLabel, -1, wx.ALL|wx.ALIGN_CENTER, 3)
        hsizerInputDevice.Add(self.inputDeviceCB, -1, wx.ALL, 3)

        hsizerOutputDevice.Add(self.outputDeviceLabel, -1, wx.ALL|wx.ALIGN_CENTER, 3)
        hsizerOutputDevice.Add(self.outputDeviceCB, -1, wx.ALL, 3)

        hsizerFirstPhysicalInput.Add(self.firstPhysicalInputLabel, -1, wx.ALL|wx.ALIGN_CENTER, 3)
        hsizerFirstPhysicalInput.Add(self.firstPhysicalInputCB, -1, wx.ALL, 3)

        hsizerFirstPhysicalOutput.Add(self.firstPhysicalOutputLabel, -1, wx.ALL|wx.ALIGN_CENTER, 3)
        hsizerFirstPhysicalOutput.Add(self.firstPhysicalOutputCB, -1, wx.ALL, 3)

        hsizerBufferSize.Add(bufferSizeLabel, -1, wx.ALL|wx.ALIGN_CENTER , 3)
        hsizerBufferSize.Add(self.bufferSizeCB, -1, wx.ALL, 3)

        hsizerSamplingRate.Add(samplingRateLabel, -1, wx.ALL|wx.ALIGN_CENTER , 3)
        hsizerSamplingRate.Add(self.samplingRateCB, -1, wx.ALL, 3)

        hsizerDuplex.Add(duplexLabel, -1, wx.ALL|wx.ALIGN_CENTER , 3)
        hsizerDuplex.Add(self.duplexCB, -1, wx.ALL, 3)

        vsizer.AddSpacer(5)
        vsizer.Add(wx.StaticText(self, -1, "The changes will be effective when the preferences will be closed."), 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(5)
        vsizer.Add(hsizerAudioDriver, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerInputDevice, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerOutputDevice, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerFirstPhysicalInput, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerFirstPhysicalOutput, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerBufferSize, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerSamplingRate, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerDuplex, 0, wx.ALL|wx.EXPAND, 0)

        border = wx.BoxSizer()
        border.Add(vsizer, -1, wx.EXPAND|wx.ALL, 5)
        self.SetSizerAndFit(border)

        self.EnableDisablePortaudioOpts()

    def EnableDisablePortaudioOpts(self):
        if QLiveLib.getVar("audio") in ["portaudio", "coreaudio"]:
            enablePortaudioOpts = True
        else:
            enablePortaudioOpts = False
        self.inputDeviceCB.Enable(enablePortaudioOpts)
        self.inputDeviceLabel.Enable(enablePortaudioOpts)
        self.outputDeviceCB.Enable(enablePortaudioOpts)
        self.outputDeviceLabel.Enable(enablePortaudioOpts)

    def setAudioDriver(self, evt):
        if QLiveLib.getVar("audio") != evt.GetString():
            self.reinit_server = True
        QLiveLib.setVar("audio", evt.GetString())
        self.EnableDisablePortaudioOpts()

    def setInputDevice(self, evt):
        if QLiveLib.getVar("audioInput") != evt.GetString():
            self.reinit_server = True
        QLiveLib.setVar("audioInput", evt.GetString())

    def setOutputDevice(self, evt):
        if QLiveLib.getVar("audioOutput") != evt.GetString():
            self.reinit_server = True
        QLiveLib.setVar("audioOutput", evt.GetString())

    def setFirstPhysicalInput(self, evt):
        if QLiveLib.getVar("defaultFirstInput") != int(evt.GetString()):
            self.reinit_server = True
        QLiveLib.setVar("defaultFirstInput", int(evt.GetString()))

    def setFirstPhysicalOutput(self, evt):
        if QLiveLib.getVar("defaultFirstOutput") != int(evt.GetString()):
            self.reinit_server = True
        QLiveLib.setVar("defaultFirstOutput", int(evt.GetString()))

    def setBufferSize(self, evt):
        if QLiveLib.getVar("bufferSize") != evt.GetString():
            self.reinit_server = True
        QLiveLib.setVar("bufferSize", evt.GetString())

    def setSamplingRate(self, evt):
        if QLiveLib.getVar("sr") != evt.GetString():
            self.reinit_server = True
        QLiveLib.setVar("sr", evt.GetString())

    def setDuplex(self, state):
        if state.GetEventObject().GetValue() == True:
            QLiveLib.setVar("duplex", "1")
        else:
            QLiveLib.setVar("duplex", "0")
        self.reinit_server = True

#TODO: needs better var names
class PreferenceFrame(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, title="QLive Preferences", style=style, size=(500, 350))
        self.parent = parent

        # Create a panel and notebook (tabs holder)
        panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        closeButton = wx.Button(panel, -1, label="Close")
        closeButton.Bind(wx.EVT_BUTTON, self.onClose)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Create the tab windows
        self.tab1 = AudioPrefsTab(nb)
        tab2 = GeneralPrefsTab(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(self.tab1, "Audio")
        nb.AddPage(tab2, "General")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 0, wx.EXPAND)
        sizer.Add(closeButton, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizerAndFit(sizer)
        Y = panel.GetSize()[1]
        self.SetSize((500, Y+35))

    def onClose(self, evt):
        if self.tab1.reinit_server:
            try:
                QLiveLib.getVar("AudioServer").reinitServer()
            except:
                pass
        self.Destroy()

