# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
from test_utils.mock import Mock, patch

from template import database_utils, mocks, validators

mocked_template_args = mocks.mocked_template_args()


def test_column_names():
    mocked_series = Mock()
    mocked_series.values = 'mocked_result'

    mocked_table = {
        'name': mocked_series,
    }

    mocked_database = Mock()
    mocked_database.query = Mock(mocked_table)

    result = database_utils.column_names(mocked_database, 'mocked_table_name')

    assert result == 'mocked_result'


@patch(database_utils._year_range, ['2020', '2021'])
@patch(database_utils._year_columns_filter, False)
def test_filter_column_names_by_id_mode():
    result = database_utils.filter_column_names_by_id_mode(['2020', '2021'], 1)
    assert isinstance(result, list)
    assert len(result) == 0


@patch(validators.min_year, 2020)
@patch(validators.max_year, 2030)
def test_year_range():
    result = database_utils._year_range(mocked_template_args['id_mode'])
    assert isinstance(result, list)
    assert len(result) == 11


def test_year_columns_filter():
    mocked_year_columns = ['mocked_column1', 'mocked_column2', '2020', '2021']
    assert database_utils._year_columns_filter('2020', mocked_year_columns)
    assert not database_utils._year_columns_filter('2022', mocked_year_columns)


class TestTable:
    def test_table_without_column_names_and_where(self):
        mocked_database = mocks.mocked_database()
        mocked_database.query = Mock('mocked_table')
        result = database_utils.table(mocked_database, 'mocked_table_name')
        assert result == 'mocked_table'

    def test_table_with_column_names_and_where(self):
        mocked_database = mocks.mocked_database()
        mocked_database.query = Mock('mocked_table')
        result = database_utils.table(
            mocked_database,
            'mocked_table_name',
            ['mocked_column1', 'mocked_column2'],
            {},
        )
        assert result == 'mocked_table'


@patch(database_utils.column_names)
@patch(database_utils.filter_column_names_by_id_mode)
@patch(database_utils.table, 'mocked_parameter_table')
def test_parameter_table():
    result = database_utils.parameter_table(
        'mocked_database',
        'mocked_id_mode',
        'mocked_table_name',
        'mocked_where_clause',
    )
    assert result == 'mocked_parameter_table'
