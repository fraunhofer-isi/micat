# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

# -*- coding: utf-8 -*-
import sys

import flask
from waitress import serve

from micat.back_end import BackEnd
from micat.development import Development
from micat.utils import settings as micat_settings


def main(arguments=None):
    # Optionally you can pass a path to the confidential database, for example
    # ../../../micat_confidential/src/micat_confidential/data/confidential.sqlite
    # or put the file at ./data/confidential.sqlite
    confidential_database_path = _confidential_database_path(arguments)
    if confidential_database_path is None:
        print("Usage: main.py confidential_database_path")
        return

    # workaround to fix issue with relative path to python in PyCharm for debugging
    # Also see
    # https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/363
    sys.executable = sys.executable.replace("micat\\App", "micat\\..\\..\\App")

    host = "localhost"
    front_end_host = host  # 'frontend.micat-project.eu'  # host
    front_end_route = "/"  # ''
    port = 8000
    front_end_port = 3000  # 80
    settings = micat_settings.load()
    _open_browser_if_enabled(
        front_end_host,
        front_end_port,
        front_end_route,
        settings,
    )

    database_path = _database_path()

    debug_mode = settings["debugMode"]
    back_end = BackEnd(
        serve,
        flask,
        front_end_port,
        debug_mode,
        database_path=database_path,
        confidential_database_path=confidential_database_path,
    )

    back_end.start(host=host, application_port=port)


def _database_path():
    # we use a relative path from this main file instead of
    # using the working directory, so that the file can also be found
    # when this project is used as python package
    current_folder = os.path.dirname(__file__)
    database_path = os.path.join(
        current_folder,
        "data",
        "public.sqlite",
    )
    return database_path


def _confidential_database_path(arguments):
    if arguments is None:
        confidential_database_path = "./data/confidential.sqlite"
    else:
        if len(arguments) != 2:
            return None
        else:
            # file_name = arguments[0]
            confidential_database_path = arguments[1]

    if os.path.exists(confidential_database_path):
        return confidential_database_path
    else:
        print('Could not find path to confidential database "' + confidential_database_path + '"')
        return None


def _open_browser_if_enabled(
    host,
    front_end_port,
    front_end_route,
    settings,
):
    open_browser_window = settings["openBrowserWindow"]
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
    front_end_prefix = "http:/" + host + ":" + str(front_end_port)
    url = front_end_prefix + front_end_route
    return url


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
