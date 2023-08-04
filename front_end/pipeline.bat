REM © 2023 Fraunhofer-Gesellschaft e.V., München
REM
REM SPDX-License-Identifier: AGPL-3.0-or-later

REM This batch file can be used to run some of the pipline commands locally
REM Run it with the command ./pipeline.bat from within PyCharm or VsCodium terminal.
REM Also see .gitlab.ci.yml in the root folder

echo "Installing JavaScript dependencies..."
npm install

echo "Checking code quality with eslint..."
npm run lint

echo "Running unit tests and determining test coverage..."
npm run test-coverage

if %1==skip_pause (
  echo "Finished front_end commands."
) else (
  echo "Finished front_end commands."
  pause
)