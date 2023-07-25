REM This batch file can be used to run some of the pipline commands locally
REM Run it with the command ./pipeline.bat from within PyCharm terminal.
REM Also see .gitlab.ci.yml

echo "Simulating front_end pipeline jobs..."'

cd back_end
call ./pipeline.bat skip_pause
cd ..

echo "Simulating front_end pipeline jobs..."'
cd front_end
call ./pipeline.bat skip_pause

cd ..

echo "...finished simulating pipline jobs."'

pause