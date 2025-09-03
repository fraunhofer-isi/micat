# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
import os
import sqlite3
import subprocess

import pandas as pd

from micat.data_import.table_validator import TableValidator
from micat.input.database import Database
from micat.log.logger import Logger
from micat.table.mapping_table import MappingTable
from micat.utils import file as file_utils


class DatabaseImport:
    def __init__(self, database_path, validation_database_path=None):
        self._database_path = database_path

        if validation_database_path is None:
            validation_database_path = database_path
        validation_database = Database(validation_database_path)
        self._table_validator = TableValidator(validation_database)

    @staticmethod
    def execute_import_scripts_in_folder(
        src_path,
        path_to_import_scripts=None,
        excluded_scripts=None,
    ):
        if path_to_import_scripts is None:
            path_to_import_scripts = os.getcwd()
        Logger.info(f"# Running import scripts in folder {path_to_import_scripts}")

        file_names = DatabaseImport._file_names(excluded_scripts, path_to_import_scripts)

        env = os.environ.copy()
        env["PYTHONPATH"] = src_path

        for file_name in file_names:
            Logger.info(
                "## Running file "
                + str(file_names.index(file_name) + 1)
                + " of "
                + str(len(file_names))
                + ": "
                + file_name
            )

            result = subprocess.run(
                "python " + file_name,
                shell=True,
                check=False,
                cwd=path_to_import_scripts,
                env=env,
            )
            if result.returncode != 0:
                message = f"Script {file_name} failed with return code {result.returncode}"
                raise RuntimeError(message)

    @staticmethod
    def _file_names(excluded_scripts, path_to_import_scripts):
        file_names = [
            os.path.join(path_to_import_scripts, file)
            for file in os.listdir(path_to_import_scripts)
            if os.path.isfile(os.path.join(path_to_import_scripts, file))
            and os.path.splitext(file)[-1].lower() == ".py"
        ]
        if excluded_scripts is not None:
            for excluded_script in excluded_scripts:
                if excluded_script in file_names:
                    file_names.remove(excluded_script)
        file_names.sort()
        return file_names

    @staticmethod
    def write_missing_entries_as_excel_file(  # pylint: disable=too-many-arguments, dangerous-default-value
        file_path,
        missing_entries,
        column_mapping,
        years,
        value,
        exclusions={},
    ):
        file_utils.delete_file_if_exists(file_path)
        file_utils.delete_file_if_exists("indexed_" + file_path)

        if len(missing_entries) > 0:
            rows = []
            for entry in missing_entries:
                if "year" in entry:
                    year = entry["year"]
                    row = DatabaseImport._create_missing_row(entry, column_mapping, year, value, exclusions)
                    if DatabaseImport._is_extra_row(row, rows):
                        rows.append(row)
                else:
                    for year in years:
                        row = DatabaseImport._create_missing_row(entry, column_mapping, year, value, exclusions)
                        if DatabaseImport._is_extra_row(row, rows):
                            rows.append(row)

            df = pd.DataFrame(rows)

            df.to_excel(file_path)

            column_names = list(column_mapping.keys())
            column_names.remove("FACTOR")
            df.set_index(column_names, inplace=True, verify_integrity=True)
            df.to_excel("indexed_" + file_path)

    @staticmethod
    def _create_missing_row(
        missing_entry,
        column_mapping,
        year,
        value,
        exclusions,
    ):
        row = {}
        for source_column_name, target_column_name in column_mapping.items():
            if target_column_name in exclusions:
                excluded_id = exclusions[target_column_name]
                id_entry = missing_entry[target_column_name]
                id_value = id_entry[0]
                if id_value == excluded_id:
                    return None
            row[source_column_name] = DatabaseImport._determine_column_entry(
                missing_entry,
                target_column_name,
                year,
                value,
            )
        return row

    @staticmethod
    def _is_extra_row(row, rows):
        if row is None:
            return False
        if row in rows:
            return False
        return True

    def append_to_sqlite(self, table, table_name):
        details = {
            "table": table_name,
        }
        self._table_validator.validate(table, details)
        self._check_if_table_exists(table_name)
        with sqlite3.connect(self._database_path) as connection:
            table.to_sql(table_name, connection, index_label="id", if_exists="append")

    def import_id_table(
        self,
        table_name,
        directory_or_database,
        optional_explicit_columns_that_will_be_unique=None,
    ):
        if directory_or_database.endswith(".sqlite"):
            df_or_table = self._read_id_table_from_database(directory_or_database, table_name)
        else:
            df_or_table = self._read_id_table_from_excel_file(directory_or_database, table_name)

        try:
            self._check_labels(df_or_table)
        except Exception as exception:
            Logger.error("Table " + table_name + " at " + directory_or_database + " contains NaN labels.")
            raise exception

        with sqlite3.connect(self._database_path) as target_connection:
            target_cursor = target_connection.cursor()
            self._delete_table_if_exists(table_name, target_cursor)

            extra_columns = []
            if "type" in df_or_table.columns:
                extra_columns.append(
                    {
                        "name": "type",
                        "type": "int",
                    }
                )

            create_query = self._query_to_create_id_table(
                table_name, optional_explicit_columns_that_will_be_unique, extra_columns
            )
            target_cursor.execute(create_query)

            df_or_table.to_sql(
                table_name,
                target_connection,
                index_label="id",
                if_exists="append",
            )

    # pylint: disable=too-many-arguments
    def import_mapping_table(
        self,
        table_name,
        source_column_name,
        target_id_name,
        data_directory,
        target_table_name=None,
    ):
        if not target_table_name:
            target_table_name = table_name

        mapping_table = self._read_mapping_table_from_excel_file(
            table_name,
            source_column_name,
            target_id_name,
            data_directory,
        )

        with sqlite3.connect(self._database_path) as target_connection:
            target_cursor = target_connection.cursor()

            self._delete_table_if_exists(target_table_name, target_cursor)

            create_query = self._query_to_create_mapping_table(source_column_name, target_id_name, target_table_name)
            target_cursor.execute(create_query)

            # hint: to_sql must not use if_exists='replace' but 'append'; otherwise table structure is lost
            mapping_table.to_sql(target_table_name, target_connection, index=False, if_exists="append")

    def read_mapping_table(
        self,
        table_name,
        source_column_name,
        target_id_name,
        data_directory,
    ):
        df = self._read_mapping_table_from_excel_file(
            table_name,
            source_column_name,
            target_id_name,
            data_directory,
        )
        return df

    def validate_table(self, table, table_name, missing_entries=[]):  # pylint: disable=dangerous-default-value
        sorted_table = table.sort()
        details = {
            "table": table_name,
        }
        missing_entries = self._table_validator.validate(sorted_table, details, missing_entries)
        return missing_entries

    def write_to_sqlite(self, table, table_name):
        sorted_table = table.sort()
        details = {"table": table_name}
        try:
            self._table_validator.validate(sorted_table, details)  # to be solved
        except AttributeError:
            pass
        with sqlite3.connect(self._database_path) as connection:
            DatabaseImport._recreate_data_table(table_name, sorted_table, connection)
            # hint: to_sql must not use if_exists='replace' but 'append'; otherwise table structure is lost
            sorted_table.to_sql(table_name, connection, index_label="id", if_exists="append")

    @staticmethod
    def _check_labels(df):
        label_values = df["label"].values
        for label in label_values:
            if not isinstance(label, str):
                if math.isnan(label):
                    raise ValueError("Labels must not contain NaN values.")
            string_label = str(label)
            stripped_label = string_label.strip()
            if stripped_label != string_label:
                message = (
                    "Labels must not start or end with whitespaces."
                    + 'Please fix the raw data entry in sharepoint "'
                    + string_label
                    + '"'
                )
                raise ValueError(message)

    @staticmethod
    def _delete_table_if_exists(table_name, target_cursor):
        delete_query = "DROP TABLE IF EXISTS `" + table_name + "`"
        target_cursor.execute(delete_query)

    @staticmethod
    def _determine_column_entry(dictionary, target, year, value):
        if target == "year":
            return year
        elif target == "value":
            return value
        else:
            id_entry = dictionary[target]
            id_label = id_entry[1]
            return id_label

    @staticmethod
    def _key_column_names(id_column_names):
        key_column_names = list(filter(lambda id_column_name: id_column_name != "id_unit", id_column_names))
        return key_column_names

    @staticmethod
    def _query_to_create_id_table(
        table_name,
        optional_explicit_columns_that_will_be_unique=None,
        extra_columns=None,
    ):
        unique_columns = ["label"]
        if optional_explicit_columns_that_will_be_unique is not None:
            unique_columns = optional_explicit_columns_that_will_be_unique

        create_query = (
            "CREATE TABLE `" + table_name + "` (" + "id integer PRIMARY KEY NOT NULL, " + "label text NOT NULL"
        )

        # In some special cases one might want to allow that
        # the label is not unique. Then you should pass ['description']
        # as unique columns instead of the default value ['label']
        if "label" in unique_columns:
            create_query += " UNIQUE"

        create_query += ", description text"
        if "description" in unique_columns:
            create_query += " UNIQUE"

        if extra_columns is not None:
            for extra_column in extra_columns:
                create_query += ", " + extra_column["name"] + " " + extra_column["type"]
                if extra_column.get("unique", False):
                    create_query += " UNIQUE"

        create_query += ")"
        return create_query

    @staticmethod
    def _query_to_create_mapping_table(
        left_id_name,
        right_id_name,
        target_table_name,
    ):
        create_query = (
            "CREATE TABLE `"
            + target_table_name
            + "` ("
            + "id integer PRIMARY KEY NOT NULL, "
            + left_id_name
            + " integer NOT NULL, "
            + right_id_name
            + " integer NOT NULL, "
            + "FOREIGN KEY ("
            + left_id_name
            + ") REFERENCES "
            + left_id_name
            + "(id), "
            + "FOREIGN KEY ("
            + right_id_name
            + ") REFERENCES "
            + right_id_name
            + "(id)"
            + ")"
        )
        return create_query

    @staticmethod
    def _read_id_table_from_excel_file(directory, table_name):
        excel_file_path = directory + "/" + table_name + ".xlsx"
        df = pd.read_excel(excel_file_path, index_col="id")
        default_columns = ["label", "description"]
        if "type" in df.columns:
            default_columns.append("type")
        df = df[default_columns]
        return df

    @staticmethod
    def _read_id_table_from_database(database_path, table_name):
        sqlite_database = Database(database_path)
        table = sqlite_database.id_table(table_name)
        return table

    @staticmethod
    def _read_mapping_table_from_excel_file(
        table_name,
        source_column_name,
        target_id_name,
        data_directory,
    ):
        file_path = data_directory + "/" + table_name + ".xlsx"
        df = pd.read_excel(file_path, index_col="id")
        df = df[[source_column_name, target_id_name]]
        return MappingTable(df, table_name)

    @staticmethod
    def _recreate_data_table(table_name, table, connection):
        id_column_names, year_column_names, value_column_names = table.column_names

        cursor = connection.cursor()

        delete_query = "DROP TABLE IF EXISTS `" + table_name + "`"
        cursor.execute(delete_query)

        create_query = "CREATE TABLE `" + table_name + "` (" + "id integer PRIMARY KEY NOT NULL, "

        for column_name in id_column_names:
            create_query += column_name + " integer NOT NULL, "

        for column_name in year_column_names:
            create_query += "`" + str(column_name) + "` real NOT NULL, "

        for column_name in value_column_names:
            create_query += "`" + str(column_name) + "` real NOT NULL, "

        for column_name in id_column_names:
            create_query += "FOREIGN KEY (" + column_name + ") REFERENCES " + column_name + "(id), "

        key_column_names = id_column_names  # table.key_column_names
        create_query += "UNIQUE (" + ", ".join(key_column_names) + ")"

        create_query += ")"

        cursor.execute(create_query)

    def _check_if_table_exists(self, table_name):
        if not self._table_exists(table_name):
            raise ValueError('Table "' + table_name + '" does not yet exist.')

    def _table_exists(self, table_name):
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table_name + "'"
            cursor.execute(query)
            result = cursor.fetchall()
            table_exists = len(result) > 0
            return table_exists
