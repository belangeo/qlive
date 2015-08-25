#!/usr/bin/python
# encoding: utf-8
from pyo64 import *
from constants import *

class AudioChannel:
    def __init__(self, input=0):
        self.input = Sig(input)
        self.gain = SigTo(1, init=1)
        self.output = Sig(self.input, mul=self.gain)
        self.ampOut = PeakAmp(self.output)

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
        self.inChannels = [AudioChannel(Input(i)) for i in range(NUM_INPUTS)] 
        self.mixer = Mixer(outs=NUM_OUTPUTS, chnls=1)       
        self.outChannels = [AudioChannel(
                            self.mixer[i]).out(i) for i in range(NUM_OUTPUTS)]

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

    def addToMixer(self, voice, sig):
        mixerInputId = len(self.mixer.getKeys())
        self.mixer.addInput(mixerInputId, sig)
        self.mixer.setAmp(mixerInputId, voice, 1)
        return mixerInputId

    def delFromMixer(self, id):
        self.mixer.delInput(id)

    def resetMixer(self):
        for key in self.mixer.getKeys():
            self.mixer.delInput(key)
        self.mixerInputCount = 0
