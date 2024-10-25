REM © 2024 Fraunhofer-Gesellschaft e.V., München
REM
REM SPDX-License-Identifier: AGPL-3.0-or-later

REM This batch file can be used to run some of the pipline commands locally
REM Run it with the command ./piepline.bat from within PyCharm terminal.
REM Also see GitHub workflows


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

echo "Creating reuse annotations"
python -m reuse annotate --copyright="Fraunhofer-Gesellschaft e.V., München" --copyright-style=symbol --merge-copyrights --license=AGPL-3.0-or-later --skip-unrecognised --recursive src test doc THIRDPARTY.md

echo "Checking REUSE Compliance"
python -m reuse lint

if (%1==skip_pause) (
 echo "Finished back_end commands."
) else (
 echo "Finished back_end commands."
 pause
)

