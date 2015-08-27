import wx, math
import wx.lib.stattext as stattext
from pyolib._wxwidgets import BACKGROUND_COLOUR
from AudioMixer import *
from constants import *
import QLiveLib

def interpFloat(t, v1, v2):
    "interpolator for a single value; interprets t in [0-1] between v1 and v2"
    return (v2-v1)*t + v1

def tFromValue(value, v1, v2):
    "returns a t (in range 0-1) given a value in the range v1 to v2"
    return float(value-v1)/(v2-v1)

def clamp(v, minv, maxv):
    "clamps a value within a range"
    if v<minv: v=minv
    if v> maxv: v=maxv
    return v

def toLog(t, v1, v2):
    return math.log10(t/v1) / math.log10(v2/v1)

def toExp(t, v1, v2):
    return math.pow(10, t * (math.log10(v2) - math.log10(v1)) + math.log10(v1))

POWOFTWO = {2:1, 4:2, 8:3, 16:4, 32:5, 64:6, 128:7, 256:8, 512:9, 1024:10, 
            2048:11, 4096:12, 8192:13, 16384:14, 32768:15, 65536:16}
def powOfTwo(x):
    return 2**x

def powOfTwoToInt(x):
    return POWOFTWO[x]

class QLiveControlKnob(wx.Panel):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), 
                 size=(50,85), log=False, outFunction=None, integer=False, 
                 backColour=None, label='', playFunction=None, 
                 editFunction=None, outOnShiftFunction=None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, pos=pos, 
                          size=size, style=wx.NO_BORDER|wx.WANTS_CHARS)
        self.parent = parent
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)  
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.outFunction = outFunction
        self.playFunction = playFunction
        self.editFunction = editFunction
        if self.playFunction is None and self.editFunction is None:
            self.drawBottomPart = False
            self.SetSize((50, 70))
        else:
            self.drawBottomPart = True
        self.SetMinSize(self.GetSize())
        self.outOnShiftFunction = outOnShiftFunction
        self.integer = integer
        self.log = log
        self.label = label
        self.SetRange(minvalue, maxvalue)
        self.borderWidth = 1
        self.selected = False
        self._enable = True
        self.new = ''
        self.floatPrecision = '%.3f'
        self.mode = 0
        self.midiLearn = False
        self.midictlLabel = ""
        self.autoPlay = False
        self.autoEdit = False
        self.colours = {0: "#000000", 1: "#FF0000", 2: "#00FF00"}
        if backColour: self.backColour = backColour
        else: self.backColour = CONTROLSLIDER_BACK_COLOUR
        if init != None: 
            self.SetValue(init)
            self.init = init
        else: 
            self.SetValue(minvalue)
            self.init = minvalue
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.DoubleClick)
        self.Bind(wx.EVT_MOTION, self.MouseMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)
        self.Bind(wx.EVT_KILL_FOCUS, self.LooseFocus)

        if PLATFORM == "win32":
            self.dcref = wx.BufferedPaintDC
        else:
            self.dcref = wx.PaintDC

    def setFloatPrecision(self, x):
        self.floatPrecision = '%.' + '%df' % x
        wx.CallAfter(self.Refresh)

    def getMinValue(self):
        return self.minvalue

    def getMaxValue(self):
        return self.maxvalue

    def setEnable(self, enable):
        self._enable = enable
        wx.CallAfter(self.Refresh)

    def getInit(self):
        return self.init

    def getLabel(self):
        return self.label

    def getLog(self):
        return self.log
        
    def SetRange(self, minvalue, maxvalue):   
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def getRange(self):
        return [self.minvalue, self.maxvalue]

    def SetValue(self, value, propagate=False):
        value = clamp(value, self.minvalue, self.maxvalue)
        if self.log:
            t = toLog(value, self.minvalue, self.maxvalue)
            self.value = interpFloat(t, self.minvalue, self.maxvalue)
        else:
            t = tFromValue(value, self.minvalue, self.maxvalue)
            self.value = interpFloat(t, self.minvalue, self.maxvalue)
        if self.integer:
            self.value = int(self.value)
        self.selected = False
        if propagate:
            if self.outFunction:
                self.outFunction(self.GetValue())
        wx.CallAfter(self.Refresh)

    def setAutoPlay(self, state):
        self.autoPlay = state
        wx.CallAfter(self.Refresh)

    def setAutoEdit(self, state):
        self.autoEdit = state
        wx.CallAfter(self.Refresh)

    def GetValue(self):
        if self.log:
            t = tFromValue(self.value, self.minvalue, self.maxvalue)
            val = toExp(t, self.minvalue, self.maxvalue)
        else:
            val = self.value
        if self.integer:
            val = int(val)
        return val

    def LooseFocus(self, event):
        self.selected = False
        wx.CallAfter(self.Refresh)

    def keyDown(self, event):
        if self.selected:
            char = ''
            if event.GetKeyCode() in range(324, 334):
                char = str(event.GetKeyCode() - 324)
            elif event.GetKeyCode() == 390:
                char = '-'
            elif event.GetKeyCode() == 391:
                char = '.'
            elif event.GetKeyCode() == wx.WXK_BACK:
                if self.new != '':
                    self.new = self.new[0:-1]
            elif event.GetKeyCode() < 256:
                char = chr(event.GetKeyCode())
            if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                self.new += char
            elif char == '.' and not '.' in self.new:
                self.new += char
            elif char == '-' and len(self.new) == 0:
                self.new += char
            elif event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
                if self.new != '':
                    self.SetValue(eval(self.new))
                    # Send value
                    if self.outFunction:
                        self.outFunction(self.GetValue())
                    self.new = ''
                self.selected = False
        wx.CallAfter(self.Refresh)

    def MouseDown(self, evt):
        if self._enable:
            rec = wx.Rect(5, 13, 45, 45)
            pos = evt.GetPosition()
            if rec.Contains(pos):
                self.clickPos = wx.GetMousePosition()
                self.oldValue = self.value
                self.CaptureMouse()
                self.selected = False
            rec = wx.Rect(7, 69, 12, 12)
            if rec.Contains(pos):
                self.autoPlay = not self.autoPlay
            rec = wx.Rect(31, 69, 12, 12)
            if rec.Contains(pos):
                self.autoEdit = not self.autoEdit
                if self.editFunction is not None:
                    self.editFunction(self.autoEdit)
            wx.CallAfter(self.Refresh)
        evt.Skip()

    def MouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def DoubleClick(self, event):
        if self._enable:
            w, h = self.GetSize()
            pos = event.GetPosition()
            reclab = wx.Rect(3, 60, w-3, 10)
            recpt = wx.Rect(self.knobPointPos[0]-3, 
                            self.knobPointPos[1]-3, 9, 9)
            if reclab.Contains(pos):
                self.selected = True
            elif recpt.Contains(pos):
                self.mode = (self.mode+1) % 3
            wx.CallAfter(self.Refresh)
        event.Skip()

    def MouseMotion(self, evt):
        if self._enable:
            if evt.Dragging() and evt.LeftIsDown() and self.HasCapture():
                pos = wx.GetMousePosition()
                offY = self.clickPos[1] - pos[1]
                offX = pos[0] - self.clickPos[0]
                off = offY + offX
                off *= 0.005 * (self.maxvalue - self.minvalue)
                self.value = clamp(self.oldValue + off, self.minvalue, 
                                   self.maxvalue)
                # Send value
                if self.outFunction:
                    self.outFunction(self.GetValue())
                if evt.ShiftDown() and self.outOnShiftFunction:
                    self.outOnShiftFunction(self.GetValue())
                self.selected = False
                wx.CallAfter(self.Refresh)

    def setbackColour(self, colour):
        self.backColour = colour
        wx.CallAfter(self.Refresh)

    def OnPaint(self, evt):
        # TODO: Drawing of the controlKnob must really be optimized
        w,h = self.GetSize()
        dc = self.dcref(self)
        gc = wx.GraphicsContext_Create(dc)

        if self._enable:
            backColour = self.backColour
            knobColour = CONTROLSLIDER_KNOB_COLOUR
        else:
            backColour = CONTROLSLIDER_DISABLE_BACK_COLOUR
            knobColour = CONTROLSLIDER_DISABLE_KNOB_COLOUR

        dc.Clear()
        gc.SetBrush(wx.Brush(backColour, wx.SOLID))

        # Draw background
        gc.SetPen(wx.Pen("#777777", width=self.borderWidth, style=wx.SOLID))
        gc.DrawRoundedRectangle(0, 0, w-1, h-1, 3)

        dc.SetFont(wx.Font(9, wx.ROMAN, wx.NORMAL, wx.NORMAL, face=FONT_FACE))
        dc.SetTextForeground(CONTROLSLIDER_TEXT_COLOUR)

        # Draw text label
        reclab = wx.Rect(0, 1, w, 9)
        dc.DrawLabel(self.label, reclab, wx.ALIGN_CENTER_HORIZONTAL)

        recval = wx.Rect(0, 55, w, 14)

        if self.selected:
            gc.SetBrush(wx.Brush(CONTROLSLIDER_SELECTED_COLOUR, wx.SOLID))
            gc.SetPen(wx.Pen(CONTROLSLIDER_SELECTED_COLOUR, self.borderWidth))  
            gc.DrawRoundedRectangle(2, 55, w-4, 12, 2)

        r = math.sqrt(.1)
        val = tFromValue(self.value, self.minvalue, self.maxvalue) * 0.8
        ph = val * math.pi * 2 - (3 * math.pi / 2.2)
        X = r * math.cos(ph)*45
        Y = r * math.sin(ph)*45
        gc.SetBrush(wx.Brush(knobColour, wx.SOLID))
        gc.SetPen(wx.Pen(self.colours[self.mode], width=2, style=wx.SOLID))
        self.knobPointPos = (X+25, Y+35)
        R = math.sqrt(X*X + Y*Y)
        gc.DrawEllipse(25-R, 35-R, R*2, R*2)
        gc.StrokeLine(25, 35, X+25, Y+35)

        if not self.midiLearn:
            dc.SetFont(wx.Font(CONTROLSLIDER_FONT-1, wx.FONTFAMILY_DEFAULT, 
                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                               face=FONT_FACE))    
            dc.DrawLabel(self.midictlLabel, wx.Rect(2, 12, 40, 40), 
                         wx.ALIGN_CENTER)
        else:
            dc.DrawLabel("?...", wx.Rect(2, 12, 40, 40), wx.ALIGN_CENTER)

        dc.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, 
                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                           face=FONT_FACE))
        # Draw text value
        if self.selected and self.new:
            val = self.new
        else:
            if self.integer:
                val = '%d' % self.GetValue()
            else:
                val = self.floatPrecision % self.GetValue()
        if PLATFORM == 'linux2':
            width = len(val) * (dc.GetCharWidth() - 3)
        else:
            width = len(val) * dc.GetCharWidth()
        dc.SetTextForeground(CONTROLSLIDER_TEXT_COLOUR)
        dc.DrawLabel(val, recval, wx.ALIGN_CENTER)

        if self.drawBottomPart:
            if self.autoPlay:
                gc.SetBrush(wx.Brush("#55DD55"))
            else:
                gc.SetBrush(wx.Brush("#333333", wx.TRANSPARENT))
            gc.SetPen(wx.Pen("#333333", 1.5))
            tri = [(8,70), (8,80), (16,75), (8, 70)]
            gc.DrawLines(tri)

            gc.SetFont(wx.Font(CONTROLSLIDER_FONT, wx.FONTFAMILY_DEFAULT, 
                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                               face=FONT_FACE))
            if self.autoEdit:
                gc.SetPen(wx.Pen("#333333", 1.5))
                gc.SetBrush(wx.Brush("#DD5555"))
            else:
                gc.SetPen(wx.Pen("#333333", 1.5))
                gc.SetBrush(wx.Brush("#333333", wx.TRANSPARENT))
            gc.DrawRoundedRectangle(32, 70, 10, 10, 2)
            gc.DrawText("e", 35, 69)

        evt.Skip()
       
