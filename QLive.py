#!/usr/bin/env python
# encoding: utf-8
import sys
import wx
import Resources.QLiveLib as QLiveLib
from Resources.MainWindow import MainWindow

class QLiveApp(wx.App):
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        X, Y = wx.DisplaySize()
        sizex, sizey = 1100, 670
        if X < 1000:
            sizex = X - 40
        if Y < 670:
            sizey = Y - 40
        self.frame = MainWindow(pos=(20, 20), size=(sizex, sizey))
        QLiveLib.setVar("MainWindow", self.frame)
        if hasattr(self, "filenames"):
            self.frame.loadFile(QLiveLib.ensureNFD(self.filenames[0]))
            
    def MacOpenFiles(self, filenames):
        if type(filenames) != list:
            filenames = [filenames]
        self.filenames = filenames

    def MacReopenApp(self):
        try:
            self.frame.Raise()
        except:
            pass

if __name__ == "__main__":

    QLiveLib.loadVars()
    qlfile = None
    if len(sys.argv) > 1:
        qlfile = sys.argv[1]

    app = QLiveApp()
    if qlfile:
        wx.CallAfter(app.frame.loadFile, QLiveLib.ensureNFD(qlfile))
    app.MainLoop()
