import time
from pyo64 import *
from constants import *
from fxbox_def import *
import QLiveLib

class Automator:
    def __init__(self, init=0):
        # Globals
        self.server = QLiveLib.getVar("AudioServer")
        self.mixer = QLiveLib.getVar("AudioMixer")
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.mixmethod = 0
        # Main value
        self.param = SigTo(init, interpTime, init)
        # Envelope follower signal chain
        self.envInputs = [0] * NUM_INPUTS
        self.envActive = 0
        self.envThreshold = SigTo(-90, time=interpTime, init=-90)
        self.envCutoff = SigTo(20, time=interpTime, init=20)
        self.envMin = SigTo(0, time=interpTime, init=0)
        self.envMax = SigTo(1, time=interpTime, init=1)
        self.envInput = Gate(Sig(0), thresh=self.envThreshold)
        self.envFol = Follower(self.envInput, freq=self.envCutoff)
        self.env = Scale(self.envFol, 0, 1, self.envMin, self.envMax)
        self.envStop()

        self.auto = Sig(0)
        self.output = Interp(self.param, self.auto, 0)

    def sig(self):
        return self.output

    def setParam(self, value=None, time=None):
        if time is not None:
            self.param.time = time
        if value is not None:
            self.param.value = value

    def envPlay(self):
        self.envThreshold.play()
        self.envCutoff.play()
        self.envMin.play()
        self.envMax.play()
        self.envInput.play()
        self.envFol.play()
        self.env.play()

    def envStop(self):
        self.envThreshold.stop()
        self.envCutoff.stop()
        self.envMin.stop()
        self.envMax.stop()
        self.envInput.stop()
        self.envFol.stop()
        self.env.stop()

    def setEnvAttributes(self, dict):
        active = dict[ID_ENV_ACTIVE]
        if active and not self.envActive:
            self.output.interp = 1
            self.envPlay()
        elif not active and self.envActive:
            self.output.interp = 0
            self.envStop()
        self.envActive = active
        if self.envInputs != dict[ID_ENV_INPUTS]:
            self.envInputs = dict[ID_ENV_INPUTS]
            new = Mix([self.mixer.getInputChannel(i).getOutput() \
                        for i, x in enumerate(self.envInputs) if x == 1])
            self.envInput.setInput(new, dict[ID_ENV_INPUTS_INTERP])
        self.envThreshold.time = dict[ID_ENV_THRESHOLD_INTERP]
        self.envThreshold.value = dict[ID_ENV_THRESHOLD]
        self.envCutoff.time = dict[ID_ENV_CUTOFF_INTERP]
        self.envCutoff.value = dict[ID_ENV_CUTOFF]
        self.envMin.time = dict[ID_ENV_MIN_INTERP]
        self.envMin.value = dict[ID_ENV_MIN]
        self.envMax.time = dict[ID_ENV_MAX_INTERP]
        self.envMax.value = dict[ID_ENV_MAX]

    def setAttributes(self, dict):
        if dict is not None:
            mixmethod = dict.get("mixmethod", 0)
            if mixmethod != self.mixmethod:
                self.mixmethod = mixmethod
                self.handleMixMethod()
            envDict = dict.get("env", None)
            if envDict is not None:
                self.setEnvAttributes(envDict)

    def handleMixMethod(self):
        if self.mixmethod == 0:
            self.auto.value = self.param + self.env
        elif self.mixmethod == 1:
            self.auto.value = self.param * self.env
        elif self.mixmethod == 2:
            self.auto.value = self.env
        elif self.mixmethod == 3:
            self.auto.value = self.env

