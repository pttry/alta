echo on
tablo %1 -wfp
if errorlevel 1 goto error
seterr 1
call ltg %1
if errorlevel 1 goto error
echo SUCCESSFULLY COMPILED %1
goto endbat
:error
echo off
echo ###### ERROR: FAILED TO COMPILE %1 #####
:endbat
echo on
