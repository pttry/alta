REM Delete old file if it exists:
del/s hardata\basedata30.har

agghar hardata\basedata64.har hardata\basedata30.har hardata\AGGSUP.har -p
pause