class SoundFilePlayer:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename
        sndfolder = os.path.join(QLiveLib.getVar("projectFolder"), "sounds")
        path = os.path.join(sndfolder, self.filename)
        self.table = SndTable(path)
        self.chnls = len(self.table)
        self.transpo = Automator(init=1)
        self.gain = Automator(init=0)
        self.looper = Looper(self.table, pitch=self.transpo.sig(),
                             mul=self.gain.sig()).stop()
        self.directout = False
        self.mixerInputId = []
        self.chnl = 0

    def getId(self):
        return self.id

    def getChnls(self):
        return self.chnls

    def setAttributes(self, dict):
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.looper.mode = dict[ID_COL_LOOPMODE]
        self.transpo.setParam(dict[ID_COL_TRANSPO],
                              dict.get(ID_COL_TRANSPOX, interpTime))
        self.gain.setParam(pow(10, dict[ID_COL_GAIN] * 0.05),
                           dict.get(ID_COL_GAINX, interpTime))
        self.looper.start = dict[ID_COL_STARTPOINT]
        self.looper.dur = dict[ID_COL_ENDPOINT] - dict[ID_COL_STARTPOINT]
        self.looper.xfade = dict[ID_COL_CROSSFADE]
        self.chnl = dict[ID_COL_CHANNEL]
        if dict[ID_COL_PLAYING] == 1:
            self.looper.reset()
            self.looper.play()
        elif dict[ID_COL_PLAYING] == 0:
            self.looper.stop()
        self.handleRouting(dict[ID_COL_DIRECTOUT])
        if dict[ID_TRANSPO_AUTO] is not None:
            self.transpo.setAttributes(dict[ID_TRANSPO_AUTO])
        if dict[ID_GAIN_AUTO] is not None:
            self.gain.setAttributes(dict[ID_GAIN_AUTO])

    def setAttribute(self, id, value):
        if id == ID_COL_LOOPMODE:
            self.looper.mode = value
        elif id == ID_COL_TRANSPO:
            self.transpo.setParam(value=value)
        elif id == ID_COL_TRANSPOX:
            self.transpo.setParam(time=value)
        elif id == ID_COL_GAIN:
            self.gain.setParam(value=pow(10, value * 0.05))
        elif id == ID_COL_GAINX:
            self.gain.setParam(time=value)
        elif id == ID_COL_STARTPOINT:
            self.looper.start = value
        elif id == ID_COL_ENDPOINT:
            self.looper.dur = value - self.looper.start
        elif id == ID_COL_CROSSFADE:
            self.looper.xfade = value
        elif id == ID_COL_PLAYING:
            if value == 1:
                self.looper.play()
            elif value == 0:
                self.looper.stop()
        elif id == ID_COL_DIRECTOUT:
            self.handleRouting(value)
        elif id == ID_COL_CHANNEL:
            self.changeRouting(value)
        elif id == ID_TRANSPO_AUTO:
            self.transpo.setAttributes(value)
        elif id == ID_GAIN_AUTO:
            self.gain.setAttributes(value)

    def changeRouting(self, chnl):
        if chnl != self.chnl and self.directout:
            self.chnl = chnl
            audioMixer = QLiveLib.getVar("AudioMixer")
            for id in self.mixerInputId:
                audioMixer.delFromMixer(id)
            self.mixerInputId = []
            for i in range(len(self.looper)):
                chnl = (i + self.chnl) % NUM_OUTPUTS
                id = audioMixer.addToMixer(chnl, self.looper[i])
                self.mixerInputId.append(id)

    def handleRouting(self, state):
        audioMixer = QLiveLib.getVar("AudioMixer")
        if state and not self.directout:
            self.directout = True
            for i in range(len(self.looper)):
                chnl = (i + self.chnl) % NUM_OUTPUTS
                id = audioMixer.addToMixer(chnl, self.looper[i])
                self.mixerInputId.append(id)
        elif not state and self.directout:
            self.directout = False
            for id in self.mixerInputId:
                audioMixer.delFromMixer(id)
            self.mixerInputId = []

class BaseAudioObject:
    def __init__(self, chnls, ctrls, values, interps):
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.chnls = chnls
        for i, ctrl in enumerate(ctrls):
            name = ctrl[0]
            if values is None:
                val = ctrl[1]
            else:
                val = values[i]
            if interps is None:
                inter = interpTime
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