class TransportButtons(wx.Panel):
    def __init__(self, parent, playCallback=None, recordCallback=None):
        super(TransportButtons, self).__init__(parent)

        self.playmode = self.recordmode = 0
        self.playCallback = playCallback
        self.recordCallback = recordCallback

        self.playIcon = wx.Bitmap(ICON_PLAY, wx.BITMAP_TYPE_PNG)
        self.playPressedIcon = wx.Bitmap(ICON_PLAY_PRESSED, wx.BITMAP_TYPE_PNG)
        self.recordIcon = wx.Bitmap(ICON_RECORD, wx.BITMAP_TYPE_PNG)
        self.recordPressedIcon = wx.Bitmap(ICON_RECORD_PRESSED, wx.BITMAP_TYPE_PNG)
        
        self.play = wx.BitmapButton(self, wx.ID_ANY, self.playIcon)
        self.play.SetToolTip(QLiveTooltip('Play / Stop'))
        self.play.Bind(wx.EVT_BUTTON, self.onPlay)

        self.record = wx.BitmapButton(self, wx.ID_ANY, self.recordIcon)
        self.record.SetToolTip(QLiveTooltip('Record'))
        self.record.Bind(wx.EVT_BUTTON, self.onRecord)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.play, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 5)
        box.Add(self.record, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 5)
        self.SetSizer(box)

    def onPlay(self, evt):
        self.playmode = (self.playmode + 1) % 2
        if self.playmode == 1:
            self.play.SetBitmapLabel(self.playPressedIcon)
            self.record.Disable()
        else:
            self.play.SetBitmapLabel(self.playIcon)
            self.record.SetBitmapLabel(self.recordIcon)
            self.record.Enable()
            self.recordmode = 0
        if self.playCallback is not None:
            self.playCallback(self.playmode)

    def onRecord(self, evt):
        self.recordmode = self.playmode = (self.recordmode + 1) % 2
        if self.recordmode == 1:
            self.record.SetBitmapLabel(self.recordPressedIcon)
            self.play.SetBitmapLabel(self.playPressedIcon)
        else:
            self.record.SetBitmapLabel(self.recordIcon)
            self.play.SetBitmapLabel(self.playIcon)
        if self.recordCallback is not None:
            self.recordCallback(self.recordmode)

