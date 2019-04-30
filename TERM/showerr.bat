if errorlevel 1 goto ERR
echo ###### ERRORLEVEL 0 #####
goto endbat
:err
echo ###### ERRORLEVEL 1 #####
:endbat
