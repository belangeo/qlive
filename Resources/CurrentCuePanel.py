# encoding: utf-8
import wx
import QLiveLib
from constants import *

class CurrentCuePanel(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Current Cue Window",
                          size=(600, 600))
        self.parent = parent
        self.SetBackgroundColour(wx.BLACK)
        self.Bind(wx.EVT_CLOSE, self.close)

        # TODO: set text during the obj creation
        # TODO: auto adjust font size to the window size
        str = "0"
        self.text = wx.StaticText(self, -1, str)
        self.text.SetForegroundColour((255,255,255))
        font = wx.Font(450, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_BOLD)
        self.text.SetFont(font)

        # Vertical/Horizontal centering
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.text, 1, wx.CENTER)
        sizer_v.Add(sizer_h, 1, wx.CENTER)
        self.SetSizer(sizer_v)

    def close(self, evt):
        menubar = self.parent.GetMenuBar()
        item = menubar.FindItemById(VIEW_CUE_WINDOW_ID)
        item.Check(False)
        self.Hide()

    def refresh(self, cue):
        wx.CallAfter(self.text.SetLabel, str(cue))