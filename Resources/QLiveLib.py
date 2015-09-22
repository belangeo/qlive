from constants import *
import variables as vars
from pyo import pa_get_input_devices, pa_get_default_input, pa_get_output_devices, pa_get_default_output, pm_get_input_devices, pm_get_default_input

def getAvailableAudioMidiDrivers():
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

# getter/setter for global variables defined at runtime (see variables.py)
def getVar(var, default=None):
    return vars.QLiveVariables.get(var, default)

def setVar(var, value):
    vars.QLiveVariables[var] = value

def saveVars():
    vars.writeQLivePrefsToFile()

def loadVars():
    vars.readQLivePrefsFromFile()

def queryAudioMidiDrivers():
    inputs, inputIndexes, defaultInput, outputs, outputIndexes, defaultOutput, midiInputs, midiInputIndexes, defaultMidiInput = getAvailableAudioMidiDrivers()
    setVar("availableAudioOutputs",  outputs)
    setVar("availableAudioOutputIndexes",  outputIndexes)
    if getVar("audioOutput") not in outputs:
        setVar("audioOutput", defaultOutput)

    setVar("availableAudioInputs", inputs)
    setVar("availableAudioInputIndexes", inputIndexes)
    if getVar("audioInput") not in inputs:
        setVar("audioInput", defaultInput)

    if midiInputs == []:
        setVar("useMidi", 0)
    else:
        setVar("useMidi", 1)
    setVar("availableMidiInputs", midiInputs)
    setVar("availableMidiInputIndexes", midiInputIndexes)
    if getVar("midiDeviceIn") not in midiInputs:
        setVar("midiDeviceIn", defaultMidiInput)

# PRINT should be used instead of print function to enable/disable printing.
def PRINT(*args):
    if DEBUG:
        for arg in args:
            print arg,
        print

def ensureNFD(unistr):
    "Converts a string to unicode."
    if unistr == None:
        return None
    if PLATFORM in ['linux2', 'win32']:
        encodings = [DEFAULT_ENCODING, SYSTEM_ENCODING,
                     'cp1252', 'iso-8859-1', 'utf-16']
        format = 'NFC'
    else:
        encodings = [DEFAULT_ENCODING, SYSTEM_ENCODING,
                     'macroman', 'iso-8859-1', 'utf-16']
        format = 'NFC'
    decstr = unistr
    if type(decstr) != UnicodeType:
        for encoding in encodings:
            try:
                decstr = decstr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
            except:
                decstr = "UnableToDecodeString"
                print "Unicode encoding not in a recognized format..."
                break
    if decstr == "UnableToDecodeString":
        return unistr
    else:
        return unicodedata.normalize(format, decstr)

def toSysEncoding(unistr):
    "Converts a unicode string to the current system encoding."
    try:
        if PLATFORM == "win32":
            unistr = unistr.encode(SYSTEM_ENCODING)
        else:
            unistr = unicode(unistr)
    except:
        pass
    return unistr
