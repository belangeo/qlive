# encoding: utf-8
import wx
import QLiveLib

class CurrentCuePanel(wx.Frame):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX) & (~wx.MINIMIZE_BOX)
        wx.Frame.__init__(self, parent, title="Current Cue Window", style=style, size=(600, 600))
        self.SetBackgroundColour(wx.BLACK)

        # TODO: set text during the obj creation
        # TODO: auto adjust font size to the window size
        str = "0"
        self.text = wx.StaticText(self, -1, str)
        self.text.SetForegroundColour((255,255,255))
        font = wx.Font(450, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.text.SetFont(font)

        # Vertical/Horizontal centering
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.text, 1, wx.CENTER)
        sizer_v.Add(sizer_h, 1, wx.CENTER)
        self.SetSizer(sizer_v)

    def refresh(self, cue):
        wx.CallAfter(self.text.SetLabel, str(cue))
