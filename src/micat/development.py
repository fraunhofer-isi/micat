# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os


class Development:
    @staticmethod
    def open_browser(url):
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        if os.path.isfile(chrome_path):
            print('Opening browser at ' + url)
            # List of chrome command line switches:
            # https://peter.sh/experiments/chromium-command-line-switches/
            # We use a non-existing disk-cache-dir to disable caching. See
            # https://stackoverflow.com/questions/40314005/command-line-flag-to-disable-all-types-of-caches-in-chrome
            #
            # The flag --disable-web-security is used to allow fetch of descriptions from weblication page.
            # There might be a waring of unsupported command line options. It nevertheless should work.
            # Also see following SQ question to see how to check if web security is disabled
            # https://stackoverflow.com/questions/35432749/disable-web-security-in-chrome-48
            command = (
                'start "chrome" "'
                + chrome_path
                + '" --user-data-dir="C:/ChromeDevelopmentSessionForMicat/userdata"'
                + ' --profile-directory=Default --auto-open-devtools-for-tabs'
                + ' --disk-cache-dir=/dev/null '
                + ' --disable-web-security --disable-site-isolation-trials '
                + url
            )
            os.system(command)
        else:
            print(
                'Could not open browser for development session.',
                '(Which is fine if this runs on the deployment server).',
            )
