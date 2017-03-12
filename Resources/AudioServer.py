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
import time
import operator
from pyo64 import *
from constants import *
from fxbox_def import *
import QLiveLib

def prod(factors):
    return reduce(operator.mul, factors, 1)

class Automator:
    def __init__(self, init=0, inter=None):
        # Globals
        self.server = QLiveLib.getVar("AudioServer")
        self.mixer = QLiveLib.getVar("AudioMixer")
        interpTime = QLiveLib.getVar("globalInterpTime")
        self.mixmethod = -1
        # Main value
        if inter == None:
            self.param = SigTo(init, interpTime, init)
        else:
            self.param = SigTo(init, inter, init)
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
        # BPF signal chain
        self.bpfActive = 0
        self.bpfMode = 0
        self.bpfLastMode = -1
        self.bpfForward = [(0, 0.0), (512, 0.998)]
        self.bpfBackward = [(0, 1.0), (512, 0.0)]
        self.bpfBackForth = [(0, 0.0), (255,1.0), (512, 0.0)]
        self.bpfPointerTable = LinTable(self.bpfForward, size=512)
        self.bpfTable = LinTable([(0, 0.0), (512, 1.0)], size=512)
        self.bpfDur = SigTo(1, time=interpTime, init=1)
        self.bpfMin = SigTo(0, time=interpTime, init=0)
        self.bpfMax = SigTo(1, time=interpTime, init=1)

        self.bpfPhasor = TableRead(self.bpfPointerTable, freq=1.0 / self.bpfDur, loop=False)
        self.bpfPhasor.setKeepLast(True)
        self.bpfLooper = Pointer(self.bpfTable, self.bpfPhasor)
        self.bpf = Scale(self.bpfLooper, 0, 1, self.bpfMin, self.bpfMax)
        self.bpfStop()

        self.auto = Sig(0)
        self.output = Interp(self.param, self.auto, 0)

    def sig(self):
        return self.output

    def setParam(self, value=None, time=None):
        if time is not None:
            self.param.time = time
        if value is not None:
            self.param.value = value

    def checkActive(self):
        if self.envActive or self.bpfActive:
            self.output.interp = 1
        else:
            self.output.interp = 0
        self.handleMixMethod()

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
            self.envPlay()
        elif not active and self.envActive:
            self.envStop()
        self.envActive = active
        self.checkActive()
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

    def bpfPlay(self):
        self.bpfDur.play()
        self.bpfMin.play()
        self.bpfMax.play()
        #self.bpfPhasor.play()
        self.bpfLooper.play()
        self.bpf.play()

    def bpfStop(self):
        self.bpfDur.stop()
        self.bpfMin.stop()
        self.bpfMax.stop()
        self.bpfPhasor.stop()
        self.bpfLooper.stop()
        self.bpf.stop()

    def bpfHandlePlaybackMode(self, mode):
        if mode == self.bpfLastMode:
            return
        if mode < 2:
            self.bpfPointerTable.replace(self.bpfForward)
        elif mode == 2:
            self.bpfPointerTable.replace(self.bpfBackward)
        elif mode == 3:
            self.bpfPointerTable.replace(self.bpfBackForth)
        if mode == 0:
            self.bpfPhasor.setLoop(False)
        else:
            self.bpfPhasor.setLoop(True)

        self.bpfPhasor.play()
        self.bpfLastMode = mode

    def setBpfAttributes(self, dict):
        active = dict[ID_BPF_ACTIVE]
        if active and not self.bpfActive:
            self.bpfPlay()
        elif not active and self.bpfActive:
            self.bpfStop()
        self.bpfActive = active
        self.checkActive()
        self.bpfDur.time = dict[ID_BPF_DUR_INTERP]
        self.bpfDur.value = dict[ID_BPF_DUR]
        self.bpfMin.time = dict[ID_BPF_MIN_INTERP]
        self.bpfMin.value = dict[ID_BPF_MIN]
        self.bpfMax.time = dict[ID_BPF_MAX_INTERP]
        self.bpfMax.value = dict[ID_BPF_MAX]
        self.bpfTable.replace(dict[ID_BPF_FUNCTION])
        self.bpfHandlePlaybackMode(dict[ID_BPF_MODE])

    def setAttributes(self, dict):
        if dict is not None:
            mixmethod = dict.get("mixmethod", 0)
            if mixmethod != self.mixmethod:
                self.mixmethod = mixmethod
                self.handleMixMethod()
            envDict = dict.get("env", None)
            if envDict is not None:
                self.setEnvAttributes(envDict)
            bpfDict = dict.get("bpf", None)
            if bpfDict is not None:
                self.setBpfAttributes(bpfDict)

    def handleMixMethod(self):
        actives = []
        if self.mixmethod < 2:
            actives.append(self.param)
        if self.envActive:
            actives.append(self.env)
        if self.bpfActive:
            actives.append(self.bpf)

        if self.mixmethod == 0:
            self.auto.value = sum(actives)
        elif self.mixmethod == 1:
            self.auto.value = prod(actives)
        elif self.mixmethod == 2:
            self.auto.value = sum(actives)
        elif self.mixmethod == 3:
            self.auto.value = prod(actives)

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
            if "gain" in name:
                val = pow(10, val * 0.05)
            setattr(self, name, Automator(val, inter=inter))

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
        self.gainCtrls = [self.gain1, self.gain2, self.gain3, self.gain4,
                          self.gain5, self.gain6, self.gain7, self.gain8]
        self.output = Sig(self.input, mul=0.0)

    def setGains(self, inchnls):
        self.gain = [ctl.sig() for i, ctl in enumerate(self.gainCtrls) if inchnls[i]]
        self.output.mul = self.gain

    def setEnable(self, x):
        self.output.value = [[0.0] * self.chnls, self.input][x]

