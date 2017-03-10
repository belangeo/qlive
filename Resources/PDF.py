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
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors

from constants import *
import QLiveLib
import xml.etree.cElementTree as ET

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

class PDF:
    def __init__(self):
        self.PAGE_HEIGHT=defaultPageSize[1]
        self.styles = getSampleStyleSheet()

        tree = ET.parse('sample.mei')
        root = tree.getroot()
        # Loading header content
        self.title = str(tree.find('./meiHead/workDesc/work/titleStmt/title').text)
        self.subtitle = str(tree.find('./meiHead/workDesc/work/titleStmt/title[@type="subordinate"]').text)
        self.composer = str(tree.find('./meiHead/workDesc/work/titleStmt/respStmt/persName[@role="composer"]').text)
        self.year = str(tree.find('./meiHead/workDesc/work/creation/date').text)

        # Loading music content
        self.preface = tree.find('./music/front/div[@type="preface"]')
        self.cues = tree.findall('./music/body/mdiv/parts/part/cues/cue')
        self.tracks = tree.findall('./music/body/mdiv/parts/part/tracks/track')
        self.soundfiles = tree.findall('./music/body/mdiv/parts/part/soundfiles/soundfile')

        # Formating
        self.Elements = []
        self.HeaderStyle = self.styles["Heading1"]
        self.HeaderStyle2 = self.styles["Heading2"]
        self.HeaderStyle3 = self.styles["Heading3"]
        self.ParaStyle = self.styles["Normal"]

    def myFirstPage(self, canvas, doc):
        self.pageinfo = "%s / %s" % (self.title, self.composer)
        canvas.saveState()
        canvas.setStrokeColorRGB(1,0,0)
        canvas.setLineWidth(5)
        canvas.line(66,72,66,self.PAGE_HEIGHT-72)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "p.1 / %s" % self.pageinfo)
        canvas.restoreState()

    def myLaterPages(self, canvas, doc):
        #canvas.drawImage("snkanim.gif", 36, 36)
        canvas.saveState()
        canvas.setStrokeColorRGB(1,0,0)
        canvas.setLineWidth(5)
        canvas.line(66,72,66,self.PAGE_HEIGHT-72)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "p.%d %s" % (doc.page, self.pageinfo))
        canvas.restoreState()

    def go(self):
        self.Elements.insert(0,Spacer(0,inch))
        doc = SimpleDocTemplate('gfe.pdf')
        doc.build(self.Elements,onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages)

    def header(self, txt, style=None, klass=Paragraph, sep=0.3):
        s = Spacer(0.2*inch, sep*inch)
        self.Elements.append(s)
        para = klass(txt, style)
        self.Elements.append(para)

    def p(self, txt):
        return self.header(txt, style=self.ParaStyle, sep=0.1)

    def build(self):
        # First page
        composer = '<para align=center spaceAfter=50>'+self.composer+'</para>'
        title = '<para align=center spaceAfter=0 spaceBefore=30 fontSize=20>'+self.title+'</para>'
        subtitle = '<para align=center spaceAfter=20>'+self.subtitle+'</para>'
        self.header("", sep=0.5, style=self.ParaStyle)
        self.header(title, style=self.HeaderStyle, sep=0)
        self.header(subtitle, sep=0, style=self.HeaderStyle3)
        self.header(composer, sep=0.2, style=self.ParaStyle)
        for i in self.preface:
            paragraph = '<para firstLineIndent=15 rightIndent=60 leftIndent=60 align=justify>%s</para>' % (str(i.text))
            self.p(paragraph)
        self.Elements.append(PageBreak())

        # Others pages

        # SOUNDFILES
        self.header("Soundfiles", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        for s in self.soundfiles:
            header_text = '%s (%s)' % (s.attrib['label'], str(s.find('./filename').text))
            self.header(header_text, style=self.ParaStyle, sep=0)
            self.p(str(s.find('./description').text))


        # TRACKS
        self.header("Tracks", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        for t in self.tracks:
            self.header(t.attrib['label'], style=self.HeaderStyle3, sep=0)
            self.p(str(t.find('./description').text))
            self.p('\n')
            w,h = 0,0
            label = ""
            LIST_STYLE = TableStyle()
            for m in t.find('./modules'):
                # getting w and h
                if int(m.attrib['x_seq']) > w: w = int(m.attrib['x_seq'])
                if int(m.attrib['y_seq']) > h: h = int(m.attrib['y_seq'])
            track_table_data = [["" for i in range(w)] for i in range(h)]
            for m in t.find('./modules'):
                x,y = int(m.attrib['x_seq'])-1, int(m.attrib['y_seq'])-1
                label = str(m.find("./name").text)
                track_table_data[y][x] = label
                LIST_STYLE.add('BOX',(x,y),(x,y),1,colors.red)
            t = Table(track_table_data, style=LIST_STYLE)
            self.Elements.append(t)

        # CUES
        self.header("Cues", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        for c in self.cues:
            self.header(c.attrib['label'], style=self.HeaderStyle3, sep=0)
            self.p(str(c.find('./description').text))
            if c.attrib['n'] is not "0":
                pass # look for parameters


pdf = PDF()
pdf.build()
pdf.go()
