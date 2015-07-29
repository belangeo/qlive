#!/usr/bin/env python
# encoding: utf-8
import wx, sys
from types import ListType
import Resources.QLiveLib as QLiveLib
from Resources.MainWindow import MainWindow

class QLiveApp(wx.App):
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        X, Y = wx.DisplaySize()
        if X < 1000:
            sizex = X - 40
        else:
            sizex = 1000
        if Y < 670:
            sizey = Y - 40
        else:
            sizey = 670
        self.filenames = []
        self.frame = MainWindow(pos=(20, 20), size=(sizex, sizey))
        QLiveLib.setVar("MainWindow", self.frame)
        if self.filenames:
            self.frame.loadFile(QLiveLib.ensureNFD(self.filenames[0]))
            
    def MacOpenFiles(self, filenames):
        if type(filenames) != ListType:
            filenames = [filenames]
        self.filenames = filenames

    def MacReopenApp(self):
        try:
            self.frame.Raise()
        except:
            pass

if __name__ == "__main__":
    qlfile = None
    if len(sys.argv) > 1:
        qlfile = sys.argv[1]
    app = QLiveApp()
    if qlfile:
        wx.CallAfter(app.frame.loadFile, QLiveLib.ensureNFD(qlfile))
    app.MainLoop()