class SoundfileIn(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.output = Sig(self.input, mul=self.gain.sig())

    def setEnable(self, x):
        self.output.value = [[0.0] * self.chnls, self.input][x]

class FxLowpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquad(self.input, freq=self.freq.sig(), q=self.Q.sig(),
                             mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxHighpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquad(self.input, freq=self.freq.sig(), q=self.Q.sig(), type=1,
                             mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxBandpass(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquadx(self.input, freq=self.freq.sig(), q=self.Q.sig(), type=2,
                              stages=2, mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxBandstop(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = Biquadx(self.input, freq=self.freq.sig(), q=self.Q.sig(), type=3,
                              stages=2, mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxPeakNotch(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = EQ(self.input, freq=self.freq.sig(), q=self.Q.sig(),
                         boost=self.boost.sig(), type=0, mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxLowshelf(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = EQ(self.input, freq=self.freq.sig(), q=self.Q.sig(),
                         boost=self.boost.sig(), type=1, mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxHighshelf(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = EQ(self.input, freq=self.freq.sig(), q=self.Q.sig(),
                         boost=self.boost.sig(), type=2, mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxLPRes24(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = MoogLP(self.input, freq=self.freq.sig(),
                             res=self.res.sig(), mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxStateVar(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.filter = SVF(self.input, freq=self.freq.sig(), q=self.Q.sig(),
                         type=self.type.sig(), mul=self.gain.sig())
        self.process = Interp(self.input, self.filter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxDCBlock(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = DCBlock(self.input, mul=self.gain.sig())
        self.output = Sig(self.process)

class FxFreeverb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = Freeverb(self.input, self.size.sig(), self.damp.sig(), 1,
                               mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxWGverb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = WGVerb(self.input, self.feed.sig(), self.cutoff.sig(),
                             bal=1.0, mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxResonator(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = Waveguide(self.input, self.freq.sig(), self.dur.sig(),
                                mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxConReson(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = AllpassWG(self.input, self.freq.sig(), self.feed.sig(),
                                detune=self.detune.sig(), mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxComplexRes(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = ComplexRes(self.input, self.freq.sig(), self.decay.sig(),
                                 mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxStereoVerb(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.reverb = STRev(self.input, self.pan.sig(), self.revtime.sig(),
                            self.cutoff.sig(), 1, mul=self.gain.sig())
        self.process = Interp(self.input, self.reverb, self.dryWet.sig())
        self.output = Sig(self.process)

class FxDelay(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.delay = Delay(self.input, self.deltime.sig(), self.feed.sig(), 5,
                           mul=self.gain.sig())
        self.process = Interp(self.input, self.delay, self.dryWet.sig())
        self.output = Sig(self.process)

class FxSmoothDelay(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.delay = SmoothDelay(self.input, self.deltime.sig(), self.feed.sig(),
                                 crossfade=0.005, maxdelay=5, mul=self.gain.sig())
        self.process = Interp(self.input, self.delay, self.dryWet.sig())
        self.output = Sig(self.process)

class FxFlanger(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.seconds = Sig(self.center.sig(), mul=0.001)
        self.lfo = Sine(self.lfofreq.sig(), mul=self.seconds*self.depth.sig(),
                        add=self.seconds)
        self.delay = Delay(self.input, self.lfo, self.feed.sig(), 0.1,
                           mul=self.gain.sig(), add=self.input)
        self.process = Interp(self.input, self.delay, self.dryWet.sig())
        self.output = Sig(self.process)

class FxPhaser(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.lfo = Sine(self.lfofreq.sig(), mul=0.5, add=0.5)
        self.phs = Phaser(self.input, self.freq.sig(), self.lfo*self.spread.sig()+1,
                          self.Q.sig(), self.feed.sig(), 12, mul=self.gain.sig())
        self.process = Interp(self.input, self.phs, self.dryWet.sig())
        self.output = Sig(self.process)

class FxDisto(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.disto = Disto(self.input, self.drive.sig(), self.slope.sig(),
                           mul=self.gain.sig())
        self.process = Interp(self.input, self.disto, self.dryWet.sig())
        self.output = Sig(self.process)

class FxDegrade(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.disto = Degrade(self.input, self.bits.sig(), self.srscale.sig(),
                             mul=self.gain.sig())
        self.process = Interp(self.input, self.disto, self.dryWet.sig())
        self.output = Sig(self.process)

class FxClipper(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.thresh = Scale(self.drive.sig(), 0, 1, 1, 0.001, 0.2)
        self.disto = Clip(self.input, -self.thresh, self.thresh,
                          mul=1.0/self.thresh)
        self.lp = ButLP(self.disto, freq=self.cutoff.sig(), mul=self.gain.sig())
        self.process = Interp(self.input, self.lp, self.dryWet.sig())
        self.output = Sig(self.process)

class FxRectifier(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.disto = self.input + (Abs(self.input) - self.input) * self.amount.sig()
        self.process = Interp(self.input, self.disto, self.dryWet.sig())
        self.output = Sig(self.process)

class FxCompressor(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.comp = Compress(self.input, self.thresh.sig(), self.ratio.sig(), self.attack.sig(),
                             self.decay.sig(), 5, knee=0.5, mul=self.gain.sig())
        self.process = Interp(self.input, self.comp, self.dryWet.sig())
        self.output = Sig(self.process)

class FxFreqShift(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.shifter = FreqShift(self.input, self.shift.sig(), mul=self.gain.sig())
        self.process = Interp(self.input, self.shifter, self.dryWet.sig())
        self.output = Sig(self.process)

class FxHarmonizer(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.harmon = Harmonizer(self.input, self.transpo.sig(), self.feed.sig(),
                                 mul=self.gain.sig())
        self.process = Interp(self.input, self.harmon, self.dryWet.sig())
        self.output = Sig(self.process)

class FxPanning(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.chnls *= 2
        self.process = Pan(self.input, self.chnls, self.pan.sig(), self.spread.sig(),
                           mul=self.gain.sig())
        self.output = Sig(self.process)

class FxAudioOut(BaseAudioObject):
    def __init__(self, chnls, ctrls, values, interps):
        BaseAudioObject.__init__(self, chnls, ctrls, values, interps)
        self.process = self.input
        self.gainCtrls = [self.gain1, self.gain2, self.gain3, self.gain4,
                          self.gain5, self.gain6, self.gain7, self.gain8]
        self.output = Sig(self.process, mul=0.0)

    def setGains(self, outchnls):
        self.gain = [ctl.sig() for i, ctl in enumerate(self.gainCtrls) if outchnls[i]]
        self.output.mul = self.gain

AUDIO_OBJECTS = {"None": AudioNone, "AudioIn": AudioIn,
                 "Soundfile": SoundfileIn, "Lowpass": FxLowpass,
                "Highpass": FxHighpass, "Bandpass": FxBandpass,
                "Bandstop": FxBandstop, "PeakNotch": FxPeakNotch,
                "Lowshelf": FxLowshelf, "Highshelf": FxHighshelf,
                "LPRes24": FxLPRes24, "StateVar": FxStateVar,
                "DCBlock": FxDCBlock,
                "Freeverb": FxFreeverb, "WGverb": FxWGverb,
                "StereoVerb": FxStereoVerb, "Resonator": FxResonator,
                "ConReson": FxConReson, "ComplexRes": FxComplexRes,
                "Delay": FxDelay, "SmoothDelay": FxSmoothDelay,
                "Flanger": FxFlanger, "Phaser": FxPhaser,
                "Disto": FxDisto, "Degrade": FxDegrade, "Clipper": FxClipper,
                "Rectifier": FxRectifier,
                "Compressor": FxCompressor,
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
            trackchnls = 1
            for but in track.getButtonInputs():
                chnls = 1
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
                    if name == "AudioIn":
                        obj.setGains(inchnls)
                trackchnls = max(trackchnls, chnls)
            for but in track.getButtonFxs():
                name = but.name
                category = but.category
                if not name:
                    name = "None"
                if name != "None":
                    ctrls = FX_DICT[category][name]["ctrls"]
                    values = but.getCurrentValues()
                    if values is not None:
                        obj = AUDIO_OBJECTS[name](trackchnls, ctrls, values,
                                                  but.getCurrentInterps())
                        but.setAudioRef(obj)
                        self.audioObjects.append(obj)
                        if name == "AudioOut":
                            obj.setGains(but.getOutChannels())
                        # TODO: we will need a better algorithm for spatialization.
                        if name in ["Panning", "StereoVerb"]:
                            trackchnls *= 2

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
