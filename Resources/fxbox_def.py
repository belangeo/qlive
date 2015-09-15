from constants import *

####### BOX PROCESS DEFINITIONS ######

# init parameters: name, init, min, max, unit, log (unit not used yet)

# Recurrent parameter definitions
GAIN_DEF = ["gain", 0, -60, 18, "dB", False]
DRYWET_DEF = ["dryWet", 1, 0, 1, "", False]
FREQ_DEF = ["freq", 1000, 20, 20000, "Hz", True]
Q_DEF = ["Q", 1, 0.5, 50, "", False]
FEED_DEF = ["feed", 0, 0, 1, "", False]

# Effects Defintiions
FX_DICT = { "None": {"ctrls": []},
            "Lowpass":  {"ctrls":   [   FREQ_DEF,
                                        Q_DEF,
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Highpass": {"ctrls":   [   FREQ_DEF,
                                        Q_DEF,
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Bandpass": {"ctrls":   [   FREQ_DEF,
                                        Q_DEF,
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Freeverb": {"ctrls":   [   ["size", 0.5, 0, 1, "", False],
                                        ["damp", 0.5, 0, 1, "", False],
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "StereoVerb": {"ctrls": [   ["pan", 0.5, 0, 1, "", False],
                                        ["revtime", 1.5, 0.1, 30, "Sec", True],
                                        ["cutoff", 5000, 100, 15000, "Hz", True],
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Disto": {"ctrls":   [      ["drive", 0.75, 0, 1, "", False],
                                        ["slope", 0.75, 0, 1, "", False],
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Delay": {"ctrls":   [      ["deltime", 1, 0, 5, "", False],
                                        FEED_DEF,
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Compressor": {"ctrls":   [ ["thresh", -10, -60, 0, "dB", False],
                                        ["ratio", 2, 1, 50, "x", True],
                                        ["attack", 0.01, 0.001, 0.5, "sec", False],
                                        ["attack", 0.1, 0.001, 1, "sec", False],
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "FreqShift": {"ctrls":   [  ["shift", 0, -5000, 5000, "Hz", False],
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Harmonizer": {"ctrls":   [ ["transpo", 0, -24, 24, "half", False],
                                        FEED_DEF,
                                        GAIN_DEF,
                                        DRYWET_DEF
                                    ]
                        },
            "Panning": {"ctrls":   [ ["pan", 0.5, 0, 1, "", False],
                                     ["spread", 0.5, 0, 1, "", False],
                                     GAIN_DEF
                                   ]
                        },
            "AudioOut": {   "ctrls":    [   GAIN_DEF
                                        ],
                            "outselect": [str(x+1) for x in range(NUM_OUTPUTS)],
                        },
          }

# Effects ordered names
FX_LIST = ["None", "Lowpass", "Highpass", "Bandpass", "Freeverb", "StereoVerb", "Disto",
           "Delay", "Compressor", "FreqShift", "Harmonizer", "Panning", "AudioOut"]

# Input defintions
INPUT_DICT = {  "None":     {"ctrls":   []},
                "AudioIn":  {"ctrls":   [GAIN_DEF],
                             "inselect": [str(x+1) for x in range(NUM_INPUTS)]},
             }

# Input ordered names
INPUT_LIST = ["None", "AudioIn"]
