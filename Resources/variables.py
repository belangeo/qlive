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
import copy
from constants import *

QLiveVariables = dict()

QLiveVariables["currentProject"] = ""
QLiveVariables["projectFolder"] = ""
QLiveVariables["MainWindow"] = None
QLiveVariables["ControlPanel"] = None
QLiveVariables["CuesPanel"] = None
QLiveVariables["CurrentCueWindow"] = None
QLiveVariables["FxTracks"] = None
QLiveVariables["AudioMixer"] = None
QLiveVariables["AudioServer"] = None
QLiveVariables["MidiServer"] = None
QLiveVariables["MixerPanel"] = None
QLiveVariables["Soundfiles"] = None
QLiveVariables["FxViews"] = []
QLiveVariables["CanProcessCueKeys"] = True
QLiveVariables["MidiLearnMode"] = False

# Audio / Midi
QLiveVariables['availableAudioOutputs'] = []
QLiveVariables['availableAudioOutputIndexes'] = []
QLiveVariables['availableAudioInputs'] = []
QLiveVariables['availableAudioInputIndexes'] = []
QLiveVariables['availableMidiOutputs'] = []
QLiveVariables['availableMidiOutputIndexes'] = []
QLiveVariables['availableMidiInputs'] = []
QLiveVariables['availableMidiInputIndexes'] = []

# Declare here QLiveVariables which will be loaded/saved in prefs file:
PREFS_TO_SAVE = {"useTooltips": False,
                 "audio":       "portaudio",
                 "sr":          "44100",
                 "duplex":      1,
                 "nchnls":      NUM_CHNLS,
                 "inchnls":     None,
                 "jackname":    "qlive",
                 "bufferSize":  "64",
                 "audioOutput": "",
                 "audioInput": "",
                 "defaultFirstInput": 0,
                 "defaultFirstOutput": 0,
                 "globalInterpTime": 0.01
                }

def readQLivePrefsFromFile():
    if not os.path.isfile(PREFERENCES_PATH):
        with open(PREFERENCES_PATH, "w") as f:
            f.write(str(PREFS_TO_SAVE))
        prefs = copy.deepcopy(PREFS_TO_SAVE)
    else:
        with open(PREFERENCES_PATH, "r") as f:
            prefs = eval(f.read())
            # Load prefs which are not in the prefs file
            for p in PREFS_TO_SAVE:
                if p not in prefs:
                    prefs[p] = PREFS_TO_SAVE[p]

    QLiveVariables.update(prefs)

def writeQLivePrefsToFile():
    try:
        file = open(PREFERENCES_PATH,"wt")
    except IOError:
        print("Unable to open the preferences file.\n")
        return

    save_tmp = {}
    for key in QLiveVariables:
        if key in PREFS_TO_SAVE:
            save_tmp[key] = QLiveVariables[key]

    with open(PREFERENCES_PATH, "w") as f:
        f.write(str(save_tmp))

    file.close()