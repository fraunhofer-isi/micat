# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import os


def load():
    settings_path = _settings_path()
    with open(settings_path, 'r', encoding='utf-8') as file:
        settings = json.load(file)
        api_settings = settings['backEnd']['api']
        return api_settings


def _settings_path():
    project_root = _parent_folder()
    user_settings_path = _user_settings_path(project_root)
    if os.path.exists(user_settings_path):
        return user_settings_path
    else:
        return _search_settings_path(project_root)


def _search_settings_path(project_root):
    local_user_settings_path = _local_user_settings_path(project_root)
    if os.path.exists(local_user_settings_path):
        return local_user_settings_path
    else:
        return _search_default_settings_path(project_root)


def _search_default_settings_path(project_root):
    default_user_settings_path = _default_settings_path(project_root)
    if os.path.exists(default_user_settings_path):
        return default_user_settings_path
    else:
        return _local_default_settings_path(project_root)


def _parent_folder():
    current_folder = os.path.dirname(__file__)
    parent_folder = os.path.dirname(current_folder)
    return parent_folder


def _local_user_settings_path(project_root):
    relative_path = os.path.join(project_root, '..', '..', '.settings.json')
    absolute_path = os.path.abspath(relative_path)
    return absolute_path


def _user_settings_path(project_root):
    relative_path = os.path.join(project_root, '..', '.settings.json')
    absolute_path = os.path.abspath(relative_path)
    return absolute_path


def _local_default_settings_path(project_root):
    relative_path = os.path.join(project_root, '..', '..', '.settings.default.json')
    absolute_path = os.path.abspath(relative_path)
    return absolute_path


def _default_settings_path(project_root):
    relative_path = os.path.join(project_root, '.settings.default.json')
    absolute_path = os.path.abspath(relative_path)
    return absolute_path
