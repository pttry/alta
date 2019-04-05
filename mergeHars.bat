REM combine basedata30 and regExtension into a single file
REM called basedata.har
mergehar hardata\basedata30.har hardata\regExtension.har hardata\basedata.har YY1

REM copy the new version to the oranig folder
copy hardata\basedata.har oranig2013\basedata.har

pause