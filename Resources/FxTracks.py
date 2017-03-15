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
from FxTrack import FxTrack
import QLiveLib


class FxTracks(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(TRACKS_BACKGROUND_COLOUR)

        self.selectedTrack = 0

        self.dragTrack = self.dragButton = None

        self.createTracks(2)

        self.SetVirtualSize((MAX_WIDTH, MAX_HEIGHT))
        self.SetScrollbars(20, 20, MAX_WIDTH/20, MAX_HEIGHT/20, 0, 0, False)

        self.setFont()
        self.createButtonBitmap()
        self.createButtonBitmap(False)

        self.buffer = wx.EmptyBitmap(MAX_WIDTH, MAX_HEIGHT)
        self.draw()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftClicked)
        self.Bind(wx.EVT_LEFT_UP, self.leftUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.leftDClicked)
        self.Bind(wx.EVT_RIGHT_DOWN, self.rightClicked)
        self.Bind(wx.EVT_MOTION, self.onMotion)

    def createTracks(self, num):
        self.tracks = []
        x = SELECTION_LINE_POS
        h = TRACK_ROW_SIZE * 2
        for i in range(num):
            track = FxTrack(self, i)
            track.setTrackPosition(x)
            track.setTrackHeight(h)
            self.tracks.append(track)
            x += h

    def addTrack(self):
        prevTrack = self.tracks[-1]
        x = prevTrack.getTrackPosition() + prevTrack.getTrackHeight()
        h = TRACK_ROW_SIZE * 2
        track = FxTrack(self, len(self.tracks))
        track.setTrackPosition(x)
        track.setTrackHeight(h)
        self.tracks.append(track)
        self.drawAndRefresh()

    def setFont(self, ptsize=10):
        self.font = wx.Font(ptsize, wx.FONTFAMILY_SWISS, wx.NORMAL,
                            wx.FONTWEIGHT_NORMAL)

    def createButtonBitmap(self, enable=True):
        w, h = BUTTON_WIDTH, BUTTON_HEIGHT
        b = wx.EmptyBitmap(w, h)
        dc = wx.MemoryDC(b)
        dc.SetPen(wx.Pen(TRACKS_BACKGROUND_COLOUR, 1))
        dc.SetBrush(wx.Brush(TRACKS_BACKGROUND_COLOUR))
        dc.DrawRectangle(0, 0, w, h)
        gc = wx.GraphicsContext_Create(dc)
        gc.SetPen(wx.Pen(FXBOX_OUTLINE_COLOUR, 1, wx.SOLID))
        if enable:
            gc.SetBrush(wx.Brush(FXBOX_ENABLE_BACKGROUND_COLOUR, wx.SOLID))
        else:
            gc.SetBrush(wx.Brush(FXBOX_DISABLE_BACKGROUND_COLOUR, wx.SOLID))
        rect = wx.Rect(0, 0, w, h)
        gc.DrawRoundedRectangle(rect[0], rect[1], rect[2], rect[3], 2)
        dc.SelectObject(wx.NullBitmap)
        if enable:
            self.buttonBitmap = b
        else:
            self.disableButtonBitmap = b

    def draw(self):
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DoDrawing(dc)

    def drawAndRefresh(self, restart=True):
        self.draw()
        wx.CallAfter(self.Refresh)
        server = QLiveLib.getVar("AudioServer")
        if restart and server.isStarted():
            server.start(False)
            server.start(True)
            QLiveLib.getVar("CuesPanel").loadCurrentCue()

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    def DoDrawing(self, dc):
        dc.BeginDrawing()

        dc.SetFont(self.font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawLabel("Inputs", wx.Rect(35, 3, 100, 22), wx.ALIGN_LEFT)
        dc.DrawLabel("Fxs", wx.Rect(125, 3, 100, 22), wx.ALIGN_LEFT)

        dc.SetPen(wx.Pen("#222222", 1))
        dc.DrawLine(0, 25, MAX_WIDTH, 25)
        dc.DrawLine(SELECTION_LINE_POS, 0, SELECTION_LINE_POS, MAX_HEIGHT)
        dc.DrawLine(INPUTS_LINE_POS, 0, INPUTS_LINE_POS, MAX_HEIGHT)

        trackPosition = SELECTION_LINE_POS
        for track in self.tracks:
            trackPosition = track.onPaint(dc, self.buttonBitmap,
                                          self.disableButtonBitmap,
                                          self.selectedTrack, trackPosition)

        dc.EndDrawing()

    def getTrackFromPos(self, pos):
        for track in self.tracks:
            tpos = track.getTrackPosition()
            theight = track.getTrackHeight()
            if pos[1] > tpos and pos[1] < tpos + theight:
                return track
        return None

    def getButtonFromPos(self, track, pos):
        for button in track.buttonsInputs:
            if button.getRect().Contains(pos):
                return button
        for button in track.buttonsFxs:
            if button.getRect().Contains(pos):
                return button
        return None

    def leftUp(self, evt):
        self.dragTrack = self.dragButton = None
        if self.HasCapture():
            self.ReleaseMouse()
        evt.Skip()

    def leftClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        track = self.getTrackFromPos(pos)
        if track is not None:
            if pos[0] < SELECTION_LINE_POS:
                self.setSelectedTrack(track.getId())
            else:
                if not QLiveLib.getVar("locked"):
                    button = self.getButtonFromPos(track, pos)
                    self.dragTrack = track
                    self.dragButton = button
                    self.CaptureMouse()
        evt.Skip()

    def leftDClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        track = self.getTrackFromPos(pos)
        if track is not None:
            if pos[0] < SELECTION_LINE_POS:
                self.setSelectedTrack(track.getId())
            else:
                button = self.getButtonFromPos(track, pos)
                if button is not None:
                    if evt.ShiftDown() and not QLiveLib.getVar("locked"):
                        track.deleteButton(button)
                    else:
                        button.openView()
                else:
                    if not QLiveLib.getVar("locked"):
                        track.createButton(pos)
        evt.Skip()

    def rightClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        track = self.getTrackFromPos(pos)
        if track is not None:
            button = self.getButtonFromPos(track, pos)
            if button is not None and not QLiveLib.getVar("locked"):
                button.openMenu(evt)
                self.drawAndRefresh()
        evt.Skip()

    def onMotion(self, evt):
        if self.HasCapture() and evt.LeftIsDown() and self.dragButton is not None:
            pos = self.CalcUnscrolledPosition(evt.GetPosition())
            self.dragTrack.moveButton(self.dragButton, pos)
        evt.Skip()

    def checkForDeletedSoundfile(self, id):
        for track in self.tracks:
            track.checkForDeletedSoundfile(id)

    def setTracksGlobalInterpTime(self, value, allcues, alltracks, meth):
        if alltracks:
            for track in self.tracks:
                track.setTrackGlobalInterpTime(value, allcues, meth)
        else:
            self.tracks[self.selectedTrack].setTrackGlobalInterpTime(value,
                                                                     allcues,
                                                                     meth)

    def getSaveDict(self):
        return [track.getSaveDict() for track in self.tracks]

    def setSaveState(self, tracks):
        self.removeAllTracks()
        self.createTracks(len(tracks))
        for i in range(len(self.tracks)):
            self.tracks[i].setSaveDict(tracks[i])
        self.drawAndRefresh()
        self.selectedTrack = 0

    def cueEvent(self, evt):
        for track in self.tracks:
            track.cueEvent(evt)

    def start(self):
        for track in self.tracks:
            track.start()

    def removeAllTracks(self):
        for track in self.tracks:
            track.close()
        self.tracks = []

    def removeTrack(self):
        self.tracks[self.selectedTrack].close()
        del self.tracks[self.selectedTrack]
        if not self.tracks:
            self.createTracks(1)

        self.selectedTrack -= 1
        if self.selectedTrack < 0:
            self.selectedTrack = 0

        [track.setId(i) for i, track in enumerate(self.tracks)]
        x = SELECTION_LINE_POS
        for track in self.tracks:
            track.setTrackPosition(x)
            x += track.getTrackHeight()
        self.drawAndRefresh()

    def setSelectedTrack(self, id=-1):
        if id == -1:
            id = (self.selectedTrack + 1) % len(self.tracks)
        self.selectedTrack = id
        self.drawAndRefresh()

    def getTracks(self):
        return self.tracks

    def close(self):
        for track in self.tracks:
            track.close()
