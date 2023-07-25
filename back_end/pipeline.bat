REM This batch file can be used to run some of the pipline commands locally
REM Run it with the command ./piepline.bat from within PyCharm terminal.
REM Also see .gitlab.ci.yml in the root directory


echo "Installing python requirements..."
pip install -e .[dev] | findstr /V /C:"Requirement already satisfied"

echo "Formatting code..."
isort .
black src -S -l 120
black test -S -l 120
black import -S -l 120

echo "Checking code quality with  pylint..."
pylint src
pylint test --recursive=true
pylint import --recursive=true

echo "Running unit tests and determining test coverage..."
pytest --cov

if (%1==skip_pause) (
 echo "Finished back_end commands."
) else (
 echo "Finished back_end commands."
 pause
)

