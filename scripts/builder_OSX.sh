##################################
# QLive OSX standalone application
# builder script.
#
# Olivier Belanger, 2016
##################################

export DMG_DIR="QLive 0.1.3"
export DMG_NAME="QLive_0.1.3.dmg"

python2 setup.py py2app

rm -rf build
mv dist QLive_OSX

if cd QLive_OSX;
then
    find . -name .git -depth -exec rm -rf {} \
    find . -name *.pyc -depth -exec rm -f {} \
    find . -name .* -depth -exec rm -f {} \;
else
    echo "Something wrong. QLive_OSX not created"
    exit;
fi

rm QLive.app/Contents/Resources/QLive-Icon.ico

# keep only 64-bit arch
ditto --rsrc --arch x86_64 QLive.app QLive-x86_64.app
rm -rf QLive.app
mv QLive-x86_64.app QLive.app

# Fixed wrong path in Info.plist
cd QLive.app/Contents
awk '{gsub("Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python", "@executable_path/../Frameworks/Python.framework/Versions/2.7/Python")}1' Info.plist > Info.plist_tmp && mv Info.plist_tmp Info.plist

cd ../../..
cp -R QLive_OSX/QLive.app .

echo "assembling DMG..."
mkdir "$DMG_DIR"
cd "$DMG_DIR"
cp -R ../QLive.app .
ln -s /Applications .

cd ..

hdiutil create "$DMG_NAME" -srcfolder "$DMG_DIR"

rm -rf "$DMG_DIR"
rm -rf QLive_OSX
rm -rf QLive.app
