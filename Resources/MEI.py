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

from pymei import *

def buildMEI():

    # Basic structure
    mei = MeiElement("mei")
    head = MeiElement("meiHead")
    mus = MeiElement("music")
    body = MeiElement("body")
    mei.addChild(head)
    mei.addChild(mus)
    mus.addChild(body)

    doc = MeiDocument()
    doc.root = mei

    return doc

def saveMEI(path):
    doc = buildMEI()
    status = documentToFile(doc, str(path))

def loadMEI():
    pass


