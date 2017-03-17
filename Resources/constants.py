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
import os, sys, unicodedata, copy
from pyolib._wxwidgets import BACKGROUND_COLOUR

reload(sys)
sys.setdefaultencoding("utf-8")

QLIVE_MAGIC_LINE = "### QLIVE PROJECT FILE ###\n"
APP_NAME = "QLive"
APP_VERSION = "0.1.4"
APP_COPYRIGHT = 'litem.umontreal.ca,  2016'
FILE_EXTENSION = "qlp"

DEFAULT_ENCODING = sys.getdefaultencoding()
SYSTEM_ENCODING = sys.getfilesystemencoding()

PLATFORM = sys.platform

if '/%s.app' % APP_NAME in os.getcwd():
    RESOURCES_PATH = os.getcwd()
else:
    RESOURCES_PATH = os.path.join(os.getcwd(), 'Resources')

if not os.path.isdir(RESOURCES_PATH) and PLATFORM == "win32":
    RESOURCES_PATH = os.path.join(os.getenv("ProgramFiles"), "QLive",
                                  "Resources")

IMAGES_PATH = os.path.join(RESOURCES_PATH, "images")

TEMP_PATH = os.path.join(os.path.expanduser('~'), '.qlive')
if not os.path.isdir(TEMP_PATH):
    os.mkdir(TEMP_PATH)

OPEN_RECENT_PATH = os.path.join(TEMP_PATH, "open_recents.txt")
if not os.path.isfile(OPEN_RECENT_PATH):
    with open(OPEN_RECENT_PATH, "w") as f:
        pass

PREFERENCES_PATH = os.path.join(TEMP_PATH, "qlive-prefs.py")

SOUNDS_PATH = os.path.join(RESOURCES_PATH, "sounds")
NEW_FILE_PATH = os.path.join(RESOURCES_PATH, "qlive_new_file.qlp")

DEBUG = False

NUM_INPUTS = 8
NUM_OUTPUTS = 8

INTERPTIME_MIN = 0.01
INTERPTIME_MAX = 600

BOX_MENU_ITEM_FIRST_ID = 1000
EXPORT_MEI_ID = 1500
EXPORT_PDF_ID = 1600
NEW_TRACK_ID = 2600
DELETE_TRACK_ID = 2601
PLAY_MODE_ID = 2700
MIDI_LEARN_ID = 2800
INTERP_TIME_ID = 2900
VIEW_CUE_WINDOW_ID = 3000
LINK_STEREO_ID = 4000
KEY_EVENT_FIRST_ID = 10000 # keep at least 100 ids from this one
AUTOMATION_PANEL_FIRST_ID = 10100 # keep at least 15 ids from this one


# Cue IDs
CUE_TYPE_SELECT = 0
CUE_TYPE_NEW = 1
CUE_TYPE_DELETE = 2
CUE_TYPE_SAVE = 3
CUE_TYPE_COPY = 4
CUE_TYPE_PASTE = 5

CUE_CUT_ID = 500
CUE_COPY_ID = 501
CUE_PASTE_ID = 502

# SoundFiles IDs and constants
ID_COL_FILENAME = 0
ID_COL_PLAYING = 1
ID_COL_LOOPMODE = 2
ID_COL_TRANSPO = 3
ID_COL_GAIN = 4
ID_COL_DIRECTOUT = 5
ID_COL_STARTPOINT = 6
ID_COL_ENDPOINT = 7
ID_COL_CROSSFADE = 8
ID_COL_CHANNEL = 9
ID_COL_TRANSPOX = 10
ID_COL_GAINX = 11
ID_TRANSPO_AUTO = 12
ID_GAIN_AUTO = 13

LABELS = ["Filename", "Playing", "Loop Mode", "Transpo", "Gain (dB)",
          "Output", "Start Sec", "End Sec", "Xfade (%)", "Out Chan"]
COLSIZES = [150, 70, 100, 70, 70, 70, 80, 80, 80, 80]
LOOPMODES = ["No Loop", "Forward", "Backward", "Back-and-Forth"]
PLAYING = ["Stop", "Play", "Through"]

# Automation IDs and constants
ID_AUTO_MIX_METHOD = 0

ID_ENV_ACTIVE = 1
ID_ENV_INPUTS = 2
ID_ENV_INPUTS_INTERP = 3
ID_ENV_THRESHOLD = 4
ID_ENV_THRESHOLD_INTERP = 5
ID_ENV_CUTOFF = 6
ID_ENV_CUTOFF_INTERP = 7
ID_ENV_MIN = 8
ID_ENV_MIN_INTERP = 9
ID_ENV_MAX = 10
ID_ENV_MAX_INTERP = 11

ID_BPF_ACTIVE = 0
ID_BPF_DUR_INTERP = 1
ID_BPF_DUR = 2
ID_BPF_MIN = 3
ID_BPF_MIN_INTERP = 4
ID_BPF_MAX = 5
ID_BPF_MAX_INTERP = 6
ID_BPF_FUNCTION = 7
ID_BPF_MODE = 8

