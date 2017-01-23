# encoding: utf-8
"""
Copyright 2017 (Pierre Michaud, Olivier Belanger, Tiago Bortoletto Vaz)

This file is part of QLive, a cues-based software to help the creation of mixed
music.

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
import Meta
from constants import *
import pprint

# Based on section "2.1 File Description" from MEI Guidelines 3.0.0
class FileDescriptionTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.tooltipsCheckBox = wx.CheckBox(self, -1, "Use tooltips",
                                            style=wx.ALIGN_RIGHT)
        self.tooltipsCheckBox.SetValue(QLiveLib.getVar("useTooltips"))
        self.Bind(wx.EVT_CHECKBOX, self.enableTooltips, self.tooltipsCheckBox)

        box = wx.StaticBox(self, -1, "File description")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL, )
        bsizer.Add(self.tooltipsCheckBox, 0, wx.TOP|wx.LEFT, 10)

        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(border)

    def enableTooltips(self, state):
        QLiveLib.setVar("useTooltips", state.GetEventObject().GetValue())

class WorkDescriptionTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.tooltipsCheckBox = wx.CheckBox(self, -1, "Use tooltips",
                                            style=wx.ALIGN_RIGHT)
        self.tooltipsCheckBox.SetValue(QLiveLib.getVar("useTooltips"))
        self.Bind(wx.EVT_CHECKBOX, self.enableTooltips, self.tooltipsCheckBox)

        box = wx.StaticBox(self, -1, "Work description")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL, )
        bsizer.Add(self.tooltipsCheckBox, 0, wx.TOP|wx.LEFT, 10)

        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(border)

    def enableTooltips(self, state):
        QLiveLib.setVar("useTooltips", state.GetEventObject().GetValue())

class OtherDescriptionTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

class MetaFrame(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        wx.Dialog.__init__(self, parent, title="Edit metadata",
                           style=style, size=(500, 350))
        self.parent = parent

        # Create a panel and notebook (tabs holder)
        panel = wx.Panel(self)
        nb = wx.Notebook(panel)

        box = wx.BoxSizer(wx.HORIZONTAL)

        saveButton = wx.Button(panel, -1, label="Save")
        saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        self.Bind(wx.EVT_CLOSE, self.onSave)

        cancelButton = wx.Button(panel, -1, label="Cancel")
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        self.Bind(wx.EVT_CLOSE, self.onCancel)

        box.Add(saveButton, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 2)
        box.Add(cancelButton, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 2)


        self.path = QLiveLib.getVar("currentProject")
        execfile(self.path, globals())
        dictSave["meta"] = Meta.getSaveDict()
        self.data = dictSave

        # Create the tab windows
        self.tabFile = FileDescriptionTab(nb)
        self.tabWork = WorkDescriptionTab(nb)
        self.tabOther = OtherDescriptionTab(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(self.tabFile, "File")
        nb.AddPage(self.tabWork, "Work")
        nb.AddPage(self.tabOther, "Other")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 0, wx.EXPAND)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        panel.SetSizerAndFit(sizer)
        Y = panel.GetSize()[1]
        self.SetSize((500, Y+35))

    #TODO: move a saveFile method from mainWindow to QliveLib (?)
    def onSave(self, evt):
        with open(self.path, "w") as f:
            f.write(QLIVE_MAGIC_LINE)
            f.write("### %s ###\n" % APP_VERSION)
            f.write("dictSave = %s" % pprint.pformat(self.data, indent=4))

    def onCancel(self, evt):
        self.Destroy()
