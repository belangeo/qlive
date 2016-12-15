#!/usr/bin/env python
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
            if len(self.filenames) > 0:
                self.frame.loadFile(QLiveLib.ensureNFD(self.filenames[0]))

    def MacOpenFiles(self, filenames):
        if type(filenames) != list:
            filenames = [filenames]
        filenames = [f for f in filenames if f.endswith(".qlp")]
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
        if sys.argv[1].endswith(".qlp"):
            qlfile = sys.argv[1]

    app = QLiveApp()
    if qlfile:
        wx.CallAfter(app.frame.loadFile, QLiveLib.ensureNFD(qlfile))
    app.MainLoop()