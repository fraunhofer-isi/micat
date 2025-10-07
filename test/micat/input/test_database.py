# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import sqlite3

import pytest

from micat.input.database import Database
from micat.input.database_exception import DatabaseException
from micat.log.logger import Logger
from micat.table.id_table import IdTable
from micat.table.mapping_table import MappingTable
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, call, patch, raises


@pytest.fixture(name="sut")
def fixture_sut():
    return Database('database_path_mock')


class TestPublicAPI:
    @patch(Database._data_query, 'mocked_json_data')
    @patch(IdTable.from_json, 'from_json')
    def test_id_table(self, sut):
        result = sut.id_table('mocked_query_string')
        assert result == 'from_json'

    class TestJsonString:
        def test_json_string(self, sut):
            dummy_data = {
                'headers': [],
                'rows': [],
            }
            sut._data_query = Mock(dummy_data)
            result = sut.json_string('SELECT * FROM table', 'where_clause_mock')
            assert result == '{"headers": [], "rows": []}'

    @patch(Database._data_query, 'mocked_json_data')
    @patch(MappingTable.from_json, 'from_json')
    def test_mapping_table(self, sut):
        result = sut.mapping_table('mocked_query_string')
        assert result == 'from_json'

    class TestQuery:
        @patch(
            Database._data_query,
            {'headers': ['id_foo', 'value']},
        )
        @patch(
            ValueTable.from_json,
            'mocked_result',
        )
        def test_with_value_table(self, sut):
            result = sut.query('mocked_query', 'mocked_where_clause')
            assert result == 'mocked_result'

        @patch(
            Database._data_query,
            {'headers': ['id_foo', '2000']},
        )
        @patch(Table.from_json, 'mocked_result')
        def test_with_table(self, sut):
            result = sut.query('mocked_query', 'mocked_where_clause')
            assert result == 'mocked_result'

    @patch(Database.query, 'mocked_result')
    def test_table(self, sut):
        result = sut.table('mocked_query_string', 'mocked_where_clause')
        assert result == 'mocked_result'


class TestPrivateAPI:
    class TestAppendWhereClause:
        def test_without_where_clause(self, sut):
            query = sut._append_where_clause('SELECT * FROM table', None)
            assert query == 'SELECT * FROM table'

        def test_empty_where_clause(self, sut):
            query = sut._append_where_clause('SELECT * FROM table', {})
            assert query == 'SELECT * FROM table'

        def test_normal_usage(self, sut):
            mocked_condition = Mock('mocked_condition')
            with patch(Database._create_condition, mocked_condition):
                query = sut._append_where_clause('SELECT * FROM table', {'id': '3', 'type': 'min'})
                assert query == 'SELECT * FROM table WHERE mocked_condition AND mocked_condition'

    class TestCreateCondition:
        def test_list(self, sut):
            _create_or_condition_mock = Mock('mocked_condition')
            with patch(Database._create_or_condition, _create_or_condition_mock) as patched__create_or_condition:
                condition = sut._create_condition('id_foo', [1, 2, 3])
                assert condition == 'mocked_condition'
                patched__create_or_condition.assert_has_calls(
                    [
                        call('id_foo', [1, 2, 3]),
                    ]
                )

        def test_string_list(self, sut):
            create_or_condition_mock = Mock('mocked_condition')
            with patch(Database._create_or_condition, create_or_condition_mock) as patched__create_or_condition:
                condition = sut._create_condition('id_foo', '[1, 2, 3]')
                assert condition == 'mocked_condition'
                patched__create_or_condition.assert_has_calls(
                    [
                        call('id_foo', ['1', '2', '3']),
                    ]
                )

        def test_single_value(self, sut):
            condition = sut._create_condition('id_foo', '3')
            assert condition == 'id_foo=3'

    def test_create_or_condition(self):
        query = Database._create_or_condition('id', [1, 2])
        assert query == '(id=1 or id=2)'

    class TestDataQuery:
        @patch(sqlite3.connect, Mock(Mock()))
        @patch(Logger.warn)
        def test_empty(self, sut):
            sut._append_where_clause = Mock('SELECT * FROM table WHERE 1')
            with pytest.raises(DatabaseException) as exception_info:
                sut._data_query('SELECT * FROM table', 'where_clause_mock')
                assert 'did not return any results' in exception_info.value.args[0]

        @staticmethod
        def mocked_connect(_self):
            mocked_connection = Mock()
            mocked_connection.__enter__ = Mock(mocked_connection)
            mocked_connection.__exit__ = Mock()
            mocked_cursor = Mock()
            mocked_cursor.fetchall = Mock(['mocked_row1', 'mocked_row2'])
            mocked_connection.cursor = Mock(mocked_cursor)
            return mocked_connection

        @patch(sqlite3.connect, mocked_connect)
        @patch(Logger.warn)
        def test_filled(self, sut):
            sut._append_where_clause = Mock('SELECT * FROM table WHERE 1')
            result = sut._data_query('SELECT * FROM table', 'where_clause_mock')
            assert list(result.keys()) == ['headers', 'rows']

        @patch(sqlite3.connect, 'invalid_connection')
        @patch(Logger.error)
        def test_error(self, sut):
            sut._append_where_clause = Mock('SELECT * FROM table WHERE 1')
            with raises(IOError):
                sut._data_query('SELECT * FROM table', 'where_clause_mock')
