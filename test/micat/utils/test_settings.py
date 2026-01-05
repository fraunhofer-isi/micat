# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

# pylint: disable=protected-access
import os
from json import JSONDecodeError

from mock import patch as original_patch

from micat.test_utils.isi_mock import Mock, mock_open, patch, patch_by_string, raises
from micat.utils import settings

mocked_settings = {
    'backEnd': {
        'api': 'mocked_api_settings',
    },
}


class TestLoad:
    @patch(settings._settings_path, 'mocked_path')
    @patch_by_string('builtins.open', Mock())
    @patch(json.load, mocked_settings)
    def test_normal_usage(self):
        result = settings.load()
        assert result == 'mocked_api_settings'

    mocked_file = Mock()

    @patch(settings._settings_path, 'mocked_path')
    @patch(json.load, Mock(side_effect=JSONDecodeError('foo', Mock(), Mock())))
    @patch(print)
    def test_with_error(self):
        with original_patch('builtins.open', mock_open(read_data="mocked_file_line_data")):
            with raises(JSONDecodeError):
                settings.load()


@patch(settings._parent_folder_of_this_file)
class TestSettingsPath:
    @patch(settings._search_settings_path, 'mocked_settings_path')
    def test_with_direct_settings(self):
        result = settings._settings_path()
        assert result == 'mocked_settings_path'

    @patch(settings._working_directory, 'mocked_working_directory')
    @patch(settings._search_settings_path, None)
    def test_without_user_settings(self):
        result = settings._settings_path()
        assert result is None


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
