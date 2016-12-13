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
        self.Bind(wx.EVT_SIZE, self.OnSize)

        label = "0"
        self.text = wx.StaticText(self, -1, label)
        self.text.SetForegroundColour((255,255,255))

        # Vertical/Horizontal centering
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.text, 1, wx.CENTER)
        sizer_v.Add(sizer_h, 1, wx.CENTER)
        self.SetSizer(sizer_v)

    def OnSize(self, evt):
        self.adjustPointSize()
        evt.Skip()

    def adjustPointSize(self):
        w, h = self.GetSize()
        label = self.text.GetLabel()
        tw, th = self.text.GetTextExtent(label)
        font = self.text.GetFont()
        if th < h:
            while (th < h):
                font.SetPointSize(font.GetPointSize()+1)
                self.text.SetFont(font)
                tw, th = self.text.GetTextExtent(label)
        else:
            while (th > h):
                font.SetPointSize(font.GetPointSize()-1)
                self.text.SetFont(font)
                tw, th = self.text.GetTextExtent(label)

    def close(self, evt):
        menubar = self.parent.GetMenuBar()
        item = menubar.FindItemById(VIEW_CUE_WINDOW_ID)
        item.Check(False)
        self.Hide()

    def refresh(self, cue):
        wx.CallAfter(self.text.SetLabel, str(cue))
