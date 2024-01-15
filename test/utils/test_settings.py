# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
from mock import MagicMock, patch

from utils import settings

mocked_settings = {
    'backEnd': {
        'api': 'mocked_api_settings',
    },
}


@patch('utils.settings._settings_path', MagicMock(return_value='mocked_path'))
@patch("builtins.open", MagicMock())
@patch('json.load', MagicMock(return_value=mocked_settings))
def test_load():
    result = settings.load()
    assert result == 'mocked_api_settings'


@patch('utils.settings._parent_folder', MagicMock())
@patch(
    'utils.settings._user_settings_path',
    MagicMock(return_value='mocked_user_settings_path'),
)
class TestSettingsPath:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_with_user_settings(self):
        result = settings._settings_path()
        assert result == 'mocked_user_settings_path'

    @patch('os.path.exists', MagicMock(return_value=False))
    @patch(
        'utils.settings._search_settings_path',
        MagicMock(return_value='mocked_found_settings_path'),
    )
    def test_without_user_settings(self):
        result = settings._settings_path()
        assert result == 'mocked_found_settings_path'


@patch(
    'utils.settings._local_user_settings_path',
    MagicMock(return_value='mocked_local_user_settings_path'),
)
class TestSearchSettingsPath:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_with_local_user_settings(self):
        result = settings._search_settings_path('mocked_project_root')
        assert result == 'mocked_local_user_settings_path'

    @patch('os.path.exists', MagicMock(return_value=False))
    @patch(
        'utils.settings._search_default_settings_path',
        MagicMock(return_value='mocked_found_settings_path'),
    )
    def test_without_local_user_settings(self):
        result = settings._search_settings_path('mocked_project_root')
        assert result == 'mocked_found_settings_path'


@patch(
    'utils.settings._default_settings_path',
    MagicMock(return_value='mocked_default_user_settings_path'),
)
class TestSearchDefaultSettingsPath:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_with_local_user_settings(self):
        result = settings._search_default_settings_path('mocked_project_root')
        assert result == 'mocked_default_user_settings_path'

    @patch('os.path.exists', MagicMock(return_value=False))
    @patch(
        'utils.settings._local_default_settings_path',
        MagicMock(return_value='mocked_found_settings_path'),
    )
    def test_without_local_user_settings(self):
        result = settings._search_default_settings_path('mocked_project_root')
        assert result == 'mocked_found_settings_path'


@patch('os.path.dirname', MagicMock(return_value='mocked_result'))
def test_parent_folder():
    result = settings._parent_folder()
    assert result == 'mocked_result'


@patch('os.path.join', MagicMock(return_value='mocked_path'))
@patch('os.path.abspath', MagicMock(return_value='mocked_result'))
def test_user_settings_path():
    result = settings._user_settings_path('mocked_project_root')
    assert result == 'mocked_result'


@patch('os.path.join', MagicMock(return_value='mocked_path'))
@patch('os.path.abspath', MagicMock(return_value='mocked_result'))
def test_local_user_settings_path():
    result = settings._local_user_settings_path('mocked_project_root')
    assert result == 'mocked_result'


@patch('os.path.join', MagicMock(return_value='mocked_path'))
@patch('os.path.abspath', MagicMock(return_value='mocked_result'))
def test_default_settings_path():
    result = settings._default_settings_path('mocked_project_root')
    assert result == 'mocked_result'


@patch('os.path.join', MagicMock(return_value='mocked_path'))
@patch('os.path.abspath', MagicMock(return_value='mocked_result'))
def test_local_default_settings_path():
    result = settings._local_default_settings_path('mocked_project_root')
    assert result == 'mocked_result'
