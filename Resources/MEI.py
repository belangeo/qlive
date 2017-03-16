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
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom

class MEI:
    def _prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def buildMEI(self, dictSave):

        root = Element('mei')
        root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        root.set('xmlns', 'http://www.music-encoding.org/ns/mei')
        root.set('meiversion', '3.0.0')

        # MEI Header
        meiHead = SubElement(root, 'meiHead')

        # http://music-encoding.org/documentation/3.0.0/fileDesc/
        fileDesc = SubElement(meiHead, 'fileDesc')

        fd_titleStmt = SubElement(fileDesc, 'fileDesc')

        fd_title = SubElement(fd_titleStmt, 'title')
        fd_title.text = 'Composition' #FIXME

        fd_subtitle = SubElement(fd_titleStmt, 'title', {'type':'subordinate'})
        fd_subtitle.text = 'Composition subtitle' #FIXME

        fd_respStmt = SubElement(fd_titleStmt, 'respStmt')
        fd_persName = SubElement(fd_titleStmt, 'persName', {'role':'creator'})
        fd_persName.text = 'Composer' #FIXME

        fd_pubStmt = SubElement(fd_titleStmt, 'pubStmt')
        fd_unpub  = SubElement(fd_pubStmt, 'unpub')
        fd_unpub.text = 'Working in progress...' #FIXME

        # http://music-encoding.org/documentation/3.0.0/encodingDesc/
        encodingDesc = SubElement(meiHead, 'encodingDesc')
        ec_appInfo = SubElement(encodingDesc, 'appInfo')
        ec_app = SubElement(ec_appInfo, 'application', {'version':APP_VERSION})
        ec_app_name = SubElement(ec_app, 'name')
        ec_app_name.text = APP_NAME

        # http://music-encoding.org/documentation/3.0.0/workDesc/
        workDesc = SubElement(meiHead, 'workDesc')
        w_work = SubElement(workDesc, 'work')

        w_titleStmt = SubElement(workDesc, 'titleStmt')
        w_title = SubElement(w_titleStmt, 'title')
        w_title.text = 'Composition' #FIXME

        w_subtitle = SubElement(w_titleStmt, 'title', {'type':'subordinate'})
        w_subtitle.text = 'Composition subtitle' #FIXME

        w_respStmt = SubElement(w_titleStmt, 'respStmt')
        w_persName = SubElement(w_titleStmt, 'persName', {'role':'composer'})
        w_persName.text = 'Composer' # FIXME

        w_creation = SubElement(w_work, 'creation')
        w_creation.text = 'Year of composition'
        w_date = SubElement(w_creation, 'date')
        w_date.text = '2017' # FIXME

        w_perfMedium = SubElement(w_work, 'perfMedium')
        w_perfResList = SubElement(w_perfMedium, 'perfResList')

        perfResList = ['Cello', 'Electronics'] #FIXME

        for p in perfResList:
            SubElement(w_perfResList, 'perfRes').text = p

        # http://music-encoding.org/documentation/3.0.0/music/
        music = SubElement(root, 'music')

        front = SubElement(music, 'front')
        body = SubElement(music, 'body')
        mdiv = SubElement(body, 'mdiv', {'n':'1', 'type':'movement'})
        score = SubElement(mdiv, 'score')
        parts = SubElement(score, 'parts')
        main_part = SubElement(parts, 'part')

        # Custom QLive MEI section starts here

        cues = SubElement(main_part, 'cues')
        for c in range(dictSave['cues']['numberOfCues']):
            SubElement(cues, 'cue', {'n':str(c), 'label':'Cue '+str(c)})

        soundfiles = SubElement(main_part, 'soundfiles')
        for sf in dictSave['soundfiles']:
            s = SubElement(soundfiles, 'soundfile', {'n': str(sf['id']), 'label':'SF #'})
            SubElement(s, 'id').text = str(sf['id'])
            SubElement(s, 'filename').text = sf['filename']
            SubElement(s, 'title').text = "Title for this soundfile"
            SubElement(s, 'description').text = "A short description for this soundfile"

        return self._prettify(root)
