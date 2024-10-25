# © 2024 Fraunhofer-Gesellschaft e.V., München
# SPDX-License-Identifier: AGPL-3.0-or-later

# This shell file can be used to run some of the pipline commands locally
# Run it with the command ./pipeline.sh.
# Also see GitHub workflows


echo "Installing python requirements..."
pip install -e .[dev]

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
