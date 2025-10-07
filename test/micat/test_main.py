# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat import development, main, utils
from micat.back_end import BackEnd

# pylint: disable=too-many-arguments
# pylint: disable=protected-access
from micat.test_utils.isi_mock import MagicMock, call, patch, patch_by_string

# noinspection PyProtectedMember

# noinspection PyProtectedMember


mocked_settings = {
    "debugMode": False,
}

mocked_start = MagicMock()


def back_end_init_mock(
    self,
    injected_serve,  # pylint: disable=unused-argument
    injected_flask,  # pylint: disable=unused-argument
    front_end_port,  # pylint: disable=unused-argument
    debug_mode,  # pylint: disable=unused-argument
    database_path="../data/public.sqlite",  # pylint: disable=unused-argument
    confidential_database_path="../data/confidential.sqlite",  # pylint: disable=unused-argument
):
    self.start = mocked_start


class TestMain:
    @patch(utils.settings.load, mocked_settings)
    @patch(main._open_browser_if_enabled)
    @patch.object(BackEnd, "__init__", back_end_init_mock)
    @patch(main._confidential_database_path, "mocked_confidential_database_path")
    def test_with_arguments(self):
        arguments = ["mocked_file_path", "mocked_confidential_database_path"]
        main.main(arguments)
        assert mocked_start.mock_calls[0] == call(host="localhost", application_port=8000)

    @patch(main._confidential_database_path, None)
    def test_without_confidential_database(self):
        with patch_by_string("builtins.print", None) as patched_print:
            main.main()
            patched_print.assert_called()


class TestConfidentialDatabasePath:
    @patch_by_string("os.path.exists", True)
    def test_without_arguments(self):
        result = main._confidential_database_path(None)
        assert result == "./data/confidential.sqlite"

    @patch_by_string("os.path.exists", True)
    def test_with_missing_argument(self):
        result = main._confidential_database_path(["mocked_file_path"])
        assert result is None

    @patch_by_string("os.path.exists", True)
    def test_with_explicit_database_path(self):
        result = main._confidential_database_path(["mocked_file_path", "mocked_confidential_database_path"])
        assert result == "mocked_confidential_database_path"

    @patch_by_string("os.path.exists", False)
    @patch_by_string("builtins.print", None)
    def test_with_non_existing_database_path(self):
        result = main._confidential_database_path(["mocked_file_path", "mocked_confidential_database_path"])
        assert result is None


@patch(main._front_end_url)
@patch(development.Development.open_browser)
def test_open_browser_if_enabled():
    front_end_path = ""
    settings = {
        "openBrowserWindow": True,
    }
    main._open_browser_if_enabled(
        "mocked_host",
        3000,
        front_end_path,
        settings,
    )


@patch(development.Development.open_browser)
def test_front_end_url():
    front_end_path = "/micat-next"
    result = main._front_end_url(
        "mocked_host",
        3000,
        front_end_path,
    )
    expected_url = "http:/mocked_host:3000/micat-next"
    assert result == expected_url
