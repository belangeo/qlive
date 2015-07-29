import time
from pyo64 import *
from constants import *
from fxbox_def import *
import QLiveLib

class SoundFilePlayer:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        sndfolder = os.path.join(QLiveLib.getVar("projectFolder"), "sounds")        
        path = os.path.join(sndfolder, self.filename)
        self.table = SndTable(path)
        self.gain = SigTo(0, time=0.02, init=0)
        self.looper = Looper(self.table, mul=self.gain).stop()
        self.directout = False
        self.mixerInputId = -1

    def setAttributes(self, dict):
        self.looper.mode = dict[ID_COL_LOOPMODE]
        self.looper.pitch = dict[ID_COL_TRANSPO]
        self.gain.value = pow(10, dict[ID_COL_GAIN] * 0.05)
        self.looper.start = dict[ID_COL_STARTPOINT]
        self.looper.dur = dict[ID_COL_ENDPOINT] - dict[ID_COL_STARTPOINT]
        self.looper.xfade = dict[ID_COL_CROSSFADE]
        if dict[ID_COL_PLAYING] == 1:
            self.looper.reset()
            self.looper.play()
            audioMixer = QLiveLib.getVar("AudioMixer")
            if dict[ID_COL_DIRECTOUT] and not self.directout:
                self.directout = True
                for i in range(len(self.looper)):
                    chnl = (i + dict[ID_COL_CHANNEL]) % NUM_CHNLS
                    self.mixerInputId = audioMixer.addToMixer(chnl, self.looper[i])
            elif not dict[ID_COL_DIRECTOUT] and self.directout:
                self.directout = False
                audioMixer.delFromMixer(self.mixerInputId)
        elif dict[ID_COL_PLAYING] == 0:
            self.looper.stop()

    def setAttribute(self, id, value):
        if id == ID_COL_LOOPMODE:
            self.looper.mode = value
        elif id == ID_COL_TRANSPO:
            self.looper.pitch = value
        elif id == ID_COL_GAIN:
            self.gain.value = pow(10, value * 0.05)
        elif id == ID_COL_STARTPOINT:
            self.looper.start = value
        elif id == ID_COL_ENDPOINT:
            self.looper.dur = value - self.looper.start
        elif id == ID_COL_CROSSFADE:
            self.looper.xfade = value
        elif id == ID_COL_PLAYING:
            if value == "Play":
                self.looper.play()
            elif value == "Stop":
                self.looper.stop()
        # handle ID_COL_DIRECTOUT and ID_COL_CHANNEL

class BaseAudioObject:
    def __init__(self, chnls, ctrls, values, interps):
        self.chnls = chnls
        for i, ctrl in enumerate(ctrls):
            name = ctrl[0]
            if values is None:
                val = ctrl[1]
            else:
                val = values[i]
            if interps is None:
                inter = 0.01
            else:
                inter = interps[i]
            if name == "gain":
                val = pow(10, val * 0.05)
            setattr(self, name, SigTo(val, time=inter, init=val))

        self.input = Sig([0] * self.chnls)

    def setInput(self, sig):
        self.input.value = sig

    def getOutput(self):
        return self.output

    def setEnable(self, x):
        self.output.value = [self.input, self.process][x]

