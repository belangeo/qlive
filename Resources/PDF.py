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

        self.tree = ET.parse('sample.mei')
        self.root = self.tree.getroot()
        # Loading header content
        self.title = str(self.tree.find('./meiHead/workDesc/work/titleStmt/title').text)
        self.subtitle = str(self.tree.find('./meiHead/workDesc/work/titleStmt/title[@type="subordinate"]').text)
        self.composer = str(self.tree.find('./meiHead/workDesc/work/titleStmt/respStmt/persName[@role="composer"]').text)
        self.year = str(self.tree.find('./meiHead/workDesc/work/creation/date').text)

        # Loading music content
        self.preface = self.tree.find('./music/front/div[@type="preface"]')
        self.cues = self.tree.findall('./music/body/mdiv/parts/part/cues/cue')
        self.tracks = self.tree.findall('./music/body/mdiv/parts/part/tracks/track')
        self.soundfiles = self.tree.findall('./music/body/mdiv/parts/part/soundfiles/soundfile')

        # Formating
        self.Elements = []
        self.HeaderStyle = self.styles["Heading1"]
        self.HeaderStyle2 = self.styles["Heading2"]
        self.HeaderStyle3 = self.styles["Heading3"]
        self.HeaderStyle4 = self.styles["Heading4"]
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
        subtitle = '<para align=center spaceAfter=0>'+self.subtitle+'</para>'
        year = '<para align=center spaceAfter=20>('+self.year+')</para>'
        self.header("", sep=0.5, style=self.ParaStyle)
        self.header(title, style=self.HeaderStyle, sep=0)
        self.header(subtitle, sep=0, style=self.HeaderStyle3)
        self.header(year, sep=0, style=self.HeaderStyle4)
        self.header(composer, sep=0, style=self.ParaStyle)
        for i in self.preface:
            paragraph = '<para firstLineIndent=15 rightIndent=60 leftIndent=60 align=justify>%s</para>' % (str(i.text))
            self.p(paragraph)
        self.Elements.append(PageBreak())

        # Others pages

        # SOUNDFILES
        self.header("SOUNDFILES", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        self.p("Here is a list of sound files used in this work:")
        self.p("\n")
        self.p("\n")
        soundfiles_line_data = []
        LIST_STYLE = TableStyle()
        styles = getSampleStyleSheet()
        soundfiles_table_data = [["ID", "Descriptive name", "Filename", "Description"]]
        for s in self.soundfiles:
            id = Paragraph('<para fontSize=9 fontName="Courier">' + s.attrib['n'] + '</para>', styles['Normal'])
            label = Paragraph('<para fontSize=9 fontName="Courier">' + s.attrib['label'] + '</para>', styles['Normal'])
            filename = Paragraph('<para fontSize=9 fontName="Courier">' + str(s.find('./filename').text) + '</para>', styles['Normal'])
            desc = Paragraph('<para fontSize=9 fontName="Courier">' + str(s.find('./description').text) + '</para>', styles['Normal'])

            soundfiles_line_data.append(id)
            soundfiles_line_data.append(label)
            soundfiles_line_data.append(filename)
            soundfiles_line_data.append(desc)
            soundfiles_table_data.append(soundfiles_line_data)
            soundfiles_line_data = []
            LIST_STYLE.add('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)
            LIST_STYLE.add('GRID', (0,0), (-1,-1), 0.25, colors.black)

        t = Table(soundfiles_table_data, colWidths=(25,90,150,170),style=LIST_STYLE)
        self.Elements.append(t)

        # TRACKS
        self.header("TRACKS", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        self.p("These are the tracks used in this work. Each track has a sequence of modules, "
               "which should be read from left to right. They can be connected in series or in parallel, "
               "here visually represented by their vertical and horizontal arrangements.")

        for t in self.tracks:
            self.header(t.attrib['label'], style=self.HeaderStyle3, sep=0)
            self.p(str(t.find('./description').text))
            self.p('\n')
            self.p("\n")
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
                label = "%s (%s)" % (str(m.find("./name").text), m.attrib['n'])
                track_table_data[y][x] = label
                LIST_STYLE.add('BOX',(x,y),(x,y),1,colors.red)
            t = Table(track_table_data, style=LIST_STYLE)
            self.Elements.append(t)

        # CUES
        self.header("CUES", style=self.HeaderStyle2)
        d = Drawing(450,1)
        d.add(Line(0,5,450,5))
        self.Elements.append(d)
        for cue in self.cues:
            self.header(cue.attrib['label'], style=self.HeaderStyle3, sep=0)
            self.p(str(cue.find('./description').text))
            if cue.attrib['n'] != "0": # no need to loop over cue 0
                # TRACKS INTO CUES
                for tracks in cue.find('./tracks'):
                    track_text = "Modules setup for track %s" % tracks.attrib['ref']
                    self.header(track_text, style=self.HeaderStyle4, sep=0)
                    for module in tracks:
                        track_ref = './music/body/mdiv/parts/part/tracks/track/[@n="%s"]/modules/module/[@n="%s"]' % (tracks.attrib['ref'], module.attrib['ref'])
                        mod_ref = "%s (%s)" % (str(self.tree.find(track_ref).find('name').text), module.attrib['ref'])
                        self.p(mod_ref)
                        for parameter in module.find('./parameters'):
                            parameter_str = '<para fontSize=9 fontName="Courier"> &nbsp;|--> %s: %s</para>' % (str(parameter.tag), str(parameter.text))
                            self.p(parameter_str)
                # SOUNDFILES INTO CUES
                self.header("Soundfiles setup for this cue:", self.HeaderStyle4, sep=0)
                soundfiles_table_data = [["ID", "Playing", "Loop", "Transp.", "Gain", "Output", "Start", "End", "Xfade", "Outchan"]]
                for soundfile in cue.find('./soundfiles'):
                    soundfiles_line_data = []
                    LIST_STYLE = TableStyle()
                    styles = getSampleStyleSheet()
                    soundfiles_line_data.append(Paragraph('<para fontSize=9 fontName="Courier">' + soundfile.attrib['ref'] + '</para>', styles["Normal"]))
                    for parameter in soundfile.find('./parameters'):
                        parameter_str = Paragraph('<para fontSize=9 fontName="Courier">' + str(parameter.text) + '</para>', styles["Normal"])
                        soundfiles_line_data.append(parameter_str)
                    soundfiles_table_data.append(soundfiles_line_data)
                t = Table(soundfiles_table_data, colWidths=(20, 45,56,45,45,45,45,48,45,45), style=LIST_STYLE)
                self.Elements.append(t)
pdf = PDF()
pdf.build()
pdf.go()