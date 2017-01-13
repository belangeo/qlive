import os, shutil, sys

version = sys.version_info[:2]

os.system('C:\Python%d%d\Scripts\pyinstaller --clean -F -c --icon=Resources\QLive-Icon.ico "QLive.py"' % version)
#os.system('C:\Python%d%d\Scripts\pyi-build "QLive.spec"' % version)

os.system("git checkout-index -a -f --prefix=QLive_Win/")
os.system("copy dist\QLive.exe QLive_Win /Y")
os.system("rmdir /Q /S QLive_Win\scripts")
os.remove("QLive_Win/QLive.py")
#os.remove("QLive_Win/Resources/QLive-Icon.icns")
#os.remove("QLive_Win/Resources/QLive-DocIcon.icns")
os.remove("QLive.spec")
os.system("rmdir /Q /S build")
os.system("rmdir /Q /S dist")
for f in os.listdir(os.getcwd()):
    if f.startswith("warn") or f.startswith("logdict"):
        os.remove(f)

