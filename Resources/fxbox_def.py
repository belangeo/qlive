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
from constants import *

####### BOX PROCESS DEFINITIONS ######

# init parameters: name, init, min, max, unit, log (unit not used yet)

# Recurrent parameter definitions
GAIN_DEF = ["gain", 0, -60, 18, "dB", False]
DRYWET_DEF = ["dryWet", 1, 0, 1, "", False]
FREQ_DEF = ["freq", 1000, 20, 20000, "Hz", True]
Q_DEF = ["Q", 1, 0.5, 50, "", False]
BOOST_DEF = ["boost", 0, -24, 24, "dB", False]
FEED_DEF = ["feed", 0, 0, 1, "", False]

# Effects Defintiions
FX_DICT = {
    "Filter effects": {
        "Lowpass": {"ctrls": [FREQ_DEF,
                              Q_DEF,
                              GAIN_DEF,
                              DRYWET_DEF]},
        "Highpass": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "Bandpass": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "Bandstop": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "PeakNotch": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               BOOST_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "Lowshelf": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               BOOST_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "Highshelf": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               BOOST_DEF,
                               GAIN_DEF,
                               DRYWET_DEF]},
        "LPRes24": {"ctrls": [FREQ_DEF,
                             ["res", 0.25, 0, 1, "", False],
                             GAIN_DEF,
                             DRYWET_DEF]},
        "StateVar": {"ctrls": [FREQ_DEF,
                               Q_DEF,
                               ["type", 0, 0, 1, "", False],
                               GAIN_DEF,
                               DRYWET_DEF]},
        "DCBlock": {"ctrls": [GAIN_DEF]},
    },

    "Reverb effects": {
        "Freeverb": {"ctrls": [["size", 0.5, 0, 1, "", False],
                               ["damp", 0.5, 0, 1, "", False],
                               GAIN_DEF,
                               DRYWET_DEF]},
        "WGverb": {"ctrls": [["feed", 0.5, 0, 1, "", False],
                             ["cutoff", 5000, 20, 15000, "Hz", True],
                             GAIN_DEF,
                             DRYWET_DEF]},
        "StereoVerb": {"ctrls": [["pan", 0.5, 0, 1, "", False],
                                 ["revtime", 1.5, 0.1, 30, "Sec", True],
                                 ["cutoff", 5000, 100, 15000, "Hz", True],
                                 GAIN_DEF,
                                 DRYWET_DEF]},
        "Resonator": {"ctrls": [["freq", 100, 20, 1000, "Hz", True],
                                ["dur", 20, 0.1, 60, "Sec", True],
                                GAIN_DEF,
                                DRYWET_DEF]},
        "ConReson": {"ctrls": [["freq", 100, 20, 1000, "Hz", True],
                               ["feed", 0.75, 0, 1, "", False],
                               ["detune", 0.5, 0, 1, "", False],
                               GAIN_DEF,
                               DRYWET_DEF]},
        "ComplexRes": {"ctrls": [["freq", 100, 20, 10000, "Hz", True],
                                 ["decay", 0.5, 0.001, 5, "Sec", True],
                                 GAIN_DEF,
                                 DRYWET_DEF]},
    },

    "Delay effects": {
        "Delay": {"ctrls": [["deltime", 1, 0, 5, "", False],
                            FEED_DEF,
                            GAIN_DEF,
                            DRYWET_DEF]},
        "SmoothDelay": {"ctrls": [["deltime", 1, 0.001, 5, "", False],
                                  FEED_DEF,
                                  GAIN_DEF,
                                  DRYWET_DEF]},
        "Flanger": {"ctrls": [["center", 5, 0.01, 30, "ms", False],
                              ["lfofreq", 0.1, 0.001, 20, "Hz", True],
                              ["depth", 0.75, 0, 1, "", False],
                              FEED_DEF,
                              GAIN_DEF,
                              DRYWET_DEF]},
        "Phaser": {"ctrls": [["freq", 100, 40, 2000, "Hz", True],
                             ["spread", .5, 0, 2, "", False],
                             ["lfofreq", 0.1, 0.001, 20, "Hz", True],
                             ["Q", 0.5, 0, 1, "", False],
                             ["feed", 0.5, 0, 1, "", False],
                             GAIN_DEF,
                             DRYWET_DEF]}
    },

    "Distortion effects": { # Degrade, Clipper
        "Disto": {"ctrls": [["drive", 0.75, 0, 1, "", False],
                            ["slope", 0.75, 0, 1, "", False],
                            GAIN_DEF,
                            DRYWET_DEF]}
    },

    "Dynamic processors": { # Gate
        "Compressor": {"ctrls":[["thresh", -10, -60, 0, "dB", False],
                                ["ratio", 2, 1, 50, "x", True],
                                ["attack", 0.01, 0.001, 0.5, "sec", False],
                                ["decay", 0.1, 0.001, 1, "sec", False],
                                GAIN_DEF,
                                DRYWET_DEF]}
    },

    "Frequency/Pitch effects": { # Chorus
        "FreqShift": {"ctrls": [["shift", 0, -5000, 5000, "Hz", False],
                                GAIN_DEF,
                                DRYWET_DEF]},
        "Harmonizer": {"ctrls": [["transpo", 0, -24, 24, "half", False],
                                 FEED_DEF,
                                 GAIN_DEF,
                                 DRYWET_DEF]}
    },

    "Spatial effects": {
        "Panning": {"ctrls": [["pan", 0.5, 0, 1, "", False],
                              ["spread", 0.5, 0, 1, "", False],
                              GAIN_DEF]}
    },

    "Others": { # BusIn, BusOut, Denorm
        "None": {"ctrls": []},
        "AudioOut": {"ctrls":[["gain1", 0, -60, 18, "dB", False],
                              ["gain2", 0, -60, 18, "dB", False],
                              ["gain3", 0, -60, 18, "dB", False],
                              ["gain4", 0, -60, 18, "dB", False],
                              ["gain5", 0, -60, 18, "dB", False],
                              ["gain6", 0, -60, 18, "dB", False],
                              ["gain7", 0, -60, 18, "dB", False],
                              ["gain8", 0, -60, 18, "dB", False]],
                     "outselect": [str(x+1) for x in range(NUM_OUTPUTS)]}
    }
}

