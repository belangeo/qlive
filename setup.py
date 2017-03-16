"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
from setuptools import setup

APP = ['QLive.py']
APP_NAME = 'QLive'
DATA_FILES = ['Resources/']
OPTIONS = {'argv_emulation': False,
           'iconfile': 'Resources/QLive-Icon.icns',
           'plist': {
               'CFBundleDisplayName': 'QLive',
               'CFBundleExecutable': 'QLive',
               'CFBundleIconFile': 'QLive-Icon.icns',
               'CFBundleIdentifier': 'com.litem.umontreal.ca.QLive',
               'CFBundleInfoDictionaryVersion': '0.1.3',
               'CFBundleName': 'QLive',
               'CFBundlePackageType': 'APPL',
               'CFBundleShortVersionString': '0.1.3',
               'CFBundleVersion': '0.1.3',
           }
       }

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
