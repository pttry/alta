echo
echo *****************************
echo       Homogenity test
echo *****************************
echo

REM Delete old files
del *.bak
del *.log

REM Test for Homogenity (psi +10)
tablo -sti oranig03.sti >nul
gemsim -cmf otest.cmf

:endbat
pause
