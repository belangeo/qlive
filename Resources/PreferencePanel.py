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
#TODO: add parameters panel for each audio driver (as in cecilia)
class AudioPrefsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        box = wx.StaticBox(self, -1, "Audio settings")
        self.t = wx.StaticText(self, -1, "Audio Driver:", wx.DefaultPosition)
        self.audioDriverCB = wx.ComboBox(self, 500, QLiveLib.getVar("audioHostAPI"), wx.DefaultPosition,
                         (140, -1), AUDIO_DRIVERS,
                         wx.CB_READONLY
                         | wx.TE_PROCESS_ENTER
                         )
        self.Bind(wx.EVT_COMBOBOX, self.setAudioDriver, self.audioDriverCB)

        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL, )
        bsizer.Add(self.t, 0, wx.TOP|wx.LEFT, 10)
        bsizer.Add(self.audioDriverCB, 0, wx.TOP|wx.LEFT, 10)

        border = wx.BoxSizer()
        border.Add(bsizer, -1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(border)

    def setAudioDriver(self, evt):
        QLiveLib.setVar("audioHostAPI", evt.GetString())

#TODO: needs better var names
class PreferenceFrame(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, title="QLive Preferences", style=style, size=(450, 250))
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
