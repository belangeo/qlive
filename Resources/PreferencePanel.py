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
#TODO: add dynamic parameters panel for each audio driver (as in cecilia)
class AudioPrefsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Setting audio driver
        audioDriverDefault = QLiveLib.getVar("audioHostAPI")
        audioDriverChoices = AUDIO_DRIVERS
        audioDriverLabel = wx.StaticText(self, -1, "Audio driver:")
        self.audioDriverCB = wx.ComboBox(self, -1, audioDriverDefault, wx.DefaultPosition,
                         (140, -1), audioDriverChoices,
                         wx.CB_READONLY
                         | wx.TE_PROCESS_ENTER
                         )
        self.audioDriverCB.Bind(wx.EVT_COMBOBOX, self.setAudioDriver, self.audioDriverCB)

        # Setting buffer size
        bufferSizeDefault = QLiveLib.getVar("bufferSize")
        bufferSizeChoices = ['64','128','256','512','1024','2048']
        bufferSizeLabel = wx.StaticText(self, -1, "Buffer size:")
        self.bufferSizeCB = wx.ComboBox(self, -1, bufferSizeDefault, wx.DefaultPosition,
                         (140, -1), bufferSizeChoices,
                         wx.CB_READONLY
                         | wx.TE_PROCESS_ENTER
                         )
        self.bufferSizeCB.Bind(wx.EVT_COMBOBOX, self.setBufferSize, self.bufferSizeCB)

        # Main box
        box = wx.StaticBox(self, -1, "Audio settings")

        # Sizers
        vsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        hsizerAudioDriver = wx.BoxSizer(wx.HORIZONTAL)
        hsizerBufferSize  = wx.BoxSizer(wx.HORIZONTAL)

        hsizerAudioDriver.Add(audioDriverLabel, -1, wx.ALL|wx.ALIGN_CENTER, 5)
        hsizerAudioDriver.Add(self.audioDriverCB, -1, wx.ALL, 5)

        hsizerBufferSize.Add(bufferSizeLabel, -1, wx.ALL|wx.ALIGN_CENTER , 5)
        hsizerBufferSize.Add(self.bufferSizeCB, -1, wx.ALL, 5)

        vsizer.AddSpacer(10)
        vsizer.Add(hsizerAudioDriver, 0, wx.ALL|wx.EXPAND, 0)
        vsizer.Add(hsizerBufferSize, 0, wx.ALL|wx.EXPAND, 0)

        border = wx.BoxSizer()
        border.Add(vsizer, -1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(border)

    def setAudioDriver(self, evt):
        QLiveLib.setVar("audioHostAPI", evt.GetString())

    def setBufferSize(self, evt):
        QLiveLib.setVar("bufferSize", evt.GetString())

#TODO: needs better var names
class PreferenceFrame(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, title="QLive Preferences", style=style, size=(300, 250))
        self.parent = parent

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create the tab windows
        tab1 = GeneralPrefsTab(nb)
        tab2 = AudioPrefsTab(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "General")
        nb.AddPage(tab2, "Audio")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
