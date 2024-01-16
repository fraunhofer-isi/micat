# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
# pylint: disable=protected-access
import os

from mock import patch as original_patch

from micat.test_utils.isi_mock import Mock, patch, patch_by_string
from micat.utils import settings

mocked_settings = {
    'backEnd': {
        'api': 'mocked_api_settings',
    },
}


@patch(settings._settings_path, 'mocked_path')
@patch_by_string('builtins.open', Mock())
@patch(json.load, mocked_settings)
def test_load():
    result = settings.load()
    assert result == 'mocked_api_settings'


@patch(settings._parent_folder_of_this_file)
@patch(settings._search_settings_path, 'mocked_settings_path')
class TestSettingsPath:
    @patch_by_string('os.path.exists', True)
    def test_with_direct_settings(self):
        result = settings._settings_path()
        assert result == 'mocked_settings_path'

    @patch_by_string('os.path.exists', False)
    @patch(settings._working_directory, 'mocked_working_directory')
    def test_without_user_settings(self):
        result = settings._settings_path()
        assert result == 'mocked_settings_path'


class TestSearchSettingsPath:
    @patch(os.path.join, 'mocked_path')
    @patch_by_string('os.path.exists', True)
    def test_with_local_user_settings(self):
        result = settings._search_settings_path('mocked_project_root')
        assert result == 'mocked_path'

    @staticmethod
    def mocked_exist(path):
        exists = path.endswith('default.json')
        return exists

    @staticmethod
    def mocked_join(_path, _prefix, file_name):
        return file_name

    @original_patch('os.path.exists', mocked_exist)
    @original_patch('os.path.join', mocked_join)
    def test_without_local_user_settings(self):
        result = settings._search_settings_path('mocked_project_root')
        assert result == '.settings.default.json'

    @patch(os.path.exists, False)
    @patch(os.path.join, 'mocked_path')
    def test_without_settings(self):
        result = settings._search_settings_path('mocked_project_root')
        assert result is None


@patch(os.path.dirname, 'mocked_result')
def test_parent_folder_of_this_file():
    result = settings._parent_folder_of_this_file()
    assert result == 'mocked_result'


@patch_by_string('os.getcwd', 'mocked_result')
def test_working_directory():
    result = settings._working_directory()
    assert result == 'mocked_result'
