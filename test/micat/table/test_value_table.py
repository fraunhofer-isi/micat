# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

import numpy as np
import pandas as pd

from micat.series.annual_series import AnnualSeries
from micat.table.abstract_table import AbstractTable
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch, raises


def mocked_data_frame():
    data_frame = Mock()
    data_frame.set_index = Mock()
    data_frame.columns = ['mocked_column']
    data_frame.empty = False
    return data_frame


class TestPublicApi:
    @patch(
        AbstractTable._construct_data_frame,
        Mock(mocked_data_frame()),
    )
    def test_construction(self):
        value_table = ValueTable(mocked_data_frame())
        data_frame = value_table._data_frame
        assert data_frame.columns == ['mocked_column']

    @patch(Table.concat)
    @patch(ValueTable._create, 'mocked_result')
    def test_concat(self):
        result = ValueTable.concat(['mocked_value_table', 'another_mocked_value_table'])
        assert result == 'mocked_result'

    def test_from_index(self):
        table = Table([{'id_foo': 1, 'id_baa': 2, '2000': 33, '2020': 66}])
        result = ValueTable.from_index(table)
        assert result['value'][1, 2] == 1

    @patch(
        ValueTable._data_frame_from_json,
        'mocked_data_frame',
    )
    @patch(
        ValueTable._drop_if_exists,
        'mocked_data_frame',
    )
    @patch(
        ValueTable._create,
        'mocked_result',
    )
    class TestFromJson:
        def test_with_id_region(self):
            where_clause = {'id_region': 1}
            result = ValueTable.from_json('mocked_json', where_clause)
            assert result == 'mocked_result'

        def test_without_id_region(self):
            result = ValueTable.from_json('mocked_json')
            assert result == 'mocked_result'

    class TestMul:
        def test_value_table_times_annual_series(self):
            value_table = ValueTable(
                [
                    {'id_foo': 1, 'value': 1},
                    {'id_foo': 2, 'value': 2},
                ]
            )

            annual_series = AnnualSeries({'2010': 10, '2020': 20})

            result = value_table * annual_series

            assert result['2010'][1] == 10
            assert result['2010'][2] == 20
            assert result['2020'][1] == 20
            assert result['2020'][2] == 40

        def test_value_table_times_value(self):
            value_table = ValueTable(
                [
                    {'id_foo': 1, 'value': 1},
                    {'id_foo': 2, 'value': 2},
                ]
            )
            value = 2
            result = value_table * value

            assert result['value'][1] == 2
            assert result['value'][2] == 4

    def test_years(self):
        value_table = ValueTable([{'id_foo': 1, 'value': 1}])
        result = value_table.years
        assert result is None


class TestPrivateAPI:
    def test_convert_single_row_reduction_result(self):
        sut = ValueTable([{'id_foo': 1, 'value': 1}], 'mocked_name')
        single_row_data_frame = pd.DataFrame([{'id_foo': 1, 'value': 10}])
        result = sut._convert_single_row_reduction_result(single_row_data_frame)
        assert result == 10

    def test_create(self):
        data_array = [{'id_foo': 1, 'value': 1}]
        result = ValueTable._create(data_array)
        assert isinstance(result, ValueTable)

    mocked_table = Mock()
    mocked_table.sort = Mock('mocked_result')

    @patch(Table._fix_id_column_order_after_multiplication)
    @patch(
        ValueTable._create,
        Mock(mocked_table),  # pylint: disable=undefined-variable
    )
    class TestJoinAndMultiplyValueTable:
        @patch(Table._validate_value_table_for_multiplication)
        @patch(Table._join_column_names, [])
        @patch(AbstractTable._contains_nan, False)
        def test_without_join_column_names(self):
            value_table = ValueTable([{'id_foo': 1, 'value': 1}], 'mocked_name')
            result = value_table._join_and_multiply_value_table(value_table)
            assert result == 'mocked_result'

        @patch(Table._validate_value_table_for_multiplication)
        @patch(Table._join_column_names, [])
        @patch(AbstractTable._contains_nan, True)
        def test_with_nan_entries(self):
            value_table = ValueTable([{'id_foo': 1, 'value': 1}], 'mocked_name')
            with raises(KeyError):
                value_table._join_and_multiply_value_table(value_table)

    class TestJoinAndMultiplyAnnualSeries:
        def test_with_nan(self):
            value_table = ValueTable([{'id_foo': 1, 'value': 1}])
            annual_series = AnnualSeries({'2010': 10, '2020': np.nan})
            with raises(ValueError):
                value_table._join_and_multiply_annual_series(annual_series)

        def test_normal_usage(self):
            value_table = ValueTable(
                [
                    {'id_foo': 1, 'value': 1},
                    {'id_foo': 2, 'value': 2},
                ]
            )
            annual_series = AnnualSeries({'2010': 10, '2020': 20})
            result = value_table._join_and_multiply_annual_series(annual_series)
            id_column_names, year_column_names, _ = result.column_names
            assert id_column_names == ['id_foo']
            assert year_column_names == ['2010', '2020']

            assert result['2010'][1] == 10
            assert result['2010'][2] == 20
            assert result['2020'][1] == 20
            assert result['2020'][2] == 40

    def test_multi_index_lookup_for_cell(self):
        value_table = ValueTable(
            [
                {'id_foo': 1, 'id_baa': 1, 'value': 10},
                {'id_foo': 1, 'id_baa': 2, 'value': 20},
            ]
        )

        index_value_or_tuple = (1, 2)
        index_order = ['id_foo', 'id_baa']

        result = value_table._multi_index_lookup_for_cell(
            index_value_or_tuple,
            'value',
            index_order,
        )
        assert result == 20
