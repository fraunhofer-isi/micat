# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mock import MagicMock, patch

from utils.file import (
    create_folder_if_not_exists,
    delete_file_if_exists,
    delete_folder_if_exists,
)


class TestCreateFolderIfNotExists:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_path_exists(self):
        with patch('os.makedirs', MagicMock()) as mocked_makedirs:
            create_folder_if_not_exists('mocked_folder_path')
            mocked_makedirs.assert_not_called()

    @patch('os.path.exists', MagicMock(return_value=False))
    def test_path_does_not_exist(self):
        with patch('os.makedirs', MagicMock()) as mocked_makedirs:
            create_folder_if_not_exists('mocked_folder_path')
            mocked_makedirs.assert_called()


class TestDeleteFolderIfExists:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_path_exists(self):
        with patch('shutil.rmtree', MagicMock()) as mocked_rmtree:
            delete_folder_if_exists('mocked_folder_path')
            mocked_rmtree.assert_called()

    @patch('os.path.exists', MagicMock(return_value=False))
    def test_path_does_not_exist(self):
        with patch('shutil.rmtree', MagicMock()) as mocked_rmtree:
            delete_folder_if_exists('mocked_folder_path')
            mocked_rmtree.assert_not_called()


class TestDeleteFileIfExists:
    @patch('os.path.exists', MagicMock(return_value=True))
    def test_path_exists(self):
        with patch('os.remove', MagicMock()) as mocked_remove:
            delete_file_if_exists('mocked_file_path')
            mocked_remove.assert_called()

    @patch('os.path.exists', MagicMock(return_value=False))
    def test_path_does_not_exist(self):
        with patch('os.remove', MagicMock()) as mocked_remove:
            delete_file_if_exists('mocked_file_path')
            mocked_remove.assert_not_called()
