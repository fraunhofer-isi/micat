# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable = protected-access
import sqlite3

import pandas as pd

from micat.log.logger import Logger
from micat.table.abstract_table import AbstractTable
from micat.table.table import Table
from micat.test_utils.assertion import falsy, truthy
from micat.test_utils.isi_mock import Mock, fixture, patch, raises


@fixture(name='data_frame')
def data_frame_fixture():
    data_frame = Mock(name='mocked_data_frame')
    data_frame.columns = ['mocked_column']
    data_frame.empty = False
    return data_frame


@fixture(name='sut')
def sut_fixture(data_frame):
    return AbstractTable(data_frame)


class TestPublicApi:
    class TestConstruction:
        def test_with_empty_data_frame(self):
            data_frame = pd.DataFrame()
            with raises(ValueError):
                AbstractTable(data_frame)

        def test_with_non_empty_data_frame(self, data_frame, sut):
            assert sut._data_frame == data_frame

    @patch(AbstractTable._column_names, 'mocked_column_names')
    def test_column_names(self, sut):
        result = sut.column_names
        assert result == 'mocked_column_names'

    def test_iterrows(self, sut):
        from micat.series.annual_series import (  # pylint: disable=import-outside-toplevel
            AnnualSeries,
        )

        sut._data_frame = pd.DataFrame(
            [
                {'id_foo': 1, '2000': 1},
                {'id_foo': 2, '2000': 2},
            ]
        )
        sut._data_frame.set_index(['id_foo'], inplace=True)
        result = sut.iterrows()
        _index, series = next(result)
        assert isinstance(series, AnnualSeries)
        assert series['2000'] == 1

    def test_set_values_by_index_table(self, sut):
        sut._data_frame = pd.DataFrame(
            [
                {'id_foo': 1, 'id_baa': 1, '2000': 1},
                {'id_foo': 1, 'id_baa': 2, '2000': 2},
            ]
        )
        sut._data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

        indices_of_values_to_be_replaced = Table(
            [
                {'id_foo': 1, '2000': (1, 2)},
            ]
        )
        index_order = ['id_foo', 'id_baa']
        value = 0
        result = sut.set_values_by_index_table(
            indices_of_values_to_be_replaced,
            index_order,
            value,
        )
        assert result['2000'][1, 2] == 0

    def test_to_string(self, sut):
        sut._data_frame.to_string = Mock('mocked_string_result')
        string_result = sut.to_string()
        assert string_result == 'mocked_string_result'

    class TestToSqL:
        @patch(AbstractTable._enable_foreign_key_constraints)
        def test_normal_usage(self, sut):
            sut._data_frame.reset_index = Mock(sut._data_frame)
            sut._data_frame.to_sql = Mock()
            sut.to_sql('mocked_table_name', 'mocked_connection')
            sut._data_frame.to_sql.assert_called_once()

        @staticmethod
        def raise_integrity_error():
            raise sqlite3.IntegrityError('foo')

        @patch(AbstractTable._enable_foreign_key_constraints)
        @patch(Logger.warn)
        def test_with_unique_constraint_issue(self, sut):
            sut._data_frame.reset_index = Mock(sut._data_frame)
            sut._data_frame.to_sql = lambda x, y: self.raise_integrity_error()
            with raises(sqlite3.IntegrityError):
                sut.to_sql('mocked_table_name', 'mocked_connection')

    def test_to_data_frame(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.copy = Mock()
        result = sut.to_data_frame()
        assert result
        sut._data_frame.copy.assert_called_once()

    def test_a_preview(self, data_frame, sut):
        assert sut.a_preview == data_frame

    def test_index(self, sut):
        sut._data_frame.index = 'mocked_index'
        result = sut.index
        assert result == 'mocked_index'

    def test_columns(self, sut):
        columns = sut.columns
        assert isinstance(columns, list)
        assert columns[0] == 'mocked_column'

    def test__repr__(self, sut):
        sut._data_frame.__repr__ = Mock('mocked__repr__')
        string_result = repr(sut)
        assert string_result == 'mocked__repr__'

    class TestGetItem:
        @staticmethod
        def data_frame():
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 33, '2020': 34},
                    {'id_foo': 1, 'id_baa': 1, '2000': 35, '2020': 36},
                ]
            )
            data_frame.set_index(['id_foo', 'id_baa'], inplace=True)
            return data_frame

        def test__getitem__for_series(self):
            data_frame = self.data_frame()
            table = AbstractTable(data_frame)
            result = table['2000']
            assert isinstance(result, pd.Series)

        @patch(AbstractTable._create, 'mocked_result')
        def test__getitem__for_table(self):
            data_frame = self.data_frame()
            table = AbstractTable(data_frame)
            result = table[data_frame['2000'] > 33]
            assert result == 'mocked_result'

    def test__setitem__(self):
        data_frame = pd.DataFrame(
            [
                {'id_foo': 1, '2000': 1},
            ]
        )
        table = AbstractTable(data_frame)
        table['2000'] = 3
        data_frame = table._data_frame
        assert data_frame['2000'][0] == 3

    @patch(AbstractTable._validate_tables_for_add_operation)
    class TestAdd:
        def test_table_plus_table(self):
            left_frame = pd.DataFrame([{'a': 1, 'b': 2}])
            left_table = AbstractTable(left_frame)

            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = AbstractTable(right_frame)

            result = left_table + right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == 11
            assert data_frame['b'][0] == 22

        def test_value_plus_table(self):
            left_value = 4

            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = AbstractTable(right_frame)

            result = left_value + right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == 14
            assert data_frame['b'][0] == 24

        def test_table_plus_value(self):
            left_frame = pd.DataFrame([{'a': 1, 'b': 2}])
            left_table = AbstractTable(left_frame)

            right_value = 4

            result = left_table + right_value

            data_frame = result._data_frame
            assert data_frame['a'][0] == 5
            assert data_frame['b'][0] == 6

    class TestDel:
        def test_with_value_column(self):
            data_frame = pd.DataFrame([{'id_measure': 1, 'id_subsector': 1, '2000': 2, '2020': 3}])
            data_frame.set_index(['id_measure', 'id_subsector'], inplace=True)
            table = AbstractTable(data_frame)
            del table['2000']
            assert table.columns == ['2020']

        def test_with_index_column(self):
            data_frame = pd.DataFrame([{'id_measure': 1, 'id_subsector': 1, '2000': 2, '2020': 3}])
            data_frame.set_index(['id_measure', 'id_subsector'], inplace=True)
            table = AbstractTable(data_frame)
            del table['id_subsector']
            index_column_names = table.index.names

            assert index_column_names == ['id_measure']

        def test_with_unknown_column(self):
            data_frame = pd.DataFrame([{'id_measure': 1, 'id_subsector': 1, '2000': 2, '2020': 3}])
            data_frame.set_index(['id_measure', 'id_subsector'], inplace=True)
            table = AbstractTable(data_frame)
            with raises(KeyError):
                del table['id_unknown']

    def test__invert__(self):
        data_frame = pd.DataFrame(
            [
                {'id_foo': 3, '2000': True},
            ]
        )
        data_frame.set_index(['id_foo'], inplace=True)
        table = AbstractTable(data_frame)
        result = ~table
        assert ~result['2000'][3]

    def test__neg__(self):
        data_frame = pd.DataFrame(
            [
                {'id_foo': 3, '2000': 1},
            ]
        )
        data_frame.set_index(['id_foo'], inplace=True)
        table = AbstractTable(data_frame)
        result = -table
        assert result['2000'][3] == -1

    class TestSub:
        def test_table_minus_table(self):
            left_frame = pd.DataFrame([{'a': 1, 'b': 2}])
            left_table = AbstractTable(left_frame)

            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = AbstractTable(right_frame)

            result = left_table - right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == -9
            assert data_frame['b'][0] == -18

        def test_value_minus_table(self):
            left_value = 4

            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = AbstractTable(right_frame)

            result = left_value - right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == -6
            assert data_frame['b'][0] == -16

        def test_table_minus_value(self):
            left_frame = pd.DataFrame([{'a': 1, 'b': 2}])
            left_table = AbstractTable(left_frame)

            right_value = 4

            result = left_table - right_value

            data_frame = result._data_frame
            assert data_frame['a'][0] == -3
            assert data_frame['b'][0] == -2

        def test_invalid_subtraction(self):
            left_value = 4

            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = AbstractTable(right_frame)
            right_table._data_frame = pd.Series([1, 2], index=['2000', '2020'])

            with raises(ValueError):
                left_value - right_table  # pylint: disable=pointless-statement

    def test_less_than(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 2}])
        right_table = AbstractTable(right_frame)

        result = left_table < right_table

        assert truthy(result['a'][0])
        assert falsy(result['b'][0])

    def test_greater_than(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 2}])
        right_table = AbstractTable(right_frame)

        result = left_table > right_table

        assert falsy(result['a'][0])
        assert truthy(result['b'][0])

    def test_less_or_equal(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
        right_table = AbstractTable(right_frame)

        result = left_table <= right_table

        assert truthy(result['a'][0])
        assert truthy(result['b'][0])

    def test_greater_or_equal(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
        right_table = AbstractTable(right_frame)

        result = left_table >= right_table

        assert falsy(result['a'][0])
        assert truthy(result['b'][0])

    def test_equal(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
        right_table = AbstractTable(right_frame)

        result = left_table == right_table

        assert falsy(result['a'][0])
        assert truthy(result['b'][0])

    def test_not_equal(self):
        left_frame = pd.DataFrame([{'a': 1, 'b': 20}])
        left_table = AbstractTable(left_frame)

        right_frame = pd.DataFrame([{'a': 10, 'b': 20}])
        right_table = AbstractTable(right_frame)

        result = left_table != right_table

        assert truthy(result['a'][0])
        assert falsy(result['b'][0])


class TestPrivateApi:
    def mocked__init__(self, data_frame):
        self._data_frame = data_frame  # pylint: disable=attribute-defined-outside-init

    class TestApplyMappingTable:
        @patch(
            AbstractTable._handle_unmapped_entries,
            lambda df, mapping: df,
        )
        def test_with_existing_source_column(self):
            data_frame = pd.DataFrame([{'source': 2}])
            mocked_mapping_table = Mock()
            mocked_mapping_table._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'source': 2, 'target': 4},
                ]
            )
            mocked_mapping_table.source_column = 'source'
            result = AbstractTable._apply_mapping_table(
                data_frame,
                mocked_mapping_table,
            )
            assert result['target'][0] == 4

        @patch(
            AbstractTable._handle_unmapped_entries,
            lambda df, mapping: df,
        )
        def test_without_source_column(self):
            data_frame = pd.DataFrame([{'foo': 2}])
            mocked_mapping_table = Mock()
            mocked_mapping_table._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'source': 2, 'target': 4},
                ]
            )
            mocked_mapping_table.source_column = 'source'
            with raises(KeyError):
                AbstractTable._apply_mapping_table(
                    data_frame,
                    mocked_mapping_table,
                )

    class TestApplyMappingTableReversely:
        @patch(
            AbstractTable._handle_unmapped_reverse_entries,
            lambda df, mapping: df,
        )
        def test_with_existing_source_column(self):
            data_frame = pd.DataFrame([{'target': 4}])
            mocked_mapping_table = Mock()
            mocked_mapping_table._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'source': 2, 'target': 4},
                ]
            )
            mocked_mapping_table.target_column = 'target'
            result = AbstractTable._apply_mapping_table_reversely(
                data_frame,
                mocked_mapping_table,
            )
            assert result['source'][0] == 2

        @patch(
            AbstractTable._handle_unmapped_reverse_entries,
            lambda df, mapping: df,
        )
        def test_without_source_column(self):
            data_frame = pd.DataFrame([{'foo': 2}])
            mocked_mapping_table = Mock()
            mocked_mapping_table._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'source': 2, 'target': 4},
                ]
            )
            mocked_mapping_table.source_column = 'source'
            with raises(KeyError):
                AbstractTable._apply_mapping_table_reversely(
                    data_frame,
                    mocked_mapping_table,
                )

    class TestCheckForDummyValuesAndRemoveThem:
        @patch(AbstractTable._contains, True)
        @patch(Logger.info)
        def test_contains_empty_value(self):
            with patch(AbstractTable._remove_rows_containing_value, 'mocked_result') as mocked_remove:
                result = AbstractTable._check_for_dummy_values_and_remove_them(
                    'mocked_df',
                    'mocked_dummy_value',
                    'mocked_table_name',
                )
                assert result == 'mocked_result'
                mocked_remove.assert_called()

        @patch(AbstractTable._contains, False)
        def test_does_not_contains_empty_value(self):
            with patch(AbstractTable._remove_rows_containing_value, 'mocked_result') as mocked_remove:
                result = AbstractTable._check_for_dummy_values_and_remove_them(
                    'mocked_df',
                    'mocked_dummy_value',
                    'mocked_table_name',
                )
                assert result == 'mocked_df'
                mocked_remove.assert_not_called()

    def test_column_names(self):
        data_frame = pd.DataFrame(
            [
                {
                    'id_foo': 1,
                    'id_baa': 2,
                    '2000': 1,
                    '2020': 2,
                }
            ]
        )
        id_column_names, year_column_names, value_column_names = AbstractTable._column_names(data_frame)
        assert id_column_names == ['id_foo', 'id_baa']
        assert year_column_names == ['2000', '2020']
        assert not value_column_names

    @patch(AbstractTable.__init__, mocked__init__)
    def test_create(self):
        result = AbstractTable._create('mocked_data_frame_or_array')
        assert result._data_frame == 'mocked_data_frame_or_array'

    class TestConstructDataFrame:
        def test_with_data_frame(self):
            data_frame = pd.DataFrame([{'foo': 11}])
            result = AbstractTable._construct_data_frame(data_frame)
            assert result['foo'][0] == 11

        def test_with_array(self):
            array = [{'foo': 11}]
            result = AbstractTable._construct_data_frame(array)
            assert result['foo'][0] == 11

    class TestContainsNaN:
        def test_with_nan(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': float('NaN')}])
            result = AbstractTable._contains_nan(data_frame)
            assert result

        def test_without_nan(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': 20}])
            result = AbstractTable._contains_nan(data_frame)
            assert not result

    class TestContainsObject:
        def test_with_object(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': object}])
            result = AbstractTable._contains_object(data_frame)
            assert result

        def test_without_object(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': 20}])
            result = AbstractTable._contains_object(data_frame)
            assert not result

    class TestContains:
        def test_with_value(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': 88}])
            result = AbstractTable._contains(data_frame, 88)
            assert result

        def test_without_value(self):
            data_frame = pd.DataFrame([{'foo': 1, '2000': 20}])
            result = AbstractTable._contains(data_frame, 88)
            assert not result

    class TestDataFrameFromJson:
        def test_non_empty_rows(self):
            custom_json = {
                'headers': ['id_foo', 'id_baa', '2000'],
                'rows': [
                    [1, 1, 33],
                    [1, 2, 34],
                ],
            }
            with patch(Logger.warn) as mocked_warn:
                data_frame = AbstractTable._data_frame_from_json(custom_json)
                mocked_warn.assert_not_called()

                columns = list(data_frame.columns)
                assert columns == ['id_foo', 'id_baa', '2000']

                series_2000 = data_frame['2000']
                first_value = series_2000[0]
                assert first_value == 33

        def test_empty_rows(self):
            custom_json = {
                'headers': ['id_foo', 'id_baa', '2000'],
                'rows': [],
            }
            with patch(Logger.warn) as mocked_warn:
                data_frame = AbstractTable._data_frame_from_json(custom_json)
                mocked_warn.assert_called_once()

                columns = list(data_frame.columns)
                assert columns == ['id_foo', 'id_baa', '2000']

                series_2000 = data_frame['2000']

                assert len(series_2000) == 0

    def test_enable_foreign_key_constraints(self):
        mocked_cursor = Mock()
        mocked_cursor.execute = Mock()

        connection = Mock()
        connection.cursor = Mock(mocked_cursor)

        AbstractTable._enable_foreign_key_constraints(connection)

        mocked_cursor.execute.assert_called_once()

    class TestHandleUnmappedEntries:
        def test_without_unmapped_entries(self):
            data_frame = pd.DataFrame([{'source': 2, 'value': 2}])

            mocked_mapping_table = Mock()
            mocked_mapping_table.source_column = 'source'
            mocked_mapping_table.source_values = [2]

            result = AbstractTable._handle_unmapped_entries(
                data_frame,
                mocked_mapping_table,
            )
            assert result['source'][0] == 2
            assert result['value'][0] == 2

        @patch(Logger.warn)
        def test_with_unmapped_entries(self):
            data_frame = pd.DataFrame(
                [
                    {'source': 1, 'value': 1},
                    {'source': 2, 'value': 2},
                ]
            )

            mocked_mapping_table = Mock()
            mocked_mapping_table.source_column = 'source'
            mocked_mapping_table.source_values = [2, 3]

            result = AbstractTable._handle_unmapped_entries(
                data_frame,
                mocked_mapping_table,
            )
            assert len(result) == 1
            assert result['source'][1] == 2

    class TestHandleUnmappedReversedEntries:
        def test_without_unmapped_entries(self):
            data_frame = pd.DataFrame([{'target': 2, 'value': 2}])

            mocked_mapping_table = Mock()
            mocked_mapping_table.target_column = 'target'
            mocked_mapping_table.target_values = [2]

            result = AbstractTable._handle_unmapped_reverse_entries(
                data_frame,
                mocked_mapping_table,
            )
            assert result['target'][0] == 2
            assert result['value'][0] == 2

        @patch(Logger.warn)
        def test_with_unmapped_entries(self):
            data_frame = pd.DataFrame(
                [
                    {'target': 1, 'value': 1},
                    {'target': 2, 'value': 2},
                ]
            )

            mocked_mapping_table = Mock()
            mocked_mapping_table.target_column = 'target'
            mocked_mapping_table.target_values = [2, 3]

            result = AbstractTable._handle_unmapped_reverse_entries(
                data_frame,
                mocked_mapping_table,
            )
            assert len(result) == 1
            assert result['target'][1] == 2

    def test_is_indexed(self):
        data_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 2, '2000': 2000}])
        assert AbstractTable._is_indexed(data_frame) is False

        data_frame.set_index(['id_foo'], inplace=True)
        assert AbstractTable._is_indexed(data_frame) is True

    class TestOtherValue:
        def test_table(self, sut):
            other = AbstractTable._other_value(sut)
            assert other is sut._data_frame

        def test_abstract_series(self):
            from micat.series.abstract_series import (  # pylint: disable=import-outside-toplevel
                AbstractSeries,
            )

            series = pd.Series([1, 2], index=['2000', '2020'])
            other_series = AbstractSeries(series)
            other = AbstractTable._other_value(other_series)
            assert other is series

        def test_no_table(self):
            obj = {'foo': 1}
            other = AbstractTable._other_value(obj)
            assert other is obj

    def test_remove_rows_containing_value(self):
        data_frame = pd.DataFrame(
            [
                {'id': 1, 'value': 32},
                {'id': 2, 'value': 33},
            ]
        )

        result = AbstractTable._remove_rows_containing_value(data_frame, 32)

        assert len(result) == 1
        assert result['value'].values[0] == 33

    class TestCreateIndexEntry:
        def test_multi_index(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 1},
                    {'id_foo': 1, 'id_baa': 2, '2000': 2},
                ]
            )
            sut._data_frame = data_frame
            index_tuple = (2, 1)
            index_order = ['id_baa', 'id_foo']
            result = sut._create_index_entry(index_tuple, index_order)
            assert result[0] == 1
            assert result[1] == 2

        def test_single_index(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                    {'id_foo': 1, '2000': 2},
                ]
            )
            sut._data_frame = data_frame
            index_tuple = (2, 1)
            index_order = ['id_baa', 'id_foo']
            result = sut._create_index_entry(index_tuple, index_order)
            assert result == 1

    def test_fix_column_order_after_multiplication(self, sut):
        data_frame = pd.DataFrame([{'id_foo': 1, '2000': 1}])
        data_frame.set_index(['id_foo'], inplace=True)
        sut._data_frame = data_frame

        unordered_data_frame = pd.DataFrame(
            [
                {'id_baa': 1, 'id_foo': 1, '2000': 1},
                {'id_baa': 2, 'id_foo': 1, '2000': 2},
            ]
        )
        unordered_data_frame.set_index(['id_baa', 'id_foo'], inplace=True)
        result = sut._fix_column_order_after_multiplication(unordered_data_frame)
        index_column_names = result.index.names

        assert index_column_names == ['id_foo', 'id_baa']
        assert result['2000'][1, 2] == 2

    @patch(AbstractTable._multi_index_lookup_for_cell, 'mocked_cell_result')
    def test_multi_index_lookup_for_column(self, sut):
        column = pd.Series([1, 2])

        result = sut._multi_index_lookup_for_column(column, 'mocked_index_order')
        assert result[0] == 'mocked_cell_result'
        assert result[1] == 'mocked_cell_result'

    class TestMultiIndexLookupForCell:
        @patch(AbstractTable._create_index_entry, 'mocked_index_entry')
        def test_with_tuple(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 'mocked_index_entry', '2000': 11},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            index_value_or_tuple = (1, 2)
            column_name = '2000'
            index_order = ['id_foo', 'id_baa']
            result = sut._multi_index_lookup_for_cell(
                index_value_or_tuple,
                column_name,
                index_order,
            )
            assert result == 11

        def test_with_value(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 33, '2000': 11},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            index_value_or_tuple = 33
            column_name = '2000'
            index_order = ['id_foo', 'id_baa']
            result = sut._multi_index_lookup_for_cell(
                index_value_or_tuple,
                column_name,
                index_order,
            )
            assert result == 11

    @patch(print)
    class TestValidateTablesForAddOperation:
        def test_with_different_length(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                    {'id_foo': 2, '2000': 2},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            other_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                ]
            )
            other_frame.set_index(['id_foo'], inplace=True)

            with raises(KeyError):
                sut._validate_tables_for_add_operation(other_frame)

        def test_with_different_index(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            other_frame = pd.DataFrame(
                [
                    {'id_foo': 2, '2000': 1},
                ]
            )
            other_frame.set_index(['id_foo'], inplace=True)

            with raises(KeyError):
                sut._validate_tables_for_add_operation(other_frame)

        def test_with_same_index(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            other_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 2},
                ]
            )
            other_frame.set_index(['id_foo'], inplace=True)

            sut._validate_tables_for_add_operation(other_frame)

        @patch(print)
        def test_with_same_index_values(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, '2000': 1},
                    {'id_foo': 2, '2000': 2},
                ]
            )
            sut._data_frame.set_index(['id_foo'], inplace=True)

            other_frame = pd.DataFrame(
                [
                    {'id_foo': 2, '2000': 2},
                    {'id_foo': 1, '2000': 1},
                ]
            )
            other_frame.set_index(['id_foo'], inplace=True)

            sut._validate_tables_for_add_operation(other_frame)