# Categories/Effects ordered names. Index 0 of each list is the category.
# Not using dicts to make dynamic submenu generation easier.
# Use the names as in FX_DICT.
FX_LIST = [ ["Delay effects", "Delay", "SmoothDelay", "Flanger", "Phaser"],
            ["Reverb effects", "Freeverb", "WGverb", "StereoVerb", "Resonator",
             "ConReson", "ComplexRes"],
            ["Filter effects", "Lowpass", "Highpass", "Bandpass", "Bandstop",
             "PeakNotch", "Lowshelf", "Highshelf", "LPRes24", "StateVar",
             "DCBlock"],
            ["Distortion effects", "Disto"],
            ["Dynamic processors", "Compressor"],
            ["Frequency/Pitch effects", "FreqShift", "Harmonizer"],
            ["Spatial effects", "Panning"],
            ["Others", "None", "AudioOut"]
          ]

# Input defintions
INPUT_DICT = {  "None":     {"ctrls":   []},
                "AudioIn":  {"ctrls":   [["gain1", 0, -60, 18, "dB", False],
                                         ["gain2", 0, -60, 18, "dB", False],
                                         ["gain3", 0, -60, 18, "dB", False],
                                         ["gain4", 0, -60, 18, "dB", False],
                                         ["gain5", 0, -60, 18, "dB", False],
                                         ["gain6", 0, -60, 18, "dB", False],
                                         ["gain7", 0, -60, 18, "dB", False],
                                         ["gain8", 0, -60, 18, "dB", False]],
                             "inselect": [str(x+1) for x in range(NUM_INPUTS)]},
                "Soundfile": {"ctrls":   [GAIN_DEF],
                              "select": None},
             }

# Input ordered names
INPUT_LIST = ["None", "AudioIn", "Soundfile"]