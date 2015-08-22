from constants import *

QLiveVariables = dict()

QLiveVariables["currentProject"] = ""
QLiveVariables["projectFolder"] = ""
QLiveVariables["MainWindow"] = None
QLiveVariables["ControlPanel"] = None
QLiveVariables["CuesPanel"] = None
QLiveVariables["FxTracks"] = None
QLiveVariables["AudioMixer"] = None
QLiveVariables["AudioServer"] = None
QLiveVariables["MixerPanel"] = None
QLiveVariables["Soundfiles"] = None
QLiveVariables["FxViews"] = []
QLiveVariables["CanProcessCueKeys"] = True

PREFS_TO_SAVE = {"useTooltips": False}

#TODO: check app version and add missing prefs in the current prefs file
def readQLivePrefsFromFile():
    if not os.path.isfile(PREFERENCES_PATH):
        with open(PREFERENCES_PATH, "w") as f:
            f.write(str(PREFS_TO_SAVE))
            prefs = PREFS_TO_SAVE
    else:
        with open(PREFERENCES_PATH, "r") as f:
            prefs = eval(f.read())

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
