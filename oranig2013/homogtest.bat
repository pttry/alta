REM Build model
    tablo -pgs ORANIG
REM Solve model using GEMSIM: homogenity test
    gemsim -cmf htest.CMF
    if errorlevel 1 goto err

dir/od *.har
dir/od *.sl4
echo JOB DONE OK
goto endbat
:err
echo ERROR
:endbat

pause