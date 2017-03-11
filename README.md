QLive
=====

QLive is a cues-based software to help the creation of mixed music
(live instruments + electronic).

Main goals of the project
-------------------------

- Propose a solution to the problem of technological obsolescence in mixed 
  music creation.

- Facilitate the development of a heuristic pedagogy of mixed music for 
  performers and composers.

Requirements
------------

If you want to try the current development version of QLive (it is still in 
alpha stage), you'll have to install these softwares/libraries on your system:

- [Python 2.7](https://www.python.org/downloads/release/python-2712/) : The
  programming language. Windows users must install the 32-bit version of python.

- [WxPython 3.0](http://wxpython.org/download.php) : The GUI toolkit. Choose 
  the installer that fits your python version.

- [Pyo (compiled from source)](http://ajaxsoundstudio.com/software/pyo/) : The audio engine. 
  Need the very last update (commit 08a223aa500911a286065c2a9643343f21f5a937).

- [psutil 4.3.0+](https://pypi.python.org/pypi/psutil) : Library used to 
  retrieve memory and CPU usage.

Starting the application
------------------------

Download and extract the QLive sources and, in a terminal window, navigate 
to the qlive folder:

```bash
cd qlive/src/folder
```

Then, start the app:

```bash
python QLive.py
```
