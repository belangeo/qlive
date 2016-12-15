# encoding: utf-8
"""
Copyright 2016 (Pierre Michaud, Olivier Belanger, Tiago Bortoletto Vaz)

This file is part of QLive, a cues-based software to help the 
creation of mixed music.

QLive is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

QLive is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with QLive.  If not, see <http://www.gnu.org/licenses/>.

"""
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
