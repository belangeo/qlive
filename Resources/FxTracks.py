import wx
from FxTrack import *

# put FxBox at the clicked position

class FxTracks(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)  
        self.SetBackgroundColour(TRACKS_BACKGROUND_COLOUR)

        self.selectedTrack = 0
        
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
        self.Bind(wx.EVT_LEFT_DCLICK, self.leftDClicked)
        self.Bind(wx.EVT_RIGHT_DOWN, self.rightClicked)

    def createTracks(self, num):
        self.tracks = []
        x = 25
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
        self.font = wx.Font(ptsize, wx.FONTFAMILY_DEFAULT, wx.NORMAL, 
                            wx.FONTWEIGHT_NORMAL, face="Monospace")

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
        rectI = wx.Rect(0, 4, w/12., h-8)
        rectO = wx.Rect(w*11/12., 4, w/12., h-8)
        gc.DrawRoundedRectangle(rect[0], rect[1], rect[2], rect[3], 5)
        gc.DrawRoundedRectangle(rectI[0], rectI[1], rectI[2], rectI[3], 2)
        gc.DrawRoundedRectangle(rectO[0], rectO[1], rectO[2], rectO[3], 2)
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

    def drawAndRefresh(self):
        self.draw()
        wx.CallAfter(self.Refresh)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        
    def DoDrawing(self, dc):
        dc.BeginDrawing()

        dc.SetFont(self.font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawLabel("Inputs", wx.Rect(35, 3, 100, 22), wx.ALIGN_LEFT)
        dc.DrawLabel("Fxs", wx.Rect(135, 3, 100, 22), wx.ALIGN_LEFT)

        dc.SetPen(wx.Pen("#222222", 1))
        dc.DrawLine(0, 25, MAX_WIDTH, 25)
        dc.DrawLine(25, 0, 25, MAX_HEIGHT)
        dc.DrawLine(125, 0, 125, MAX_HEIGHT)

        for track in self.tracks:
            track.onPaint(dc, self.buttonBitmap, self.disableButtonBitmap,
                            self.selectedTrack)

        dc.EndDrawing()

    def leftClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        trackFounded = buttonFounded = None
        for track in self.tracks:
            if pos[1] > track.getTrackPosition() and \
               pos[1] < track.getTrackPosition() + track.getTrackHeight():
                trackFounded = track
                break
        if trackFounded is not None:
            buttonFounded = None
            if pos[0] < 25:
                self.setSelectedTrack(track.getId())
            elif pos[0] < 125:
                for but in track.buttonsInputs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
            else:
                for but in track.buttonsFxs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
        if buttonFounded is not None:
            if evt.ShiftDown():
                trackFounded.deleteButton(buttonFounded)
            else:
                buttonFounded.openView()
        evt.Skip()

    def leftDClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        trackFounded = buttonFounded = selection = None
        for track in self.tracks:
            if pos[1] > track.getTrackPosition() and \
               pos[1] < track.getTrackPosition() + track.getTrackHeight():
                trackFounded = track
                break
        if trackFounded is not None:
            buttonFounded = None
            if pos[0] < 25:
                self.setSelectedTrack(track.getId())
                selection = track.getId()
            elif pos[0] < 125:
                for but in track.buttonsInputs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
            else:
                for but in track.buttonsFxs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
        if buttonFounded is None and selection is None:
            track.createButton(pos)
            self.drawAndRefresh()
        evt.Skip()

    def rightClicked(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition())
        trackFounded = buttonFounded = None
        for track in self.tracks:
            if pos[1] > track.getTrackPosition() and \
               pos[1] < track.getTrackPosition() + track.getTrackHeight():
                trackFounded = track
                break
        if trackFounded is not None:
            buttonFounded = None
            if pos[0] < 100:
                for but in track.buttonsInputs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
            else:
                for but in track.buttonsFxs:
                    if but.getRect().Contains(pos):
                        buttonFounded = but
                        break
        if buttonFounded is not None:
            buttonFounded.openMenu(evt)
            self.drawAndRefresh()
        evt.Skip()

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
        x = 25
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