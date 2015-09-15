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
        self.transpo = SigTo(1, time=0.01, init=1)
        self.gain = SigTo(0, time=0.01, init=0)
        self.looper = Looper(self.table, pitch=self.transpo, mul=self.gain).stop()
        self.directout = False
        self.mixerInputId = -1

    def setAttributes(self, dict):
        self.looper.mode = dict[ID_COL_LOOPMODE]
        self.transpo.value = dict[ID_COL_TRANSPO]
        self.transpo.time = dict.get(ID_COL_TRANSPOX, 0.01)
        self.gain.value = pow(10, dict[ID_COL_GAIN] * 0.05)
        self.gain.time = dict.get(ID_COL_GAINX, 0.01)
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
            self.transpo.value = value
        elif id == ID_COL_TRANSPOX:
            self.transpo.time = value
        elif id == ID_COL_GAIN:
            self.gain.value = pow(10, value * 0.05)
        elif id == ID_COL_GAINX:
            self.gain.time = value
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

class FxBandpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)        
        self.filter = Biquadx(self.input, freq=self.freq, q=self.Q, type=2, stages=2, mul=self.gain)
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

class FxPanning(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.panning = Pan(self.input, self.chnls, self.pan, self.spread, mul=self.gain)
        self.process = Interp(self.input, self.panning)
        self.output = Sig(self.process)

class FxAudioOut(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = self.input
        self.output = Sig(self.process, mul=self.gain)

AUDIO_OBJECTS = {"None": AudioNone, "AudioIn": AudioIn, "Lowpass": FxLowpass,
                "Highpass": FxHighpass, "Bandpass": FxBandpass, "Freeverb": FxFreeverb, 
                "StereoVerb": FxStereoVerb, "Disto": FxDisto, "Delay": FxDelay, 
                "Compressor": FxCompressor, "FreqShift": FxFreqShift,
                "Harmonizer": FxHarmonizer, "Panning": FxPanning, "AudioOut": FxAudioOut}

class AudioServer:
    def __init__(self):
        sr, bufferSize, audio, jackname, nchnls, inchnls, duplex = self.getPrefs()
        self.server = Server(sr=sr, buffersize=bufferSize, audio=audio, jackname=jackname, nchnls=nchnls, duplex=duplex)
        if inchnls != None:
            self.server.setIchnls(int(inchnls))
        self.server.deactivateMidi()
        self.server.boot()
        self.soundfiles = []
        self.audioObjects = []
        self.recording = False

    def getPrefs(self):
        sr = int(QLiveLib.getVar("sr"))
        bufferSize = int(QLiveLib.getVar("bufferSize"))
        audio = QLiveLib.getVar("audio")
        jackname = QLiveLib.getVar("jackname")
        nchnls = int(QLiveLib.getVar("nchnls"))
        inchnls = QLiveLib.getVar("inchnls")
        duplex = int(QLiveLib.getVar("duplex"))
        return sr, bufferSize, audio, jackname, nchnls, inchnls, duplex

    def getAvailableAudioMidiDrivers(self):
        inputDriverList, inputDriverIndexes = pa_get_input_devices()
        defaultInputDriver = inputDriverList[inputDriverIndexes.index(pa_get_default_input())]
        outputDriverList, outputDriverIndexes = pa_get_output_devices()
        defaultOutputDriver = outputDriverList[outputDriverIndexes.index(pa_get_default_output())]
        midiDriverList, midiDriverIndexes = pm_get_input_devices()
        if midiDriverList == []:
            defaultMidiDriver = ""
        else:
            defaultMidiDriver = midiDriverList[midiDriverIndexes.index(pm_get_default_input())]
        return inputDriverList, inputDriverIndexes, defaultInputDriver, outputDriverList, outputDriverIndexes, \
                defaultOutputDriver, midiDriverList, midiDriverIndexes, defaultMidiDriver

    def getSaveState(self):
        return {}

    def setSaveState(self, state):
        pass

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
            self.stop()
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
        self.server.setAmp(0)
        time.sleep(.1)
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

class MidiServer:
    def __init__(self):
        self.ctlscan_callback = None
        self.noteonscan_callback = None
        self.bindings = {"ctls": {}, "noteon": {}}
        self.listen = MidiListener(self._midirecv, 20)
        self.listen.start()

    def _midirecv(self, status, data1, data2):
        #print status, data1, data2
        if status & 0xF0 == 0x90 and data2 != 0: # noteon
            midichnl = status - 0x90 + 1
            if self.noteonscan_callback is not None:
                self.noteonscan_callback(data1, midichnl)
                self.noteonscan_callback = None
            elif data1 in self.bindings["noteon"]:
                for callback in self.bindings["noteon"][data1]:
                    callback(data1, data2)
        if status & 0xF0 == 0xB0: # control change
            midichnl = status - 0xB0 + 1
            if self.ctlscan_callback is not None:
                self.ctlscan_callback(data1, midichnl)
                self.ctlscan_callback = None
            if data1 in self.bindings["ctls"]:
                for callback in self.bindings["ctls"][data1]:
                    callback(data2)

    def ctlscan(self, callback):
        self.ctlscan_callback = callback

    def noteonscan(self, callback):
        if self.noteonscan_callback is not None:
            self.noteonscan_callback(-1, -1)
        self.noteonscan_callback = callback
        
    def bind(self, group, x, callback):
        if x in self.bindings[group]:
            self.bindings[group][x].append(callback)
        else:
            self.bindings[group][x] = [callback]
        
    def unbind(self, group, x, callback):
        if x in self.bindings[group]:
            if callback in self.bindings[group][x]:
                self.bindings[group][x].remove(callback)
                if not self.bindings[group][x]:
                    del self.bindings[group][x]