class AudioNone(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.output = Sig(self.input)

    def setEnable(self, x):
        self.output.value = [[0.0] * self.chnls, self.input][x]
    
class AudioIn(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.output = Sig(self.input, mul=self.gain)

    def setEnable(self, x):
        self.output.value = [[0.0] * self.chnls, self.input][x]

class FxLowpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquad(self.input, freq=self.freq, q=self.Q, mul=self.gain)
        self.process = Interp(self.input, self.filter, self.dryWet)
        self.output = Sig(self.process)

class FxHighpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.filter = Biquad(self.input, freq=self.freq, q=self.Q, type=1, mul=self.gain)
        self.process = Interp(self.input, self.filter, self.dryWet)
        self.output = Sig(self.process)

class FxFreeverb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.reverb = Freeverb(self.input, self.size, self.damp, 1, mul=self.gain)
        self.process = Interp(self.input, self.reverb, self.dryWet)
        self.output = Sig(self.process)

class FxStereoVerb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.reverb = STRev(self.input, self.pan, self.revtime, self.cutoff, 1, mul=self.gain)
        self.process = Interp(self.input, self.reverb, self.dryWet)
        self.output = Sig(self.process)

class FxDisto(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.disto = Disto(self.input, self.drive, self.slope, mul=self.gain)
        self.process = Interp(self.input, self.disto, self.dryWet)
        self.output = Sig(self.process)

class FxDelay(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.delay = Delay(self.input, self.deltime, self.feed, 5, mul=self.gain)
        self.process = Interp(self.input, self.delay, self.dryWet)
        self.output = Sig(self.process)

class FxCompressor(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.comp = Compress(self.input, self.thresh, self.ratio, self.attack,
                             self.decay, 5, knee=0.5, mul=self.gain)
        self.process = Interp(self.input, self.comp, self.dryWet)
        self.output = Sig(self.process)

class FxFreqShift(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.shifter = FreqShift(self.input, self.shift, mul=self.gain)
        self.process = Interp(self.input, self.shifter, self.dryWet)
        self.output = Sig(self.process)

class FxHarmonizer(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.harmon = Harmonizer(self.input, self.transpo, self.feed, mul=self.gain)
        self.process = Interp(self.input, self.harmon, self.dryWet)
        self.output = Sig(self.process)

class FxAudioOut(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = self.input
        self.output = Sig(self.process, mul=self.gain)

AUDIO_OBJECTS = {"None": AudioNone, "AudioIn": AudioIn, "Lowpass": FxLowpass,
                "Highpass": FxHighpass, "Freeverb": FxFreeverb, 
                "StereoVerb": FxStereoVerb, "Disto": FxDisto, "Delay": FxDelay, 
                "Compressor": FxCompressor, "FreqShift": FxFreqShift,
                "Harmonizer": FxHarmonizer, "AudioOut": FxAudioOut}

class AudioServer:
    def __init__(self):
        self.server = Server(buffersize=64)
        self.server.setMidiInputDevice(99)
        self.server.boot()
        self.soundfiles = []
        self.audioObjects = []
        self.recording = False
        self.cueMidiLearn = CueMidiLearn(self.cueMidiLearnCallback)
        self.cueMidiLearnState = None
        self.cueMidiNotes = {}
        self.cueMidiNotein = Notein(poly=1)
        self.cueMidiCall = TrigFunc(self.cueMidiNotein["trigon"], self.cueMidiNoteCallback)

    def getSaveState(self):
        return {"cueMidiNotes": self.cueMidiNotes}

    def setSaveState(self, state):
        if state:
            self.cueMidiNotes = state["cueMidiNotes"]
            for val, state in self.cueMidiNotes.items():
                if state in ["up", "down"]:
                    QLiveLib.getVar("ControlPanel").setButtonTooltip(state, 
                                                        "Midi key: %d" % val)

    def createSoundFilePlayers(self):
        objs = QLiveLib.getVar("Soundfiles").getSoundFileObjects()
        for obj in objs:
            id = obj.getId()
            filename = obj.getFilename()
            player = SoundFilePlayer(id, filename)
            player.setAttributes(obj.getAttributes())
            self.soundfiles.append(player)
            obj.setPlayerRef(player)

    def createBoxObjects(self):
        tracks = QLiveLib.getVar("FxTracks").getTracks()
        for track in tracks:
            chnls = 1
            for but in track.getButtonInputs():
                name = but.name
                if not name: name = "None"
                if name == "AudioIn":
                    inchnls = but.getInChannels()
                    numchnls = inchnls.count(1)
                    ismulti = but.getIsMultiChannels()
                    if ismulti:
                        chnls = max(chnls, numchnls)
                    else:
                        chnls = 1
                ctrls = INPUT_DICT[name]["ctrls"]
                values = but.getCurrentValues()
                if values is not None:
                    obj = AUDIO_OBJECTS[name](chnls, ctrls, values,
                                              but.getCurrentInterps())
                    but.setAudioRef(obj)
                    self.audioObjects.append(obj)
            for but in track.getButtonFxs():
                name = but.name
                if not name: name = "None"
                ctrls = FX_DICT[name]["ctrls"]
                values = but.getCurrentValues()
                if values is not None:
                    obj = AUDIO_OBJECTS[name](chnls, ctrls, values,
                                              but.getCurrentInterps())
                    but.setAudioRef(obj)
                    self.audioObjects.append(obj)
            
    def resetPlayerRefs(self):
        objs = QLiveLib.getVar("Soundfiles").getSoundFileObjects()
        for obj in objs:
            obj.setPlayerRef(None)

    def resetObjectRefs(self):
        tracks = QLiveLib.getVar("FxTracks").getTracks()
        for track in tracks:
            for but in track.getButtonInputs():
                but.setAudioRef(None)
            for but in track.getButtonFxs():
                but.setAudioRef(None)

    def start(self, state):
        if state:
            QLiveLib.getVar("AudioMixer").resetMixer()
            self.createSoundFilePlayers()
            self.createBoxObjects()
            QLiveLib.getVar("FxTracks").start()
            self.server.start()
        else:
            if self.recording:
                self.recording = False
                self.recStop()
            self.server.stop()
            self.resetPlayerRefs()
            self.resetObjectRefs()
            self.soundfiles = []
            self.audioObjects = []
            QLiveLib.getVar("CuesPanel").onSaveCue()

    def record(self, state):
        if state:
            self.recording = True
            self.recStart()
            self.start(True)
        else:
            self.recording = False
            self.recStop()
            self.start(False)

    def stop(self):
        self.server.stop()

    def shutdown(self):
        self.server.shutdown()

    def isStarted(self):
        return self.server.getIsStarted()

    def isBooted(self):
        return self.server.getIsBooted()

    def recStart(self, filename="", fileformat=0, sampletype=0):
        self.server.recordOptions(fileformat=fileformat, sampletype=sampletype)
        if not filename:
            filename = os.path.basename(QLiveLib.getVar("currentProject"))
        filename, ext = os.path.splitext(filename)
        filename = os.path.join(QLiveLib.getVar("projectFolder"), "bounce", filename)
        if fileformat >= 0 and fileformat < 8:
            ext = RECORD_EXTENSIONS[fileformat]
        else: 
            ext = ".wav"
        date = time.strftime('_%d_%b_%Y_%Hh%M')
        complete_filename = QLiveLib.toSysEncoding(filename+date+ext)
        self.server.recstart(complete_filename)

    def recStop(self):
        self.server.recstop()

    def cueMidiNoteCallback(self):
        if not self.cueMidiLearn.isStarted():
            if self.cueMidiNotes:
                pit = self.cueMidiNotein.get("pitch")
                if pit in self.cueMidiNotes:
                    QLiveLib.getVar("ControlPanel").moveCueFromMidi(self.cueMidiNotes[pit])

    def setCueMidiLearnState(self, which):
        self.cueMidiLearnState = which

    def startCueMidiLearn(self):
        self.cueMidiLearn.scan()

    def stopCueMidiLearn(self):
        self.cueMidiLearn.stop()
        
    def cueMidiLearnCallback(self, val, ctl=False):
        if ctl:
            self.cueMidiCtls[val] = self.cueMidiLearnState
        else:
            self.cueMidiNotes[val] = self.cueMidiLearnState
        QLiveLib.getVar("ControlPanel").setButtonTooltip(self.cueMidiLearnState, 
                                                        "Midi key: %d" % val)
        self.cueMidiLearnState = None
        QLiveLib.getVar("ControlPanel").resetCueButtonBackgroundColour()

class MidiLearn:
    def __init__(self, callback):
        self.callback = callback
        self.scanner = CtlScan2(self.scanned, True).stop()
    
    def scan(self):
        self.scanner.reset()
        self.scanner.play()

    def stop(self):
        self.scanner.stop()

    def scanned(self, ctlnum, midichnl):
        self.callback(ctlnum, midichnl)
        self.scanner.stop()

class CueMidiLearn:
    def __init__(self, callback):
        self.callback = callback
        self.started = False
        self.current_pitch = -1
        self.scanner = CtlScan(self.scanned, True).stop()
        self.notes = Notein(poly=1).stop()
        self.notecall = TrigFunc(self.notes["trigon"], self.noteon).stop()
        self.notecall2 = TrigFunc(self.notes["trigoff"], self.noteoff).stop()
    
    def scan(self):
        self.scanner.reset()
        self.scanner.play()
        self.notes.play()
        self.notecall.play()
        self.notecall2.play()
        self.started = True

    def stop(self):
        self.scanner.stop()
        self.notes.stop()
        self.notecall.stop()
        self.notecall2.stop()
        self.started = False

    def scanned(self, ctlnum):
        if 0:
            self.callback(ctlnum, ctl=True)
            self.stop()

    def noteon(self):
        pit = int(self.notes.get("pitch"))
        self.current_pitch = pit
        self.callback(pit)
    
    def noteoff(self):
        pit = int(self.notes.get("pitch"))
        if pit == self.current_pitch:
            self.stop()
            self.current_pitch = -1

    def isStarted(self):
        return self.started