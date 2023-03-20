@echo off

echo Cleaning SystemSDKExample project ...

rem Delete Visual Studio files
erase *.pdb
erase *.APS
erase *.bak
erase *.ilk
erase *.sdf
erase *.obj
erase *.sbr
erase *.ncb
erase *.tlog
erase *.bsc

rem Below binary folder when compiled on Visual Studio 2010
rmdir /S /Q ipch
rmdir /S /Q x64
rmdir /S /Q DebugVer2
rmdir /S /Q ReleaseVer2

echo Cleaning SystemSDKExample project done