class CueButton(wx.Panel):
    def __init__(self, parent, size, number, evtHandler):
        wx.Panel.__init__(self, parent, -1, size=size, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(CUEBUTTON_UNSELECTED_COLOUR)
        self.learning = False
        self.midinote = None
        self.labtext = stattext.GenStaticText(self, -1, label="", 
                                              style=wx.ALIGN_CENTER)
        self.labtext.SetBackgroundColour(CUEBUTTON_UNSELECTED_COLOUR)
        self.evtHandler = evtHandler
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        self.labtext.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.labtext.Bind(wx.EVT_RIGHT_DOWN, self.midiLearn)
        wx.CallAfter(self.setNumber, number)

    def midiLearn(self, evt):
        midi = QLiveLib.getVar("MidiServer")
        # remove current binding
        if evt.ShiftDown():
            self.learning = False
            self.select(0)
            midi.noteonscan(None)
            if self.midinote is not None:
                midi.unbind("noteon", self.midinote)
            self.midinote = None
            self.SetToolTip(QLiveTooltip(""))
        # stop midi learn
        elif self.learning:
            self.learning = False
            self.select(0)
            midi.noteonscan(None)
        # start midi learn
        else:
            self.learning = True
            self.SetBackgroundColour(MIDILEARN_COLOUR)
            self.labtext.SetBackgroundColour(MIDILEARN_COLOUR)
            midi.noteonscan(self.getMidiScan)            

    def assignMidi(self, num):
        self.midinote = num
        self.SetToolTip(QLiveTooltip("Midi key: %d" % num))
        QLiveLib.getVar("MidiServer").bind("noteon", num, self.midi)

    def getMidiScan(self, num, midichnl):
        if num != -1:
            self.assignMidi(num)
        self.learning = False
        self.select(0)
 
    def midi(self, pitch, vel):
        self.evtHandler(self.getNumber())
        
    def OnLeftDown(self, evt):
        self.evtHandler(self.getNumber())

    def OnSize(self, evt):
        self.labtext.Center()

    def setNumber(self, x):
        try:
            self.number = x
            wx.CallAfter(self.labtext.SetLabel, str(self.number))
            self.labtext.Center()
        except:
            pass

    def getNumber(self):
        return self.number

    def select(self, state):
        if state:
            wx.CallAfter(self.SetBackgroundColour, CUEBUTTON_SELECTED_COLOUR)
            wx.CallAfter(self.labtext.SetBackgroundColour, CUEBUTTON_SELECTED_COLOUR)
        else:
            wx.CallAfter(self.SetBackgroundColour, CUEBUTTON_UNSELECTED_COLOUR)
            wx.CallAfter(self.labtext.SetBackgroundColour, CUEBUTTON_UNSELECTED_COLOUR)

    def getSaveDict(self):
        return {"number": self.number, "midinote": self.midinote}

    def setSaveDict(self, dict):
        midinote = dict.get("midinote", None)
        if midinote is not None:
            self.assignMidi(midinote)
        self.setNumber(dict["number"])

class MeterControlSlider(wx.Panel):
    def __init__(self, parent, minvalue, maxvalue, init=None, pos=(0,0), 
                 size=(28,150), outFunction=None, outLinValue=False, 
                 backColour=None):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=pos, size=size,
                            style=wx.NO_BORDER | wx.WANTS_CHARS | wx.EXPAND)
        self.parent = parent
        if backColour:
            self.backgroundColour = backColour
        else:
            self.backgroundColour = BACKGROUND_COLOUR
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(self.backgroundColour)
        self.midiBackgroundColour = None

        self.knobSize = 11
        self.knobHalfSize = 5
        self.sliderWidth = size[0] - 23
        self.meterWidth = 8
        self.meterHeight = 0
        self.meterOffset = 30

        self.outLinValue = outLinValue
        self.outFunction = outFunction
        self.SetRange(minvalue, maxvalue)
        self.selected = False
        self.propagate = False
        self.midictl = None
        self.label = ''
        self.new = ''
        if init != None:
            self.SetValue(init, False)
        else:
            self.SetValue(minvalue, False)
        self.clampPos()
        self.amplitude = self.last_amplitude = 0.0

        self.greybrush = wx.Brush("#444444")
        self.selectbrush = wx.Brush("#CCCCCC")
        self.selectpen = wx.Pen("#CCCCCC")
        self.textrect = wx.Rect(0, size[1]-29, size[0], 16)
        self.hlrect = wx.Rect(0, size[1]-28, size[0], 13)
        self.midirect = wx.Rect(0, size[1]-16, size[0], 16)

        self.needBackground = True
        self.backBitmap = None
        self.createKnobBitmap()
        self.createMeterBitmap()

        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.DoubleClick)
        self.Bind(wx.EVT_MOTION, self.MouseMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)
        self.Bind(wx.EVT_KILL_FOCUS, self.LooseFocus)

        if sys.platform in ['win32', 'linux2']:
            self.font = wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.NORMAL, 
                                wx.FONTWEIGHT_BOLD, face="Monospace")
        else:
            self.font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.NORMAL, 
                                wx.FONTWEIGHT_NORMAL, face="Monospace")

    def createKnobBitmap(self):
        b = wx.EmptyBitmap(10, self.knobSize)
        dc = wx.MemoryDC(b)
        gc = wx.GraphicsContext_Create(dc)
        dc.SetBackground(wx.Brush(self.backgroundColour))
        dc.Clear()
        gc.SetPen(wx.Pen("#444444"))
        gc.SetBrush(self.greybrush)
        p1 = (1, 1)
        p2 = (1, self.knobSize-1)
        p3 = (9, self.knobHalfSize)
        gc.DrawLines([p1,p2,p3])
        dc.SelectObject(wx.NullBitmap)
        self.knobBitmap = b

    def createMeterBitmap(self):
        w, h = self.meterWidth, self.GetSize()[1] - self.meterOffset
        f = wx.EmptyBitmap(w,h)
        dcf = wx.MemoryDC(f)
        dcf.SetPen(wx.Pen("#000000", width=1))
        steps = int(h / 10.0 + 0.5)
        bounds = int(steps / 6.0)
        for i in range(steps):
            if i == (steps - 1):
                dcf.SetBrush(wx.Brush("#FF0000"))
            elif i >= (steps - bounds):
                dcf.SetBrush(wx.Brush("#CC0000"))
            elif i >= (steps - (bounds*2)):
                dcf.SetBrush(wx.Brush("#CCCC00"))
            else:
                dcf.SetBrush(wx.Brush("#00CC00"))
            ii = steps - 1 - i
            dcf.DrawRectangle(0, ii*10, w, 11)
        dcf.DrawLine(0, 0, w, 0)
        dcf.SelectObject(wx.NullBitmap)
        self.bitmap = f

    def setRms(self, *args):
        if args[0] < 0:
            return
        if not args:
            self.amplitude = 0.0
        else:
            self.amplitude = args[0]
        if self.amplitude != self.last_amplitude:
            self.last_amplitude = self.amplitude
            h = self.GetSize()[1] - self.meterOffset
            db = math.log10(self.amplitude+0.00001) * 0.2 + 1.
            self.meterHeight = int(db * h)
            self.needBackground = False
            wx.CallAfter(self.Refresh)

    def setMidiCtl(self, x, propagate=True):
        self.propagate = propagate
        self.midictl = x
        wx.CallAfter(self.Refresh)

    def getMidiCtl(self):
        return self.midictl

    def getMinValue(self):
        return self.minvalue

    def getMaxValue(self):
        return self.maxvalue

    def setSliderHeight(self, height):
        self.sliderHeight = height
        wx.CallAfter(self.Refresh)

    def setSliderWidth(self, width):
        self.sliderWidth = width
        wx.CallAfter(self.Refresh)

    def SetRange(self, minvalue, maxvalue):
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def getRange(self):
        return [self.minvalue, self.maxvalue]

    def scale(self):
        h = self.GetSize()[1] - self.meterOffset
        inter = tFromValue(h-self.pos, self.knobHalfSize, h-self.knobHalfSize)
        return interpFloat(inter, self.minvalue, self.maxvalue)

    def SetValue(self, value, propagate=True):
        # TODO: setting value is often ovveride by
        # setRms calls and the label is not always updated
        self.propagate = propagate
        if self.HasCapture():
            self.ReleaseMouse()
        value = clamp(value, self.minvalue, self.maxvalue)
        t = tFromValue(value, self.minvalue, self.maxvalue)
        self.value = interpFloat(t, self.minvalue, self.maxvalue)
        self.clampPos()
        self.selected = False
        self.valueChanged()
        wx.CallAfter(self.Refresh)

    def GetValue(self):
        return self.value

    def valueChanged(self):
        if self.outFunction and self.propagate:
            if self.outLinValue:
                self.outFunction(pow(10, self.value * 0.05))
            else:
                self.outFunction(self.value)
        self.propagate = True
        self.labelChanged()

    def labelChanged(self):
        if self.selected and self.new:
            val = self.new
        else:
            val = self.GetValue()
            if abs(val) >= 100:
                val = '%.0f' % val
            elif abs(val) >= 10:
                val = '%.1f' % val
            elif abs(val) < 10:
                val = '%.2f' % val
        if self.GetValue() >= 0:
            val = " " + val
        self.label = val

    def LooseFocus(self, event):
        self.selected = False
        wx.CallAfter(self.Refresh)

    def keyDown(self, event):
        if self.selected:
            char = ''
            if event.GetKeyCode() in range(324, 334):
                char = str(event.GetKeyCode() - 324)
            elif event.GetKeyCode() == 390:
                char = '-'
            elif event.GetKeyCode() == 391:
                char = '.'
            elif event.GetKeyCode() == wx.WXK_BACK:
                if self.new != '':
                    self.new = self.new[0:-1]
                    self.labelChanged()
            elif event.GetKeyCode() < 256:
                char = chr(event.GetKeyCode())
            if char in ['0','1','2','3','4','5','6','7','8','9','.','-']:
                self.new += char
                self.labelChanged()
            elif event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
                self.SetValue(eval(self.new))
                self.new = ''
                self.selected = False
            wx.CallAfter(self.Refresh)
        event.Skip()

    def MouseDown(self, evt):
        h = self.GetSize()[1] - self.meterOffset
        posY = evt.GetPosition()[1]
        if evt.ShiftDown():
            self.DoubleClick(evt)
            return
        if posY < h:
            self.pos = clamp(evt.GetPosition()[1], self.knobHalfSize, h)
            self.value = self.scale()
            self.CaptureMouse()
            self.selected = False
            self.valueChanged()
            wx.CallAfter(self.Refresh)
        evt.Skip()

    def MouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def DoubleClick(self, event):
        w, h = self.GetSize()
        pos = event.GetPosition()
        if self.textrect.Contains(pos):
            self.selected = True
        wx.CallAfter(self.Refresh)
        event.Skip()

    def MouseMotion(self, evt):
        posY = evt.GetPosition()[1]
        h = self.GetSize()[1] - self.meterOffset
        if evt.LeftIsDown() and evt.Dragging():
            self.pos = clamp(posY, self.knobHalfSize, h-self.knobHalfSize)
            self.value = self.scale()
            self.selected = False
            self.valueChanged()
            wx.CallAfter(self.Refresh)

    def OnResize(self, evt):
        w, h = self.GetSize()
        self.createKnobBitmap()
        self.createMeterBitmap()
        self.textrect = wx.Rect(0, h-29, w, 16)
        self.hlrect = wx.Rect(0, h-28, w, 13)
        self.midirect = wx.Rect(0, h-16, w, 16)
        self.clampPos()
        wx.CallAfter(self.Refresh)

    def clampPos(self):
        h = self.GetSize()[1] - self.meterOffset
        val = tFromValue(self.value, self.minvalue, self.maxvalue)
        self.pos = (1.0 - val) * (h - self.knobSize) + self.knobHalfSize
        self.pos = clamp(self.pos, self.knobHalfSize, h-self.knobHalfSize)

    def setBackgroundColour(self, colour):
        self.backgroundColour = colour
        self.SetBackgroundColour(self.backgroundColour)
        wx.CallAfter(self.Refresh)

    def setMidiBackgroundColour(self, colour):
        self.midiBackgroundColour = colour
        wx.CallAfter(self.Refresh)

    def revertMidiBackgroundColour(self):
        self.midiBackgroundColour = None
        wx.CallAfter(self.Refresh)

    def drawBackground(self):
        w, h = self.GetSize()
        bitmap = wx.EmptyBitmap(w, h)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)

        dc.SetBackground(wx.Brush(self.backgroundColour))
        dc.Clear()

        if self.selected:
            dc.SetPen(self.selectpen)
            dc.SetBrush(self.selectbrush)
            dc.DrawRectangleRect(self.hlrect)

        dc.SetFont(self.font)
        dc.SetTextForeground('#000000')
        dc.DrawLabel(self.label, self.textrect, 
                     wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        if self.midiBackgroundColour:
            dc.SetPen(wx.Pen(self.midiBackgroundColour))
            dc.SetBrush(wx.Brush(self.midiBackgroundColour))
            dc.DrawRectangleRect(self.midirect)

        if self.midictl is None:
            midilabel = "M: ?"
        else:
            midilabel = "M: %d" % self.midictl
        dc.DrawLabel(midilabel, self.midirect, wx.ALIGN_CENTER)

        dc.SelectObject(wx.NullBitmap)
        self.backBitmap = bitmap

    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.AutoBufferedPaintDC(self)

        if self.needBackground or self.backBitmap is None:
            self.drawBackground()
        dc.DrawBitmap(self.backBitmap, 0, 0)

        # Draw meter
        dc.SetBrush(self.greybrush)
        dc.DrawRectangle(11, 0, self.meterWidth, h-self.meterOffset+1)
        if self.meterHeight > 0:
            dc.SetClippingRegion(11, h-self.meterHeight, 
                                 self.meterWidth, self.meterHeight)
            dc.DrawBitmap(self.bitmap, 11, 0)
            dc.DestroyClippingRegion()

        dc.DrawBitmap(self.knobBitmap, 0, self.pos-self.knobHalfSize)

        self.needBackground = True

        evt.Skip()

class QLiveTooltip(wx.ToolTip):
    def __init__(self, tip):
        if QLiveLib.getVar("useTooltips") is True:
            wx.ToolTip.__init__(self, tip)
        else:
            wx.ToolTip.__init__(self, '')

if __name__ == "__main__":
    from pyo64 import *
    s = Server().boot().start()
    class TestFrame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None)
            panel = wx.Panel(self)
            panel.SetBackgroundColour(BACKGROUND_COLOUR)
            knob = QLiveControlKnob(panel, 20, 20000, 1000, pos=(20,20), 
                                    label="Freq", outFunction = self.callback)
            self.Show()

        def callback(self, value):
            pass

    app = wx.App()
    f = TestFrame()
    app.MainLoop()
