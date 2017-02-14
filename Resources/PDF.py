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
import xml.etree.cElementTree as ET

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

class PDF:
    def __init__(self):
        self.PAGE_HEIGHT=defaultPageSize[1]
        self.styles = getSampleStyleSheet()

        tree = ET.parse('test.mei')
        root = tree.getroot()
        # Loading header content
        self.title = str(tree.find('./meiHead/workDesc/titleStmt/title').text)
        self.subtitle = str(tree.find('./meiHead/workDesc/titleStmt/title[@type="subordinate"]').text)
        self.composer = str(tree.find('./meiHead/workDesc/titleStmt/persName[@role="composer"]').text)
        self.year = str(tree.find('./meiHead/workDesc/work/creation/date').text)
        self.abstract = """This paper describes the primative methods underlying the implementation
of SQL query evaluation in Gadfly 2, a database management system implemented
in Python [Van Rossum]. The major design goals behind
the architecture described here are to simplify the implementation
and to permit flexible and efficient extensions to the gadfly
engine. Using this architecture and its interfaces programmers
can add functionality to the engine such as alternative disk based
indexed table implementations, dynamic interfaces to remote data
bases or or other data sources, and user defined computations."""

        self.Elements = []
        self.HeaderStyle = self.styles["Heading1"]
        self.ParaStyle = self.styles["Normal"]


    def myFirstPage(self, canvas, doc):
        self.pageinfo = "%s / %s" % (self.title, self.composer)
        canvas.saveState()
        canvas.setStrokeColorRGB(1,0,0)
        canvas.setLineWidth(5)
        canvas.line(66,72,66,self.PAGE_HEIGHT-72)
        canvas.setFont('Times-Bold',16)
        canvas.drawString(108, self.PAGE_HEIGHT-108, self.title)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "First Page / %s" % self.pageinfo)
        canvas.restoreState()

    def myLaterPages(self, canvas, doc):
        #canvas.drawImage("snkanim.gif", 36, 36)
        canvas.saveState()
        canvas.setStrokeColorRGB(1,0,0)
        canvas.setLineWidth(5)
        canvas.line(66,72,66,self.PAGE_HEIGHT-72)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, self.pageinfo))
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
        self.header(self.subtitle, sep=0.1, style=self.ParaStyle)
        self.header(self.composer, sep=0.1, style=self.ParaStyle)
        self.header("WORK DESCRIPTION", style=self.HeaderStyle)
        self.p(self.abstract)
        self.Elements.append(PageBreak())
        self.header("SOUNDFILES", style=self.HeaderStyle)
        self.p(self.abstract)
        self.header("TRACKS", style=self.HeaderStyle)
        self.p(self.abstract)
        self.header("CUES", style=self.HeaderStyle)
        self.p(self.abstract)


pdf = PDF()
pdf.build()
pdf.go()
