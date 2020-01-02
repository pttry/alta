call cleanup.bat
del test.zip
pkzipc -add test @ziplist

pkzipc -del test *.af2
pkzipc -del test notes.*
pkzipc -del test real*.cmf
pkzipc -del test orng*.*
pkzipc -del test oran*.*
pkzipc -del test Adtiny*.*
pkzipc -del test *.doc
pkzipc -del test Termsc*.*
pkzipc -del test ChkmdD.*
pkzipc -del test prepare.*
pkzipc -del test raslin2.*

pkzipc -del test tstdif.*
pkzipc -del test rntstdif.*
pkzipc -del test rnAdtiny.*
pkzipc -del test rnTermsc.*
pkzipc -del test rnChkmdD.*
pkzipc -del test mkdatawas.*

pkzipc -add test regdata.doc

rd/s/q test
md test
md  \chterm\data
del/q \chterm\data\*.*
copy test.zip \chterm\data

move test.zip test
cd test
unzip test
dir/w
pause
call mkdata.bat
cd ..
