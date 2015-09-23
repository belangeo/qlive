#!/usr/bin/python
# encoding: utf-8
from pyo64 import *
from constants import *

class AudioChannel:
    def __init__(self, input=0):
        self.input = Sig(input)
        self.gain = SigTo(1, time=0.001, init=1, mul=0)
        self.output = Sig(self.input, mul=self.gain)
        self.ampOut = PeakAmp(self.output)

    def mute(self, muted):
        if muted:
            self.gain.mul = 0
        else:
            self.gain.mul = 1
            
    def setInput(self, input):
        self.input.setValue(input)
        
    def out(self, chnl=0):
        self.output.out(chnl)
        return self

    def getOutput(self):
        return self.output
        
    def setVolume(self, value):
        self.gain.setValue(value)
        
    def setAmpCallback(self, call):
        self.ampOut.function = call

class AudioMixer:
    def __init__(self):
        self.muted = True
        self.mixerInputCount = 0
        self.inChannels = [AudioChannel(Input(i)) for i in range(NUM_INPUTS)] 
        self.mixer = Mixer(outs=NUM_OUTPUTS, chnls=1)       
        self.outChannels = [AudioChannel(
                            self.mixer[i]).out(i) for i in range(NUM_OUTPUTS)]

    def getInputChannels(self):
        return self.inChannels

    def getInputChannel(self, index):
        if index < len(self.inChannels):
            return self.inChannels[index]
        else:
            return None

    def getOutputChannel(self, index):
        if index < len(self.outChannels):
            return self.outChannels[index]
        else:
            return None

    def cueEvent(self, evt):
        mute = self.muted
        if evt.getCurrent() == 0 and not self.muted:
            mute = True
        elif evt.getCurrent() > 0 and self.muted:
            mute = False
        if mute != self.muted:
            self.muted = mute
            for inChannel in self.inChannels:
                inChannel.mute(self.muted)
            for outChannel in self.outChannels:
                outChannel.mute(self.muted)

    def addToMixer(self, voice, sig):
        mixerInputId = self.mixerInputCount
        self.mixerInputCount += 1
        self.mixer.addInput(mixerInputId, sig)
        self.mixer.setAmp(mixerInputId, voice, 1)
        return mixerInputId

    def delFromMixer(self, id):
        self.mixer.delInput(id)

    def resetMixer(self):
        for key in self.mixer.getKeys():
            self.mixer.delInput(key)
        self.mixerInputCount = 0
