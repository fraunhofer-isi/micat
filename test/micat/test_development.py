# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mock import MagicMock, call, patch

from micat.development import Development


class TestOpenBrowser:
    @patch('os.path')
    @patch('os.system')
    @patch('builtins.print')
    def test_chrome_exists(self, mocked_print, mocked_system, mocked_path):
        mocked_path.isfile = MagicMock(return_value=True)
        Development.open_browser('url_mock')

        assert mocked_print.mock_calls == [call('Opening browser at url_mock')]
        assert len(mocked_system.mock_calls) == 1

    @patch('os.path')
    @patch('builtins.print')
    def test_chrome_does_not_exist(self, mocked_print, mocked_path):
        mocked_path.isfile = MagicMock(return_value=False)
        Development.open_browser('url_mock')

        assert mocked_print.mock_calls == [
            call(
                'Could not open browser for development session.',
                '(Which is fine if this runs on the deployment server).',
            ),
        ]
