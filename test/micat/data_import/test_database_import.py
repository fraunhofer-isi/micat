# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
# pylint: disable=too-many-arguments
import sqlite3

import pandas

from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.mapping_table import MappingTable
from micat.test_utils.isi_mock import (
    Mock,
    disable_stdout,
    enable_stdout,
    fixture,
    patch,
    patch_by_string,
    patch_sqlite_connect,
    raises,
)
from micat.utils import file


@fixture(name="sut")
def sut_fixture():
    return DatabaseImport("mocked_data_base_path")


class TestPublicApi:
    @patch_by_string("subprocess.run", Mock())
    @patch_by_string("os.getcwd", "mocked_cwd")
    @patch_by_string("os.path.join", "mocked_file_a.py")
    @patch_by_string("os.listdir", ["mocked_file_a.py", "mocked_file_b.py"])
    @patch_by_string("os.path.isfile", True)
    @patch_by_string("os.path.splitext", ["test", ".py"])
    class TestExcecuteImportScriptsInFolder:
        def test_without_excluded_scripts(self):
            disable_stdout()
            DatabaseImport.execute_import_scripts_in_folder("mocked_src_path")
            enable_stdout()

        def test_with_excluded_scripts(self):
            disable_stdout()
            DatabaseImport.execute_import_scripts_in_folder(
                "mocked_src_path",
                "mocked_cwd",
                ["mocked_file_a.py"],
            )
            enable_stdout()

    @patch(file.delete_file_if_exists)
    class TestWriteMissingEntriesAsExcelFile:
        def test_without_entries(self):
            DatabaseImport.write_missing_entries_as_excel_file(
                "mocked_file_path",
                [],
                "mocked_column_mapping",
                "mocked_years",
                "mocked_value",
                "mocked_exclusions",
            )

        @staticmethod
        def mocked_create_row(entry, _column_mapping, year, _value, _exclusions):
            return {"REGION_LABEL": entry["id_region"], "YEAR": year, "FACTOR": 1}

        @patch(DatabaseImport._create_missing_row, mocked_create_row)
        @patch(DatabaseImport._is_extra_row, True)
        @patch(pandas.DataFrame.to_excel, Mock())
        def test_with_entries(self):
            mocked_entries = [
                {"id_region": 2, "year": 2000},
                {"id_region": 1},
            ]

            mocked_column_mapping = {
                "REGION_LABEL": "id_region",
                "FACTOR": "value",
            }

            mocked_years = [2001]

            DatabaseImport.write_missing_entries_as_excel_file(
                "mocked_file_path",
                mocked_entries,
                mocked_column_mapping,
                mocked_years,
                "mocked_value",
                "mocked_exclusions",
            )

    class TestCreateMissingRow:
        @patch(
            DatabaseImport._determine_column_entry,
            "mocked_entry",
        )
        def test_with_exclusion(self):
            missing_entry = {
                "id_region": (0, "Foo"),
            }
            exclusions = {"id_region": 0}

            column_mapping = {
                "REGION_LABEL": "id_region",
            }

            result = DatabaseImport._create_missing_row(
                missing_entry,
                column_mapping,
                "mocked_year",
                "mocked_value",
                exclusions,
            )
            assert result is None

        @patch(
            DatabaseImport._determine_column_entry,
            "mocked_entry",
        )
        def test_without_exclusion(self):
            missing_entry = {
                "id_region": (1, "Baa"),
            }
            exclusions = {"id_region": 0}

            column_mapping = {
                "REGION_LABEL": "id_region",
            }

            result = DatabaseImport._create_missing_row(
                missing_entry,
                column_mapping,
                "mocked_year",
                "mocked_value",
                exclusions,
            )
            assert result["REGION_LABEL"] == "mocked_entry"

    class TestIsExtraRow:
        def test_none(self):
            result = DatabaseImport._is_extra_row(None, "mocked_rows")
            assert result is False

        def test_existing_row(self):
            result = DatabaseImport._is_extra_row("foo", ["foo"])
            assert result is False

        def test_not_existing_row(self):
            result = DatabaseImport._is_extra_row("foo", ["baa"])
            assert result is True

    @patch(sqlite3.connect)
    def test_append_to_sqlite(self, sut):
        sut._table_validator.validate = Mock()

        mocked_table = Mock()
        mocked_to_sql = Mock()
        mocked_table.to_sql = mocked_to_sql

        with patch(DatabaseImport._check_if_table_exists) as mocked_check:
            sut.append_to_sqlite(mocked_table, "mocked_table_name")

            mocked_check.assert_called_once()
            mocked_to_sql.assert_called_once()

    class TestImportIdTable:
        @patch(sqlite3.connect)
        @patch(DatabaseImport._delete_table_if_exists)
        @patch(DatabaseImport._query_to_create_id_table)
        def test_without_label_issue(self, sut):
            mocked_df = Mock()
            mocked_df.to_sql = Mock()

            with patch(DatabaseImport._read_id_table_from_excel_file) as mocked_read:
                with patch(DatabaseImport._check_labels) as mocked_check:
                    mocked_read.return_value = mocked_df
                    sut.import_id_table(
                        "mocked_table_name",
                        "mocked_directory",
                        "mocked_optional_explicit_columns_that_will_be_unique",
                    )

                    mocked_check.assert_called_once()

                    mocked_df.to_sql.assert_called_once()

        @patch(
            DatabaseImport._check_labels,
            Mock(side_effect=ValueError("mocked_error")),
        )
        @patch(print)
        @patch(DatabaseImport._read_id_table_from_excel_file)
        def test_with_label_issue(self, sut):
            with raises(ValueError):
                sut.import_id_table(
                    "mocked_table_name",
                    "mocked_directory",
                    "mocked_optional_explicit_columns_that_will_be_unique",
                )

        @patch(
            DatabaseImport._check_labels,
            Mock(side_effect=ValueError("mocked_error")),
        )
        @patch(print)
        @patch(DatabaseImport._read_id_table_from_database)
        def test_with_database_path(self, sut):
            with raises(ValueError):
                sut.import_id_table(
                    "mocked_table_name",
                    "mocked_database_path.sqlite",
                    "mocked_optional_explicit_columns_that_will_be_unique",
                )

    class TestImportMappingTable:
        @patch(sqlite3.connect)
        @patch(DatabaseImport._delete_table_if_exists)
        @patch(DatabaseImport._query_to_create_mapping_table)
        def test_with_target_table_name(self, sut):
            mocked_df = Mock()
            mocked_df.to_sql = Mock()

            with patch(DatabaseImport._read_mapping_table_from_excel_file) as mocked_read:
                mocked_read.return_value = mocked_df
                sut.import_mapping_table(
                    "mocked_table_name",
                    "mocked_left_id_name",
                    "mocked_right_id_name",
                    "mocked_data_directory",
                    "mocked_target_table_name",
                )
                mocked_read.assert_called_once()

                mocked_df.to_sql.assert_called_once()

        @patch(sqlite3.connect)
        @patch(DatabaseImport._delete_table_if_exists)
        @patch(DatabaseImport._query_to_create_mapping_table)
        def test_without_target_table_name(self, sut):
            mocked_df = Mock()
            mocked_df.to_sql = Mock()

            with patch(DatabaseImport._read_mapping_table_from_excel_file) as mocked_read:
                mocked_read.return_value = mocked_df
                sut.import_mapping_table(
                    "mocked_table_name",
                    "mocked_left_id_name",
                    "mocked_right_id_name",
                    "mocked_data_directory",
                    None,
                )
                mocked_read.assert_called_once()

                mocked_df.to_sql.assert_called_once()

    @patch(
        DatabaseImport._read_mapping_table_from_excel_file,
        "mocked_result",
    )
    def test_read_mapping_table(self, sut):
        result = sut.read_mapping_table(
            "mocked_table_name",
            "mocked_source_column_name",
            "mocked_target_id_name",
            "mocked_data_directory",
        )
        assert result == "mocked_result"

    def test_validate_table(self, sut):
        sut._table_validator = Mock()
        sut._table_validator.validate = Mock("mocked_result")

        mocked_table = Mock()
        result = sut.validate_table(mocked_table, "mocked_missing_entries")
        assert result == "mocked_result"

    @patch(sqlite3.connect)
    def test_write_to_sqlite(self, sut):
        sut._table_validator.validate = Mock()

        mocked_table = Mock()

        with patch(DatabaseImport._recreate_data_table) as mocked_recreate:
            sut.write_to_sqlite(mocked_table, "mocked_table_name")

            mocked_recreate.assert_called_once()


