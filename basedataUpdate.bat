REM Update adjusted values for V1CAP and V1OCT from capital
REM calculations into the basedata.har and create new file
REM called basedataNEW.har
mergehar hardata\basedata.har hardata\adjustData.har hardata\basedataNEW.har YY2

REM Copy har files to TERM, where they are later needed:
copy hardata\basedataNEW.har TERM\basedataNEW.har
copy hardata\REGSUPP.har TERM\REGSUPP.har


pause