class SoundfileIn(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.output = Sig(self.input, mul=self.gain)

    def setEnable(self, x):
        self.output.value = [[0.0] * self.chnls, self.input][x]

class FxLowpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquad(self.input, freq=self.freq, q=self.Q,
                             mul=self.gain)
        self.process = Interp(self.input, self.filter, self.dryWet)
        self.output = Sig(self.process)

class FxHighpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquad(self.input, freq=self.freq, q=self.Q, type=1,
                             mul=self.gain)
        self.process = Interp(self.input, self.filter, self.dryWet)
        self.output = Sig(self.process)

class FxBandpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquadx(self.input, freq=self.freq, q=self.Q, type=2,
                              stages=2, mul=self.gain)
        self.process = Interp(self.input, self.filter, self.dryWet)
        self.output = Sig(self.process)

class FxFreeverb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = Freeverb(self.input, self.size, self.damp, 1,
                               mul=self.gain)
        self.process = Interp(self.input, self.reverb, self.dryWet)
        self.output = Sig(self.process)

class FxStereoVerb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = STRev(self.input, self.pan, self.revtime, self.cutoff,
                            1, mul=self.gain)
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
        self.delay = Delay(self.input, self.deltime, self.feed, 5,
                           mul=self.gain)
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
        self.harmon = Harmonizer(self.input, self.transpo, self.feed,
                                 mul=self.gain)
        self.process = Interp(self.input, self.harmon, self.dryWet)
        self.output = Sig(self.process)

class FxPanning(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = Pan(self.input, self.chnls, self.pan, self.spread,
                           mul=self.gain)
        self.output = Sig(self.process)

class FxAudioOut(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = self.input
        self.output = Sig(self.process, mul=self.gain)

AUDIO_OBJECTS = {"None": AudioNone, "AudioIn": AudioIn,
                 "Soundfile": SoundfileIn, "Lowpass": FxLowpass,
                "Highpass": FxHighpass, "Bandpass": FxBandpass,
                "Freeverb": FxFreeverb, "StereoVerb": FxStereoVerb,
                "Disto": FxDisto, "Delay": FxDelay, "Compressor": FxCompressor,
                "FreqShift": FxFreqShift, "Harmonizer": FxHarmonizer,
                "Panning": FxPanning, "AudioOut": FxAudioOut}

class AudioServer:
    def __init__(self):
        prefs = self.getPrefs()
        sr = prefs[0]
        bufferSize = prefs[1]
        audio = prefs[2]
        jackname = prefs[3]
        nchnls = prefs[4]
        inchnls = prefs[5]
        duplex = prefs[6]
        outdev = prefs[7]
        indev = prefs[8]
        firstin = prefs[9]
        firstout = prefs[10]
        self.server = Server(sr=sr, buffersize=bufferSize, audio=audio,
                             jackname=jackname, nchnls=nchnls, duplex=duplex)
        if inchnls != None:
            self.server.setIchnls(inchnls)
        self.server.deactivateMidi()
        self.soundfiles = []
        self.audioObjects = []
        self.recording = False
        self.server.setOutputDevice(outdev)
        self.server.setInputOffset(firstin)
        self.server.setOutputOffset(firstout)
        if QLiveLib.getVar("duplex"):
            self.server.setInputDevice(indev)
        self.server.boot()

    def reinitServer(self):
        mixer = QLiveLib.getVar("AudioMixer")
        mixerPanel = QLiveLib.getVar("MixerPanel")
        restart = False
        reboot = False
        if self.isStarted():
            restart = True
            self.start(False)
            time.sleep(.1)
        mixer.deleteMixer()
        if self.isBooted():
            reboot = True
            self.shutdown()
            time.sleep(.1)

        prefs = self.getPrefs()
        sr = prefs[0]
        bufferSize = prefs[1]
        audio = prefs[2]
        jackname = prefs[3]
        nchnls = prefs[4]
        inchnls = prefs[5]
        duplex = prefs[6]
        outdev = prefs[7]
        indev = prefs[8]
        firstin = prefs[9]
        firstout = prefs[10]

        self.server.reinit(audio=audio, jackname=jackname)
        self.server.setSamplingRate(sr)
        self.server.setBufferSize(bufferSize)
        self.server.setNchnls(nchnls)
        self.server.setDuplex(duplex)
        if inchnls != None:
            self.server.setIchnls(inchnls)
        self.server.deactivateMidi()
        self.server.setOutputDevice(outdev)
        self.server.setInputOffset(firstin)
        self.server.setOutputOffset(firstout)
        if duplex:
            self.server.setInputDevice(indev)
        if reboot:
            self.server.boot()
        mixer.createMixer()
        mixerPanel.connectSliders()
        if restart:
            self.start(True)

    def getPrefs(self):
        audioOutputs = QLiveLib.getVar("availableAudioOutputs")
        audioInputs = QLiveLib.getVar("availableAudioInputs")
        outputIndexes = QLiveLib.getVar("availableAudioOutputIndexes")
        inputIndexes = QLiveLib.getVar("availableAudioInputIndexes")

        sr = int(QLiveLib.getVar("sr"))
        bufferSize = int(QLiveLib.getVar("bufferSize"))
        audio = QLiveLib.getVar("audio")
        jackname = QLiveLib.getVar("jackname")
        nchnls = QLiveLib.getVar("nchnls")
        inchnls = QLiveLib.getVar("inchnls")
        duplex = QLiveLib.getVar("duplex")
        audioOut = QLiveLib.getVar("audioOutput")
        if audioOut == "":
            outdev = -1
        else:
            outdev = outputIndexes[audioOutputs.index(audioOut)]
        audioIn = QLiveLib.getVar("audioInput")
        if audioIn == "":
            indev = -1
        else:
            indev = inputIndexes[audioInputs.index(audioIn)]
        firstin = QLiveLib.getVar("defaultFirstInput")
        firstout = QLiveLib.getVar("defaultFirstOutput")
        return (sr, bufferSize, audio, jackname, nchnls, inchnls,
                duplex, outdev, indev, firstin, firstout)

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

    def getSoundfiles(self):
        return self.soundfiles

    def createBoxObjects(self):
        tracks = QLiveLib.getVar("FxTracks").getTracks()
        for track in tracks:
            chnls = 1
            for but in track.getButtonInputs():
                name = but.name
                if not name:
                    name = "None"
                if name == "AudioIn":
                    inchnls = but.getInChannels()
                    numchnls = inchnls.count(1)
                    ismulti = but.getIsMultiChannels()
                    if ismulti:
                        chnls = max(chnls, numchnls)
                    else:
                        chnls = 1
                elif name == "Soundfile":
                    id = but.getSoundfileId()
                    if id is not None:
                        chnls = self.soundfiles[id].getChnls()
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
                category = but.category
                if not name:
                    name = "None"
                if name != "None":
                    ctrls = FX_DICT[category][name]["ctrls"]
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

    # Global recording.
    # AudioMixer should handle a per track recording.
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
        filename = os.path.join(QLiveLib.getVar("projectFolder"),
                                "bounce", filename)
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
        QLiveLib.PRINT("midirecv: ", status, data1, data2)
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