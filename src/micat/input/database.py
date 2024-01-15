# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import sqlite3

from micat.input.database_exception import DatabaseException
from micat.log.logger import Logger
from micat.table.id_table import IdTable
from micat.table.mapping_table import MappingTable
from micat.table.table import Table
from micat.table.value_table import ValueTable


class Database:
    def __init__(self, database_path):
        self.database_path = database_path

    def id_table(self, id_table_name):
        query = 'SELECT *  FROM `' + id_table_name + '`'
        where_clause = {}
        json_data = self._data_query(query, where_clause)
        id_table = IdTable.from_json(json_data, id_table_name)
        return id_table

    def json_string(self, query_string, where_clause):
        # logger = Logger(True)
        # logger.start_timer()

        data = self._data_query(query_string, where_clause)

        # logger.info_elapsed_time('Time after query "' + query_string + '": ')

        json_string = json.dumps(data)

        # logger.info_elapsed_time('Time after conversion: ')

        return json_string

    def mapping_table(self, mapping_table_name):
        query = 'SELECT *  FROM `' + mapping_table_name + '`'
        where_clause = {}
        json_data = self._data_query(query, where_clause)
        mapping_table = MappingTable.from_json(json_data, mapping_table_name)
        return mapping_table

    def query(self, query_string, where_clause):
        json_data = self._data_query(query_string, where_clause)
        headers = json_data['headers']
        if 'value' in headers:
            table = ValueTable.from_json(json_data, where_clause)
        else:
            table = Table.from_json(json_data, where_clause)
        return table

    def table(self, table_name, where_clause):
        query = 'SELECT * FROM `' + table_name + '`'
        return self.query(query, where_clause)

    @staticmethod
    def _append_where_clause(query_string, where_clause):
        if where_clause:
            if len(where_clause) > 0:
                query_string += ' WHERE '
                conditions = []
                for key, string_value in where_clause.items():
                    condition = Database._create_condition(key, string_value)
                    conditions.append(condition)

                query_string += ' AND '.join(conditions)

        return query_string

    @staticmethod
    def _create_condition(key, string_value):
        if isinstance(string_value, list):
            or_condition = Database._create_or_condition(key, string_value)
            return or_condition
        elif string_value[0] == '[':
            or_values = string_value[1:-1].replace(' ', '').split(',')
            or_condition = Database._create_or_condition(key, or_values)
            return or_condition
        else:
            condition = key + '=' + string_value
            return condition

    @staticmethod
    def _create_or_condition(key, values):
        conditions = []
        for value in values:
            condition = key + '=' + str(value)
            conditions.append(condition)
        return '(' + ' or '.join(conditions) + ')'

    def _data_query(self, query_string, where_clause):
        query_string = self._append_where_clause(query_string, where_clause)
        query_string = query_string.replace('WHERE LIMIT=', 'LIMIT ')
        try:
            with sqlite3.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(query_string)
                headers = list(map(lambda entries: entries[0], cursor.description))
                rows = cursor.fetchall()
                if len(rows) < 1:
                    Logger.warn('Fetched empty table with query: ' + query_string)
                data = {
                    'headers': headers,
                    'rows': rows,
                }
        except Exception as exception:  # pylint: disable=broad-except
            Logger.error(exception)
            message = 'Could not query database for ' + query_string
            raise IOError(message, exception) from exception
        if len(data['rows']) == 0:
            raise DatabaseException(f'Fetching data with "{query_string}" did not return any results.')
        return data
