call deljunk.bat
call compile preagg
if errorlevel 1 goto error
echo on
preagg -cmf preagg.cmf 
if errorlevel 1 goto error

REM The following causes error due to maptxt
REM maptxt mapagg.har aggmap.txt >maptxt.log 
REM if errorlevel 1 goto error
REM aggmap jap9 aggmap aggmap >aggmap.log
REM if errorlevel 1 goto error


dir/od *.har
echo BATCH JOB SUCCESSFUL
dir preagg.har
dir aggmap.*
goto endbat
:error
echo off
echo ###### ERROR: BATCH JOB FAILED #####
echo Check log file; most recent is listed last
dir/od *.log
:again
echo Please press CTRL-C to terminate batch job
pause > nul
goto again
:endbat
