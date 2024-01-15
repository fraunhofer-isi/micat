# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# -*- coding: utf-8 -*-
import sys

import flask
from waitress import serve

from back_end import BackEnd
from development import Development
from utils import settings as micat_settings


def main(arguments):
    if len(arguments) != 2:
        print("Usage: python main.py confidential_database_path")
        return

    # workaround to fix issue with relative path to python in PyCharm for debugging
    # Also see
    # https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/363
    sys.executable = sys.executable.replace('micat\\App', 'micat\\..\\..\\App')

    host = 'localhost'
    front_end_host = host  # 'frontend.micat-project.eu'  # host
    front_end_route = '/'  # ''
    port = 5000
    front_end_port = 3000  # 80
    settings = micat_settings.load()
    _open_browser_if_enabled(
        front_end_host,
        front_end_port,
        front_end_route,
        settings,
    )

    # file_name = arguments[0]

    confidential_database_path = arguments[1]

    debug_mode = settings['debugMode']
    back_end = BackEnd(
        serve,
        flask,
        front_end_port,
        debug_mode,
        confidential_database_path=confidential_database_path,
    )

    back_end.start(host=host, application_port=port)


def _open_browser_if_enabled(
    host,
    front_end_port,
    front_end_route,
    settings,
):
    open_browser_window = settings['openBrowserWindow']
    if open_browser_window:
        front_end_url = _front_end_url(
            host,
            front_end_port,
            front_end_route,
        )
        Development.open_browser(front_end_url)


def _front_end_url(
    host,
    front_end_port,
    front_end_route,
):
    front_end_prefix = 'http:/' + host + ':' + str(front_end_port)
    url = front_end_prefix + front_end_route
    return url


if __name__ == '__main__':
    main(sys.argv)
