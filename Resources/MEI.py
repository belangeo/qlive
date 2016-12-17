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
from constants import *
from datetime import date

def buildMEI():

    # Root structure
    mei = MeiElement("mei")
    meiHead = MeiElement("meiHead")
    fileDesc = MeiElement("fileDesc")
    workDesc = MeiElement("workDesc")
    encodingDesc = MeiElement("encodingDesc")
    music = MeiElement("music")
    body = MeiElement("body")

    # Header structure
    appInfo = MeiElement("appInfo")
    application = MeiElement("application")
    name_application = MeiElement("name")
    perfMedium = MeiElement("perfMedium")
    instrumentation = MeiElement("instrumentation")
    titleStmt_file = MeiElement("titleStmt")
    titleStmt_work = MeiElement("titleStmt")
    respStmt = MeiElement("respStmt")
    work = MeiElement("work")
    title_file = MeiElement("title") # Machine readable work title (ex.: electronic part of composition X)
    title_work = MeiElement("title") # Master work title (ex.: Composition X)
    title_file.value = "Electronic part for Composition X"
    title_work.value = "Composition X"
    pubStmt = MeiElement("pubStmt")
    unpub = MeiElement("unpub")
    unpub.value = "Working in progress."
    persName_composer = MeiElement("persName")
    persName_encoder = MeiElement("persName")
    persName_composer.addAttribute("role", "composer")
    persName_encoder.addAttribute("role", "encoder")
    persName_composer.value = "Mrs. Test Q. L. Composer"
    persName_encoder.value = "Mrs. Test Q. L. Encoder"

    # Building header tree
    mei.addChild(meiHead)
    meiHead.addChild(fileDesc)
    meiHead.addChild(workDesc)
    meiHead.addChild(encodingDesc)
    fileDesc.addChild(titleStmt_file)
    work.addChild(titleStmt_work)
    work.addChild(perfMedium)
    perfMedium.addChild(instrumentation)

    # must be a dynamic loopvar assignment
    instrVoice1 = MeiElement("instrVoice")
    instrVoice2 = MeiElement("instrVoice")
    instrVoice1.value = "Cello"
    instrVoice2.value = "Electronics"
    instrumentation.addChild(instrVoice1)
    instrumentation.addChild(instrVoice2)
    # ================================

    encodingDesc.addChild(appInfo)
    appInfo.addChild(application)
    application.addChild(name_application)
    name_application.value = APP_NAME
    application.addAttribute("version", APP_VERSION)
    today = date.today().isoformat()
    application.addAttribute("isodate", today)
    workDesc.addChild(work)
    fileDesc.addChild(pubStmt)
    titleStmt_file.addChild(title_file)
    titleStmt_file.addChild(respStmt)
    titleStmt_work.addChild(title_work)
    respStmt.addChild(persName_composer)
    respStmt.addChild(persName_encoder)
    pubStmt.addChild(unpub)

    # Content
    mei.addChild(music)
    music.addChild(body)

    doc = MeiDocument()
    doc.root = mei

    return doc

def saveMEI(path):
    doc = buildMEI()
    status = documentToFile(doc, str(path))

def loadMEI():
    pass


