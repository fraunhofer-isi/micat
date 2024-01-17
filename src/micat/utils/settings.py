# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import os
from json import JSONDecodeError


def load():
    settings_path = _settings_path()
    absolute_settings_path = os.path.abspath(settings_path)
    print('Loading settings from ' + absolute_settings_path)
    with open(absolute_settings_path, 'r', encoding='utf-8') as file:
        try:
            settings = json.load(file)
        except JSONDecodeError as error:
            print('Could not load json file:')
            for line in file:
                print(line)

            raise error
        api_settings = settings['backEnd']['api']
        return api_settings


def _settings_path():
    project_root = _parent_folder_of_this_file()
    settings_path = _search_settings_path(project_root)
    if settings_path is not None:
        return settings_path
    else:
        working_directory = _working_directory()
        return _search_settings_path(working_directory)


def _search_settings_path(reference_folder):
    prefixes = ['', '..', '../..', '../../..', '../../../..']
    for prefix in prefixes:
        settings_path = os.path.join(reference_folder, prefix, '.settings.json')
        if os.path.exists(settings_path):
            return settings_path

        default_settings_path = os.path.join(reference_folder, prefix, '.settings.default.json')
        if os.path.exists(default_settings_path):
            return default_settings_path

    return None


def _parent_folder_of_this_file():
    current_folder = os.path.dirname(__file__)
    parent_folder = os.path.dirname(current_folder)
    return parent_folder


def _working_directory():
    working_directory = os.getcwd()
    return working_directory