class TestPrivateApi:
    class TestCheckLabels:
        def test_with_white_spaces(self, sut):
            df = pandas.DataFrame(
                [
                    {"label": "  label_starting_with_whitespace"},
                ]
            )
            with raises(ValueError):
                sut._check_labels(df)

        def test_without_white_spaces(self, sut):
            df = pandas.DataFrame(
                [
                    {"label": "mocked_label"},
                ]
            )
            sut._check_labels(df)

        def test_with_nan_value(self, sut):
            df = pandas.DataFrame(
                [
                    {"label": float("NaN")},
                ]
            )
            with raises(ValueError):
                sut._check_labels(df)

    def test_delete_table_if_exists(self, sut):
        mocked_target_cursor = Mock()
        mocked_target_cursor.execute = Mock()

        sut._delete_table_if_exists(
            "mocked_table_name",
            mocked_target_cursor,
        )
        mocked_target_cursor.execute.assert_called_once()

    class TestDetermineColumnEntry:
        def test_for_year(self):
            target = "year"
            year = 2020
            value = -999
            result = DatabaseImport._determine_column_entry(
                "mocked_dictionary",
                target,
                year,
                value,
            )
            assert result == 2020

        def test_for_value(self):
            target = "value"
            year = 2020
            value = -999
            result = DatabaseImport._determine_column_entry(
                "mocked_dictionary",
                target,
                year,
                value,
            )
            assert result == -999

        def test_for_id_label(self):
            dictionary = {
                "id_region": (3, "foo"),
            }
            target = "id_region"
            year = 2020
            value = -999
            result = DatabaseImport._determine_column_entry(
                dictionary,
                target,
                year,
                value,
            )
            assert result == "foo"

    def test_key_column_names(self):
        id_column_names = ["id_foo", "id_unit", "id_baa"]
        result = DatabaseImport._key_column_names(id_column_names)
        assert result == ["id_foo", "id_baa"]

    class TestQueryToCreateIdTable:
        def test_with_optional_column_names(self, sut):
            mocked_optional_explicit_columns_that_will_be_unique = [
                "description",
            ]
            result = sut._query_to_create_id_table(
                "mocked_table_name",
                mocked_optional_explicit_columns_that_will_be_unique,
            )
            expected_query = (
                "CREATE TABLE `mocked_table_name` ("
                + "id integer PRIMARY KEY NOT NULL, "
                + "label text NOT NULL, "
                + "description text UNIQUE"
                + ")"
            )
            assert result == expected_query

        def test_without_optional_column_names(self, sut):
            result = sut._query_to_create_id_table(
                "mocked_table_name",
                None,
            )
            expected_query = (
                "CREATE TABLE `mocked_table_name` ("
                + "id integer PRIMARY KEY NOT NULL, "
                + "label text NOT NULL UNIQUE, "
                + "description text"
                + ")"
            )
            assert result == expected_query

    def test_query_to_create_mapping_table(self, sut):
        result = sut._query_to_create_mapping_table(
            "mocked_left_id_name",
            "mocked_right_id_name",
            "mocked_target_table_name",
        )
        expected_query = (
            "CREATE TABLE `mocked_target_table_name` ("
            + "id integer PRIMARY KEY NOT NULL, "
            + "mocked_left_id_name integer NOT NULL, "
            + "mocked_right_id_name integer NOT NULL, "
            + "FOREIGN KEY (mocked_left_id_name) REFERENCES mocked_left_id_name(id), "
            + "FOREIGN KEY (mocked_right_id_name) REFERENCES mocked_right_id_name(id)"
            + ")"
        )
        assert result == expected_query

    def test_read_id_table_from_exel_file(self, sut):
        mocked_df = Mock()
        mocked_df.__getitem__ = Mock("mocked_result")

        with patch_by_string("pandas.read_excel", mocked_df):
            result = sut._read_id_table_from_excel_file(
                "mocked_directory",
                "mocked_table_name",
            )

            assert result == "mocked_result"

    class TestREadIdTableFromDatabase:
        def mocked_database__init__(self, path):
            self._path = path  # pylint: disable=attribute-defined-outside-init
            self.id_table = Mock("mocked_table")  # pylint: disable=attribute-defined-outside-init

        @patch(Database.__init__, mocked_database__init__)
        def test_read_id_table_from_database(self, sut):
            result = sut._read_id_table_from_database("mocked_database_path", "table_name")
            assert result == "mocked_table"

    # pylint: disable=attribute-defined-outside-init
    def mocked_mapping_table_init(self, df, name):
        self._data_frame = df
        self._name = name

    @patch(
        MappingTable.__init__,
        mocked_mapping_table_init,
    )
    def test_read_mapping_table_from_exel_file(self, sut):
        mocked_df = Mock()
        mocked_df.__getitem__ = Mock("mocked_df")

        with patch_by_string("pandas.read_excel", mocked_df):
            result = sut._read_mapping_table_from_excel_file(
                "mocked_table_name",
                "mocked_source_column_name",
                "mocked_target_id_name",
                "mocked_data_directory",
            )

            assert result._name == "mocked_table_name"

    @patch(
        DatabaseImport._key_column_names,
        ["mocked_key_column"],
    )
    def test_recreate_data_table(self, sut):
        mocked_cursor = Mock()
        mocked_cursor.execute = Mock()

        mocked_connection = Mock()
        mocked_connection.cursor = Mock(mocked_cursor)

        mocked_table = Mock()
        mocked_table.column_names = (
            ["mocked_id_column"],
            ["mocked_year_column"],
            ["mocked_value_column"],
        )

        sut._recreate_data_table(
            "mocked_table_name",
            mocked_table,
            mocked_connection,
        )

        mocked_cursor.execute.assert_called()

    class TestCheckIfTableExists:
        @patch(DatabaseImport._table_exists, False)
        def test_without_table(self, sut):
            with raises(ValueError):
                sut._check_if_table_exists("mocked_table_name")

        @patch(DatabaseImport._table_exists, True)
        def test_with_table(self, sut):
            sut._check_if_table_exists("mocked_table_name")

    class TestTableExists:
        @patch(sqlite3.connect, patch_sqlite_connect(["mocked_table_info"]))
        def test_with_table(self, sut):
            result = sut._table_exists("mocked_table_name")
            assert result

        @patch(sqlite3.connect, patch_sqlite_connect([]))
        def test_without_table(self, sut):
            result = sut._table_exists("mocked_table_name")
            assert not result
