##################################
# QLive OSX standalone application
# builder script.
#
# Olivier Belanger, 2015
##################################

export DMG_DIR="QLive 0.1.0"
export DMG_NAME="QLive_0.1.0.dmg"

py2applet --make-setup --argv-emulation=0 QLive.py Resources/*
python setup.py py2app --plist=scripts/info.plist
rm -f setup.py
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

cd ..
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
