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
from constants import *
import QLiveLib
from xml.etree import cElementTree as ET

def loadFromTemplate():
    tree = ET.parse(os.path.join(RESOURCES_PATH,"template.mei"))
    e = tree.getroot()
    return QLiveLib.etree_to_dict(e)

def getSaveDict():
    path = QLiveLib.getVar("currentProject")
    execfile(path, globals())
    if "meta" in dictSave:
        if dictSave["meta"] is None:
            dictSave["meta"] = loadFromTemplate()
    else:
        dictSave["meta"] = loadFromTemplate()

    return dictSave["meta"]