# GUI Constants
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 25
TRACK_COL_SIZE = 90
TRACK_ROW_SIZE = 35
SELECTION_LINE_POS = 25
INPUTS_LINE_POS = 115
MAX_WIDTH = 3000
MAX_HEIGHT = 1000

# Audio drivers
if PLATFORM == 'darwin' and '/%s.app' % APP_NAME in os.getcwd():
    AUDIO_DRIVERS = ['portaudio']
elif PLATFORM == 'darwin':
    AUDIO_DRIVERS = ['coreaudio', 'portaudio', 'jack']
elif PLATFORM == 'win32':
    AUDIO_DRIVERS = ['portaudio']
else:
    AUDIO_DRIVERS = ['portaudio', 'jack']

# MIDI drivers
MIDI_DRIVERS = ['portmidi']

# Audio settings
SAMPLE_RATES = ['22050','44100','48000', '88200', '96000']
BUFFER_SIZES = ['64','128','256','512','1024','2048','4096','8192','16384']
ALLOWED_EXTENSIONS = ["wav","wave","aif","aiff","aifc","au","",
                      "sd2","flac","caf","ogg"]
EXPORT_FORMATS = ['WAV', 'AIFF', 'AU', 'RAW', 'SD2', 'FLAC', 'CAF', 'OGG']
EXPORT_TYPES = ['16 int', '24 int', '32 int', '32 float', '64 float']
RECORD_EXTENSIONS = [".wav",".aif",".au","",".sd2",".flac",".caf",".ogg"]
AUDIO_FILE_WILDCARD =  "All files|*.*|" \
                   "Wave file|*.wave;*.WAV;*.WAVE;*.Wav;*.Wave;*.wav|" \
                   "AIFF file|*.aif;*.aiff;*.aifc;*.AIF;*.AIFF;*.Aif;*.Aiff|" \
                   "Flac file|*.flac;*.FLAC;*.Flac;|" \
                   "OGG file|*.ogg;*.OGG;*.Ogg;|" \
                   "SD2 file|*.sd2;*.SD2;*.Sd2;|" \
                   "AU file|*.au;*.AU;*.Au;|" \
                   "CAF file|*.caf;*.CAF;*.Caf"

# Fonts
if sys.platform in ['linux2', 'win32']:
    CONTROLSLIDER_FONT = 7
else:
    CONTROLSLIDER_FONT = 10

# Icons
ICON_PLAY = os.path.join(IMAGES_PATH, "play-icon.png")
ICON_PLAY_PRESSED = os.path.join(IMAGES_PATH, "stop-icon.png")
ICON_RECORD = os.path.join(IMAGES_PATH, "record-icon.png")
ICON_RECORD_PRESSED = os.path.join(IMAGES_PATH, "record-pressed-icon.png")
ICON_ADD = os.path.join(IMAGES_PATH, "add-icon.png")
ICON_DELETE = os.path.join(IMAGES_PATH, "delete-icon.png")
ICON_ARROW_UP = os.path.join(IMAGES_PATH, "arrow-up-icon.png")
ICON_ARROW_DOWN = os.path.join(IMAGES_PATH, "arrow-down-icon.png")
ICON_ARROW_UP_MIDI = os.path.join(IMAGES_PATH, "arrow-up-midi-icon.png")
ICON_ARROW_DOWN_MIDI = os.path.join(IMAGES_PATH, "arrow-down-midi-icon.png")

# Colours
BACKGROUND_COLOUR = BACKGROUND_COLOUR
BACKGROUND_COLOUR_LOCKED = "#C2C2C2"
MIDILEARN_COLOUR = "#CCBBBB"
CUEBUTTON_UNSELECTED_COLOUR = "#DDDDDD"
CUEBUTTON_SELECTED_COLOUR = "#5555FF"
CUEBUTTON_0_SELECTED_COLOUR = "#FF3344"
CONTROLSLIDER_KNOB_COLOUR = '#DDDDDD'
CONTROLSLIDER_DISABLE_KNOB_COLOUR = '#ABABAB'
CONTROLSLIDER_BACK_COLOUR = '#BBB9BC'
CONTROLSLIDER_BACK_COLOUR_INTERP = '#CCCACD'
CONTROLSLIDER_DISABLE_BACK_COLOUR = '#777777'
CONTROLSLIDER_SELECTED_COLOUR = '#EAEAEA'
CONTROLSLIDER_TEXT_COLOUR = '#000000'

TRACKS_BACKGROUND_COLOUR = "#444444"

FXBOX_OUTLINE_COLOUR = "#222222"
FXBOX_ENABLE_BACKGROUND_COLOUR = "#EEEEEE"
FXBOX_DISABLE_BACKGROUND_COLOUR = "#CCCCCC"
FXBOX_FOREGROUND_COLOUR = "#000000"

SOUNDFILE_CELL_BACKGROUND_COLOUR = "#FFFFFF"
SOUNDFILE_AUTO_CELL_BACKGROUND_COLOUR = "#00FF00"

