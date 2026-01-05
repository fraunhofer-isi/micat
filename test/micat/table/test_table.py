# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
import numpy as np
import pandas as pd

from micat.log.logger import Logger
from micat.series.annual_series import AnnualSeries
from micat.table.abstract_table import AbstractTable
from micat.table.id_table import IdTable
from micat.table.table import Table
from micat.test_utils.isi_mock import (
    Mock,
    call,
    fixture,
    patch,
    patch_by_string,
    patch_property,
    raises,
)
from micat.utils import list as list_utils


def mocked_data_frame():
    data_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 2, '2000': 2000}])
    return data_frame


@fixture(name='sut')
def sut_fixture():
    with patch(AbstractTable._construct_data_frame, mocked_data_frame()):
        return Table('mocked_data_frame')


# noinspection PyProtectedMember
def assert_has_mocked_data_frame(table):
    data_frame = table._data_frame
    series2000 = data_frame['2000']
    assert series2000[1, 2] == 2000


# noinspection PyUnusedLocal
def mocked_table__init__(self, data_frame_or_array):  # pylint: disable=unused-argument
    self._data_frame = 'mocked_frame'  # pylint: disable=attribute-defined-outside-init


class TestPublicApi:
    class TestConstruction:
        @staticmethod
        def mocked_indexed_data_frame():
            data_frame = mocked_data_frame()
            data_frame_with_index = data_frame.set_index(['id_foo', 'id_baa'])
            return data_frame_with_index

        @staticmethod
        def mocked_data_frame_without_id_columns():
            data_frame = pd.DataFrame([{'foo': 1, 'baa': 2}])
            return data_frame

        @patch(AbstractTable._construct_data_frame, mocked_indexed_data_frame())
        def test_data_frame_with_index(self):
            with patch(Table._is_indexed, True) as mocked_is_indexed:
                table = Table('mocked_data_frame')
                mocked_is_indexed.assert_called_once()
                assert_has_mocked_data_frame(table)

        @patch(AbstractTable._construct_data_frame, mocked_data_frame())
        @patch(Table._column_names, (['id_foo', 'id_baa'], ['2000'], []))
        def test_data_frame_without_index_and_with_id_columns(self):
            with patch(Table._is_indexed, False) as mocked_is_indexed:
                table = Table('mocked_data_frame')
                mocked_is_indexed.assert_called_once()
                assert_has_mocked_data_frame(table)

        @patch(
            AbstractTable._construct_data_frame,
            mocked_data_frame_without_id_columns(),
        )
        @patch(Table._column_names, ([], [], ['foo', 'baa']))
        def test_data_frame_without_index_and_without_id_columns(self):
            with patch(Table._is_indexed, False) as mocked_is_indexed:
                table = Table('mocked_data_frame')
                mocked_is_indexed.assert_called_once()
                data_frame = table._data_frame
                baa_series = data_frame['baa']
                assert baa_series[0] == 2

    def test_aggregate_to(self):
        table = Table(
            [
                {'id_foo': 1, 'id_baa': 1, '2000': 1},
                {'id_foo': 1, 'id_baa': 2, '2000': 1},
            ]
        )
        result = table.aggregate_to(['id_foo'])
        assert result['2000'][1] == 2

    def test_aggregate_by_mean_to(self):
        table = Table(
            [
                {'id_foo': 1, 'id_baa': 1, '2000': 1},
                {'id_foo': 1, 'id_baa': 2, '2000': 10},
            ]
        )
        result = table.aggregate_by_mean_to(['id_foo'])
        assert result['2000'][1] == 5.5

    def test_multi_index_lookup(self):
        table = Table(
            [
                {'id_final_energy_carrier': 1, 'id_partner_region': 1, '2000': 10, '2020': 20},
                {'id_final_energy_carrier': 1, 'id_partner_region': 2, '2000': 30, '2020': 10},
                {'id_final_energy_carrier': 2, 'id_partner_region': 1, '2000': 30, '2020': 10},
                {'id_final_energy_carrier': 2, 'id_partner_region': 2, '2000': 10, '2020': 20},
            ]
        )
        index_values = table.indices_for_max_annual_values(['id_final_energy_carrier'])
        result = table.multi_index_lookup(index_values, ['id_final_energy_carrier', 'id_partner_region'])
        assert result['2000'][1] == 30
        assert result['2000'][2] == 30

        assert result['2020'][1] == 20
        assert result['2020'][2] == 20

    def test_annual_mean(self, sut):
        result = sut.annual_mean()
        assert result.iloc[0] == 2000

    def test_astype(self, sut):
        sut._data_frame = pd.DataFrame([[1.33, 2.44]])
        result = sut.astype(int)
        assert isinstance(result.values[0][0], np.integer)

    class TestConcat:
        @patch(
            AbstractTable._other_value,
            mocked_data_frame(),
        )
        def test_normal_usage(self):
            result = Table.concat(['mocked_table', 'mocked_table'])
            assert len(result._data_frame) == 2

        def test_with_different_column_order(self):
            first = Table([{'id_a': 1, 'id_b': 1, 'value': 1}])
            second = Table([{'id_b': 2, 'id_a': 1, 'value': 10}])
            with raises(KeyError):
                Table.concat([first, second])

    def test_concat_years(self):
        left_table = Table([{'id_foo': 1, '2000': 0}])
        right_table = Table([{'id_foo': 1, '2010': 10}])

        result = Table.concat_years([left_table, right_table])
        id_column_names, year_column_names, _ = result.column_names
        assert id_column_names == ['id_foo']
        assert year_column_names == ['2000', '2010']
        assert result['2000'][1] == 0
        assert result['2010'][1] == 10

    @patch(AbstractTable._contains_nan, 'mocked_result')
    def test_contains_nan(self, sut):
        result = sut.contains_nan()
        assert result == 'mocked_result'

    def test_contains_non_nan(self, sut):
        result = sut.contains_non_nan()
        assert result

    @patch(AbstractTable._contains_object, 'mocked_result')
    def test_contains_object(self, sut):
        result = sut.contains_object()
        assert result == 'mocked_result'

    class TestContainsNegativeValues:
        def test_with_negative_values(self, sut):
            sut._data_frame = pd.DataFrame([{'value': -1}])
            result = sut.contains_negative_values()
            assert result

        def test_without_negative_values(self, sut):
            sut._data_frame = pd.DataFrame([{'value': 1}])
            result = sut.contains_negative_values()
            assert not result

    def test_copy(self, sut):
        sut._data_frame = pd.DataFrame([1, 2])
        result = sut.copy()
        assert result is not sut._data_frame

    @patch(Table.__init__, mocked_table__init__)
    def test_droplevel(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.droplevel = Mock()
        sut.droplevel(0)
        assert sut._data_frame.droplevel.called

    @patch(Table.__init__, mocked_table__init__)
    def test_drop(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.drop = Mock()
        sut.drop()
        assert sut._data_frame.drop.called

    @patch(Table.__init__, mocked_table__init__)
    def test_eq(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.eq = Mock()
        result = sut.eq(0)
        sut._data_frame.eq.assert_called_once()
        assert result._data_frame == 'mocked_frame'

    @staticmethod
    def mocked_data_frame_row():
        data_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 7, '2000': 3}])
        data_frame.set_index(['id_foo', 'id_baa'], inplace=True)
        return data_frame

    @patch.object(Table, 'column_names', (['id_foo', 'id_baa'], ['2000'], []))
    @patch(Table._parent_id_column_names, ['id_foo'])
    @patch(Table._index_entries, [(1)])
    @patch(Table._create_data_frame_with_single_row, mocked_data_frame_row())
    def test_fill_missing_values(self, sut):
        id_column_name = 'id_baa'
        id_values = [7]
        value = 0

        sut.fill_missing_values(
            id_column_name,
            id_values,
            value,
        )
        assert len(sut._data_frame) == 2

    def test_fill_missing_value(self, sut):
        key_entries = {
            'id_foo': 1,
            'id_baa': 3,
        }
        value = -999

        sut.fill_missing_value(key_entries, value)
        assert sut['2000'][1, 3] == -999

    class TestFillNa:
        @patch(Table.__init__, mocked_table__init__)
        def test_inplace(self, sut):
            sut._data_frame = Mock()
            sut._data_frame.fillna = Mock()

            sut.fillna(0, inplace=True)
            sut._data_frame.fillna.assert_called_once()

        @patch(Table.__init__, mocked_table__init__)
        def test_with_return_value(self, sut):
            sut._data_frame = Mock()
            sut._data_frame.fillna = Mock()

            result = sut.fillna(0)
            sut._data_frame.fillna.assert_called_once()
            assert result._data_frame == 'mocked_frame'

    class TestFillNaNValuesByExtrapolation:
        @patch_property(Table.column_names, (['id_foo'], ['2000', '2020', '2030'], []))
        def test_with_existing_negative_values(self, _mocked_column_names):
            table = Table([{'id_foo': 1, '2000': -1, '2020': 1, '2030': np.nan}])
            with patch(Logger.error) as mocked_error:
                with patch(Logger.warn) as mocked_warn:
                    table.fill_nan_values_by_extrapolation()
                    mocked_error.assert_called_once()
                    mocked_warn.assert_called_once()

        @patch_property(Table.column_names, (['id_foo'], ['2000', '2020', '2030'], []))
        def test_interpolation(self, _mocked_column_names):
            table = Table([{'id_foo': 1, '2000': 10, '2020': np.nan, '2030': 30}])
            extrapolated_table = table.fill_nan_values_by_extrapolation()
            assert extrapolated_table['2020'][1] == 20

        @patch_property(Table.column_names, (['id_foo'], ['2030', '2000', '2020'], []))
        def test_interpolation_with_unsorted_columns(self, _mocked_column_names):
            table = Table([{'id_foo': 1, '2030': 30, '2000': 10, '2020': np.nan}])
            extrapolated_table = table.fill_nan_values_by_extrapolation()
            assert extrapolated_table['2020'][1] == 20

    @patch(AbstractTable._data_frame_from_json, 'mocked_data_frame')
    @patch(Table.__init__, mocked_table__init__)
    class TestFromJson:
        def test_with_id_region(self):
            with patch(AbstractTable._drop_if_exists, 'mocked_data_frame') as mocked_drop:
                where_clause = {'id_region': 1}
                table = Table.from_json('mocked_json', where_clause)

                mocked_drop.assert_has_calls(
                    [
                        call('mocked_data_frame', 'id'),
                        call('mocked_data_frame', 'id_region'),
                        call('mocked_data_frame', 'id_unit'),
                    ]
                )
                assert table._data_frame == 'mocked_frame'

        def test_without_id_region(self):
            with patch(AbstractTable._drop_if_exists, 'mocked_data_frame') as mocked_drop:
                table = Table.from_json('mocked_json')

                mocked_drop.assert_has_calls(
                    [
                        call('mocked_data_frame', 'id'),
                        call('mocked_data_frame', 'id_unit'),
                    ]
                )
                assert table._data_frame == 'mocked_frame'

    @patch(Table._fix_integer_year_columns, mocked_data_frame())
    def test_from_json_string(self):
        json_string = '[{"id_foo": 1, "id_baa": 2, "2000": 2000, "details": {}}]'
        table = Table.from_json_string(json_string)
        assert_has_mocked_data_frame(table)

    @patch_by_string('pandas.read_excel', pd.DataFrame([{'id_foo': 1, '2000': 'mocked_value'}]))
    def test_read_excel(self):
        result = Table.read_excel('mocked_file_path')
        assert result['2000'][1] == 'mocked_value'

    def test_has_index_column(self, sut):
        result = sut.has_index_column('id_foo')
        assert result

    def test_index(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.index = 'mocked_index'
        result = sut.index
        assert result == 'mocked_index'

    class TestIndicesForMaxAnnualValues:
        def test_keeping_column_order(self):
            table = Table(
                [
                    {'id_final_energy_carrier': 1, 'id_partner_region': 1, '2000': 10, '2020': 20},
                    {'id_final_energy_carrier': 1, 'id_partner_region': 2, '2000': 30, '2020': 10},
                    {'id_final_energy_carrier': 2, 'id_partner_region': 1, '2000': 30, '2020': 10},
                    {'id_final_energy_carrier': 2, 'id_partner_region': 2, '2000': 10, '2020': 20},
                ]
            )
            result = table.indices_for_max_annual_values(['id_final_energy_carrier'])
            assert result['2000'][1] == (1, 2)
            assert result['2000'][2] == (2, 1)

            assert result['2020'][1] == (1, 1)
            assert result['2020'][2] == (2, 2)

        def test_changing_column_order(self):
            table = Table(
                [
                    {'id_partner_region': 1, 'id_final_energy_carrier': 1, '2000': 10, '2020': 20},
                    {'id_partner_region': 1, 'id_final_energy_carrier': 2, '2000': 30, '2020': 10},
                    {'id_partner_region': 2, 'id_final_energy_carrier': 1, '2000': 30, '2020': 10},
                    {'id_partner_region': 2, 'id_final_energy_carrier': 2, '2000': 10, '2020': 20},
                ]
            )
            result = table.indices_for_max_annual_values(['id_final_energy_carrier'])
            assert result['2000'][1] == (2, 1)
            assert result['2000'][2] == (1, 2)

            assert result['2020'][1] == (1, 1)
            assert result['2020'][2] == (2, 2)

    def test_insert_index_column(self, sut):
        result = sut.insert_index_column('id_new', 1, 33)
        id_column_names, _, _ = result.column_names
        assert id_column_names == ['id_foo', 'id_new', 'id_baa']
        index_values = list(result.index.get_level_values(1))
        assert index_values == [33]

    class TestJoinAndMultiply:
        @patch(Table.contains_nan, True)
        def test_with_nan_entries(self, sut):
            with raises(ValueError):
                sut._join_and_multiply('mocked_factor_table')

        @patch(Table.contains_nan, False)
        @patch(
            Table._validate_factor_table_for_multiplication,
            'mocked_result',
        )
        def test_without_nan_entries(self, sut):
            factor_table = Table([{'id_parameter': 11, '2000': 2}])
            result = sut._join_and_multiply(factor_table)
            assert result['2000'][1, 2, 11] == 4000

    @patch(Table._fix_id_column_order_after_multiplication)
    # pylint: disable=undefined-variable
    class TestJoinAndMultiplyValueTable:
        mocked_table = Mock()
        mocked_table.sort = Mock('mocked_result')

        @patch(Table._validate_value_table_for_multiplication)
        @patch(Table._join_column_names, [])
        @patch(AbstractTable._contains_nan, False)
        @patch(Table._create, Mock(mocked_table))
        def test_without_join_column_names(self, sut):
            value_table = Mock()
            result = sut._join_and_multiply_value_table(value_table)
            assert result == 'mocked_result'

        @patch(Table._validate_value_table_for_multiplication)
        @patch(Table._join_column_names, [])
        @patch(AbstractTable._contains_nan, True)
        @patch(Table._create, mocked_table)
        def test_with_nan_entries(self, sut):
            value_table = Mock()
            with raises(KeyError):
                sut._join_and_multiply_value_table(value_table)

    class TestJoinIdColumn:
        def test_without_unknown_entries(self):
            table = Table([{'id_foo': 1, '2000': 10}])
            id_table = IdTable([{'id': 1, 'label': 'baa', 'description': 'baa_description'}])

            result = table.join_id_column(id_table, 'foo')
            data_frame = result._data_frame
            columns = list(data_frame.columns)
            assert columns == ['2000', 'foo']
            assert result['foo'][0] == 'baa'

        def test_with_unknown_entries(self):
            table = Table([{'id_foo': 2, '2000': 10}])
            id_table = IdTable([{'id': 1, 'label': 'baa', 'description': 'baa_description'}])

            with raises(KeyError):
                table.join_id_column(id_table, 'foo')

    def test_map(self):
        table = Table(
            [
                {'id_foo': 1, 'id_baa': 1, '2010': 10, '2020': 20},
                {'id_foo': 1, 'id_baa': 2, '2010': 30, '2020': 40},
            ]
        )

        def mapping_function(value, index, column_name):
            mapping_result = column_name + '|' + str(index) + '|' + str(value)
            return mapping_result

        result = table.map(mapping_function)

        assert result['2010'][1, 1] == '2010|(1, 1)|10'
        assert result['2010'][1, 2] == '2010|(1, 2)|30'

        assert result['2020'][1, 1] == '2020|(1, 1)|20'
        assert result['2020'][1, 2] == '2020|(1, 2)|40'

    @patch(AbstractTable._apply_mapping_table, 'mocked_data_frame')
    @patch(Table.__init__, mocked_table__init__)
    def test_map_id_column(self, sut):
        result = sut.map_id_column('mocked_mapping_table')
        data_frame = result._data_frame
        assert data_frame == 'mocked_frame'

    def test_mean(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.mean = Mock('mocked_result')
        result = sut.mean()
        assert result == 'mocked_result'

    class TestDiv:
        class TestTableThroughValue:
            def test_table_contains_numbers_divided_by_number(self):
                left_table = Table([{'a': 10, 'b': 20}])

                right_value = 2

                result = left_table / right_value

                data_frame = result._data_frame
                assert data_frame['a'][0] == 5
                assert data_frame['b'][0] == 10

            def test_table_contains_numbers_divided_by_zero(self):
                left_table = Table([{'a': 10, 'b': 20}])

                right_value = 0

                result = left_table / right_value

                data_frame = result._data_frame
                assert data_frame['a'][0] == 0
                assert data_frame['b'][0] == 0

            def test_table_contains_zero_divided_by_zero(self):
                left_table = Table([{'a': 0, 'b': 20}])

                right_value = 0

                result = left_table / right_value

                data_frame = result._data_frame
                assert data_frame['a'][0] == 0
                assert data_frame['b'][0] == 0

            def test_table_contains_nan_divided_by_number(self):
                left_table = Table([{'a': np.nan, 'b': 20}])

                right_value = 2

                with raises(ValueError):
                    left_table / right_value  # pylint: disable=pointless-statement

            def test_table_contains_infinity_divided_by_number(self):
                left_table = Table([{'a': np.inf, 'b': 20}])

                right_value = 2

                with raises(ValueError):
                    left_table / right_value  # pylint: disable=pointless-statement

        def test_table_through_table(self):
            left_table = Table([{'a': 10, 'b': 20}])
            right_table = Table([{'a': 1, 'b': 2}])

            result = left_table / right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == 10
            assert data_frame['b'][0] == 10

        def test_value_through_table(self):
            left_value = 10
            right_table = Table([{'a': 1, 'b': 2}])

            result = left_value / right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == 10
            assert data_frame['b'][0] == 5

    class TestMul:
        class TestTableTimesTable:
            @patch(
                AbstractTable._fix_column_order_after_multiplication,
                lambda self, frame: frame,
            )
            def test_same_dimension(self):
                left_table = Table([{'a': 10, 'b': 20}])
                right_table = Table([{'a': 1, 'b': 2}])

                result = left_table * right_table

                data_frame = result._data_frame
                assert data_frame['a'][0] == 10
                assert data_frame['b'][0] == 40

            class TestDifferentDimension:
                @patch(
                    AbstractTable._fix_column_order_after_multiplication,
                    lambda self, frame: frame,
                )
                def test_left_more_columns(self):
                    left_table = Table(
                        [
                            {'id_foo': 1, 'id_baa': 1, '2000': 1},
                            {'id_foo': 1, 'id_baa': 2, '2000': 2},
                        ]
                    )

                    right_table = Table(
                        [
                            {'id_baa': 1, '2000': 10},
                            {'id_baa': 2, '2000': 20},
                        ]
                    )

                    result = left_table * right_table
                    data_frame = result._data_frame
                    assert data_frame['2000'][1, 1] == 10
                    assert data_frame['2000'][1, 2] == 40

                result_frame = pd.DataFrame(
                    [
                        {'id_foo': 1, 'id_baa': 1, '2000': 10},
                        {'id_foo': 1, 'id_baa': 2, '2000': 40},
                    ]
                )
                result_frame.set_index(['id_foo', 'id_baa'], inplace=True)

                @patch(
                    AbstractTable._fix_column_order_after_multiplication,
                    result_frame,
                )
                def test_right_more_columns(self):
                    left_table = Table(
                        [
                            {'id_baa': 1, '2000': 10},
                            {'id_baa': 2, '2000': 20},
                        ]
                    )

                    right_table = Table(
                        [
                            {'id_foo': 1, 'id_baa': 1, '2000': 1},
                            {'id_foo': 1, 'id_baa': 2, '2000': 2},
                        ]
                    )

                    result = left_table * right_table
                    data_frame = result._data_frame
                    assert data_frame['2000'][1, 1] == 10
                    assert data_frame['2000'][1, 2] == 40

        @patch(
            AbstractTable._fix_column_order_after_multiplication,
            lambda self, frame: frame,
        )
        def test_value_times_table(self):
            left_value = 2
            right_table = Table([{'a': 1, 'b': 2}])

            result = left_value * right_table

            data_frame = result._data_frame
            assert data_frame['a'][0] == 2
            assert data_frame['b'][0] == 4

        @patch(
            AbstractTable._fix_column_order_after_multiplication,
            lambda self, frame: frame,
        )
        def test_table_times_value(self):
            left_table = Table([{'a': 1, 'b': 2}])
            right_value = 2

            result = left_table * right_value

            data_frame = result._data_frame
            assert data_frame['a'][0] == 2
            assert data_frame['b'][0] == 4

        @patch(
            AbstractTable._fix_column_order_after_multiplication,
            lambda self, frame: frame,
        )
        def test_data_frame_times_table(self):
            left_frame = pd.DataFrame([{'a': 10, 'b': 20}])
            right_table = Table([{'a': 1, 'b': 2}])

            # attention: this returns a data_frame of table values
            with raises(ValueError):
                left_frame * right_table  # pylint: disable=pointless-statement

        @patch(
            AbstractTable._fix_column_order_after_multiplication,
            lambda self, frame: frame,
        )
        def test_table_times_data_frame(self):
            left_table = Table([{'a': 1, 'b': 2}])
            right_frame = pd.DataFrame([{'a': 10, 'b': 20}])

            # attention: this returns a data_frame of table values
            result = left_table * right_frame

            assert result['a'][0] == 10
            assert result['b'][0] == 40

    class TestNormalize:
        @patch(Table.contains_nan, True)
        @patch(Table.contains_object, False)
        def test_with_nan(self, sut):
            with raises(ValueError):
                sut.normalize(['id_foo'])

        @patch(Table.contains_nan, False)
        @patch(Table.contains_object, True)
        def test_with_object(self, sut):
            with raises(ValueError):
                sut.normalize(['id_foo'])

        @patch(Table.contains_nan, False)
        @patch(Table.contains_object, False)
        def test_with_index_columns(self, sut):
            result = sut.normalize(['id_foo'])
            assert result['2000'][1, 2] == 1

        @patch(Table.contains_nan, False)
        @patch(Table.contains_object, False)
        @patch(
            Table._normalize_group,
            pd.DataFrame([{'id_foo': 1, 'id_baa': 2, '2000': 99}]),
        )
        def test_without_index_columns(self, sut):
            result = sut.normalize()
            assert result['2000'][1, 2] == 99

    class TestQuery:
        @patch(Table.__init__, mocked_table__init__)
        def test_normal_usage(self, sut):
            mocked_result = pd.DataFrame([{'id_foo': 1, '2000': 1}])

            sut._data_frame = Mock()
            sut._data_frame.query = Mock(mocked_result)

            result = sut.query('mocked_query')
            assert result._data_frame == 'mocked_frame'

        @patch(Table.__init__, mocked_table__init__)
        def test_with_empty_result(self, sut):
            mocked_result = pd.DataFrame()

            sut._data_frame = Mock()
            sut._data_frame.query = Mock(mocked_result)

            result = sut.query('mocked_query')
            assert result is None

    def test_query_using_at_syntax(self):
        table = Table(
            [
                {'id_foo': 1, 'id_baa': 33, '2000': 2000},
                {'id_foo': 1, 'id_baa': 34, '2000': 2000},
            ]
        )

        query = 'id_baa in @query_list'
        id_values = [34, 35]
        result_table = table.query_using_at_syntax(query, id_values)

        data_frame = result_table._data_frame
        assert len(data_frame) == 1

        assert data_frame['2000'][1, 34] == 2000

    class TestReduce:
        @patch(Table._reduce_data_frame, None)
        def test_none(self, sut):
            result = sut.reduce('mocked_id_name', 'mocked_id_value_or_array')
            assert result is None

        @patch(Table._reduce_data_frame, pd.DataFrame())
        def test_empty_result(self, sut):
            result = sut.reduce('mocked_id_name', 'mocked_id_value_or_array')
            assert result is None

        @patch(
            Table._reduce_data_frame,
            Mock(pd.DataFrame([{'id_foo': 1, '2000': 1}])),
        )
        @patch(
            Table._convert_single_row_reduction_result,
            Mock('mocked_result'),
        )
        def test_single_row_result(self, sut):
            result = sut.reduce('mocked_id_name', 'mocked_id_value_or_array')
            assert result == 'mocked_result'

        @patch(
            Table._reduce_data_frame,
            Mock(
                pd.DataFrame(
                    [
                        {'id_foo': 1, '2010': 10},
                        {'id_foo': 2, '2020': 20},
                    ]
                ),
            ),
        )
        @patch(
            Table._create,
            Mock('mocked_table'),
        )
        def test_normal_usage(self, sut):
            result = sut.reduce('mocked_id_name', 'mocked_id_value_or_array')
            assert result == 'mocked_table'

    @patch(
        Table._create,
        Mock('mocked_table'),
    )
    def test_reindex(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.reindex = Mock()
        result = sut.reindex()
        sut._data_frame.reindex.assert_called_once()
        assert result == 'mocked_table'

    def test_rename(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.rename = Mock()
        sut.rename(None)
        sut._data_frame.rename.assert_called_once()

    def mocked_table_init(self, _data_frame_or_array):
        self._data_frame = 'mocked_frame'  # pylint: disable=attribute-defined-outside-init

    @patch(Table.__init__, mocked_table_init)
    def test_replace(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.empty = False
        sut._data_frame.replace = Mock()

        sut.replace('value_from', 'value_to')
        sut._data_frame.replace.assert_called_once()

    def test_replace_negative_values_with_zeros(self, sut):
        sut._data_frame = pd.DataFrame([{'value': -1}])
        result = sut.replace_negative_values_with_zero()
        assert result['value'][0] == 0

    class TestSetIndex:
        def test_with_multiindex(self):
            table = Table(
                [
                    {'id_foo': 1, 'id_baa': 1, '2010': 1, '2020': 2},
                    {'id_foo': 1, 'id_baa': 2, '2010': 10, '2020': 20},
                ]
            )
            table.set_index(['id_baa', 'id_foo'])
            id_column_names, _, _ = table.column_names
            assert id_column_names == ['id_baa', 'id_foo']

        def test_without_multiindex(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2010': 1, '2020': 2},
                    {'id_foo': 1, 'id_baa': 2, '2010': 10, '2020': 20},
                ]
            )
            sut._data_frame = data_frame
            sut.set_index(['id_baa', 'id_foo'])
            id_column_names, _, _ = sut.column_names
            assert id_column_names == ['id_baa', 'id_foo']

    def test_sort(self, sut):
        data_frame = pd.DataFrame(
            [
                {'id_foo': 2, 'value': 2},
                {'id_foo': 1, 'value': 1},
            ]
        )
        data_frame.set_index(['id_foo'], inplace=True)
        sut._data_frame = data_frame

        result = sut.sort()

        values = list(result['value'].values)
        assert values == [1, 2]

    def test_sort_columns(self, sut):
        columns = ['c', 'b', 'a']
        sut._data_frame = pd.DataFrame([[1, 2, 3]], columns=columns)
        sorted_table = sut.sort_columns()
        sorted_columns = sorted_table._data_frame.columns
        assert sorted_columns[0] == 'a'
        assert sorted_columns[-1] == 'c'

    def test_sum(self):
        table = Table(
            [
                {'id_foo': 1, '2000': 1, '2020': 2},
                {'id_foo': 2, '2000': 10, '2020': 20},
            ]
        )
        result = table.sum()
        series = result._series
        assert series['2000'] == 11
        assert series['2020'] == 22

    def test_to_custom_json(self, sut):
        with patch_property(Table.column_names, (['id_foo', 'id_baa'], ['2000'], [])):
            with patch_property(Table.rows, 'mocked_rows'):
                custom_json = sut.to_custom_json()
                assert custom_json['idColumnNames'] == ['id_foo', 'id_baa']
                assert custom_json['yearColumnNames'] == ['2000']
                assert custom_json['rows'] == 'mocked_rows'

    def test_to_numpy(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.to_numpy = Mock()
        sut.to_numpy()
        sut._data_frame.to_numpy.assert_called_once()

    @patch(np.vstack, [])
    def test_to_numpy_with_headers(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.columns.to_numpy = Mock()
        sut._data_frame.to_numpy = Mock()
        return_value = sut.to_numpy_with_headers()

        sut._data_frame.reset_index.assert_called_once()
        assert return_value == []

    mocked_df = pd.DataFrame(
        [
            {'energy_carrier': 'oil', '2000': 10, '2020': 20},
            {'energy_carrier': 'gas', '2000': 100, '2020': 200},
        ]
    )
    mocked_df.set_index('energy_carrier', inplace=True)

    def test_to_table_with_numeric_column_names(self, sut):
        converted_table = sut.to_table_with_numeric_column_names()
        data_frame = converted_table._data_frame
        columns = list(data_frame.columns)
        assert columns == [2000]

    def test_to_table_with_string_column_names(self):
        table = Table([{'id_foo': 1, 'id_baa': 2, 2000: 2000}])
        converted_table = table.to_table_with_string_column_names()
        data_frame = converted_table._data_frame
        columns = list(data_frame.columns)
        assert columns == ['2000']

    @patch(Table._fix_integer_year_columns, mocked_df)
    def test_transpose(self):
        table = Table(
            [
                {'energy_carrier': 'oil', '2000': 10, '2020': 20},
                {'energy_carrier': 'gas', '2000': 100, '2020': 200},
            ]
        )
        result = table.transpose('energy_carrier')

        data_frame = result._data_frame
        columns = list(data_frame.columns)
        assert columns == ['oil', 'gas']

        assert result['oil']['2000'] == 10
        assert result['oil']['2020'] == 20

    @staticmethod
    def mocked_index():
        data_frame = pd.DataFrame(
            [
                {'id_qux': 1, 'id_foo': 1, 'id_baa': 1, 'value': 10},
                {'id_qux': 1, 'id_foo': 1, 'id_baa': 2, 'value': 20},
            ]
        )
        data_frame.set_index(['id_foo', 'id_baa'], inplace=True)
        return data_frame.index

    def test_unique_index_values(self, sut):
        with patch_property(Table.index, TestPublicApi.mocked_index()):
            foo_values = sut.unique_index_values('id_foo')
            assert foo_values == [1]

            baa_values = sut.unique_index_values('id_baa')
            assert baa_values == [1, 2]

    def test_unique_multi_index_tuples(self, sut):
        with patch_property(Table.index, TestPublicApi.mocked_index()):
            foo_values = sut.unique_multi_index_tuples(['id_foo', 'id_baa'])
            assert foo_values == [(1, 1), (1, 2)]

    class TestUpdate:
        def test_existing_entry(self):
            table = Table(
                [
                    {'id_foo': 1, '2000': 1},
                    {'id_foo': 2, '2000': 2},
                ]
            )

            update_table = Table(
                [
                    {'id_foo': 1, '2000': 10},
                ]
            )

            result = table.update(update_table)

            assert result['2000'][1] == 10
            assert result['2000'][2] == 2

        def test_extra_entry(self):
            table = Table(
                [
                    {'id_foo': 1, '2000': 1},
                    {'id_foo': 2, '2000': 2},
                ]
            )

            update_table = Table(
                [
                    {'id_foo': 3, '2000': 3},
                ]
            )

            result = table.update(update_table)

            assert result['2000'][1] == 1
            assert result['2000'][2] == 2
            assert result['2000'][3] == 3

    def test_values(self, sut):
        sut._data_frame = Mock()
        sut._data_frame.values = []
        assert sut.values == []

    @patch(AbstractTable._other_value)
    def test_where(self, sut):
        sut._data_frame = Mock()
        mocked_frame = pd.DataFrame([{'foo': 1}])
        sut._data_frame.where = Mock(mocked_frame)
        result = sut.where('mocked_condition_table', 'mocked_fallback_value_table')
        assert result._data_frame['foo'][0] == 1

    def test_rows(self):
        table = Table(
            [
                {'id_foo': 1, '2000': 33},
                {'id_foo': 2, '2000': 34},
            ]
        )
        result = table.rows
        assert result == [
            [1, 33],
            [2, 34],
        ]

    @patch(
        list_utils.string_to_integer,
        'mocked_integer_years',
    )
    def test_years(self, sut):
        with patch_property(
            Table.column_names,
            ([], 'mocked_year_column_names', []),
        ):
            result = sut.years
            assert result == 'mocked_integer_years'


class TestPrivateApi:
    class TestContainsAnyValue:
        def test_with_value(self):
            result = Table._contains_any_value([1], [1, 2, 3])
            assert result is True

        def test_without_value(self):
            result = Table._contains_any_value([4], [1, 2, 3])
            assert result is False

    def test_create_data_frame_with_single_row(self):
        parent_id_names = ['id_region', 'id_subsector']
        parent_id_values = (1, 3)
        id_name = 'id_final_energy_carrier'
        id_value = 7
        year_column_names = ['2000', '2020']
        value = 0

        result = Table._create_data_frame_with_single_row(
            parent_id_names,
            parent_id_values,
            id_name,
            id_value,
            year_column_names,
            value,
        )
        assert len(result) == 1
        assert list(result.index.names) == ['id_region', 'id_subsector', 'id_final_energy_carrier']
        assert list(result.columns) == year_column_names

    def test_drop_if_exists(self, sut):
        result_data_frame = Table._drop_if_exists(sut._data_frame, '2000')
        columns = list(result_data_frame.columns)
        assert columns == []  # pylint: disable=use-implicit-booleaness-not-comparison

        result_data_frame = Table._drop_if_exists(result_data_frame, '2000')
        columns = list(result_data_frame.columns)
        assert columns == []  # pylint: disable=use-implicit-booleaness-not-comparison

    @patch(Table._column_names, (['id_foo', 'id_baa'], [2000], []))
    def test_fix_integer_year_columns(self):
        data_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 2, 2000: 2000}])
        fixed_data_frame = Table._fix_integer_year_columns(data_frame)
        columns = list(fixed_data_frame.columns)
        assert columns == ['id_foo', 'id_baa', '2000']

    def test_normalize_group(self):
        series = pd.Series(data=[2, 2, 0], index=[1, 2, 3])
        result = Table._normalize_group(series)
        assert result[1] == 0.5
        assert result[2] == 0.5
        assert result[3] == 0

    class TestParentIdColumnNames:
        def test_without_column(self):
            id_column_names = ['id_foo', 'id_baa', 'id_qux']
            id_column_name = 'id_other'
            with raises(KeyError):
                Table._parent_id_column_names(id_column_names, id_column_name)

        def test_with_interim_column(self):
            id_column_names = ['id_foo', 'id_baa', 'id_qux']
            id_column_name = 'id_baa'
            with raises(KeyError):
                Table._parent_id_column_names(id_column_names, id_column_name)

        def test_normal_usage(self):
            id_column_names = ['id_foo', 'id_baa', 'id_qux']
            id_column_name = 'id_qux'
            result = Table._parent_id_column_names(id_column_names, id_column_name)
            assert result == ['id_foo', 'id_baa']

    @patch(
        Table._id_column_order_after_multiplication,
        ['id_foo', 'id_baa'],
    )
    def test_fix_id_column_order_after_multiplication(self, sut):
        indexed_data_frame = pd.DataFrame([{'id_baa': 1, 'id_foo': 2}])
        indexed_data_frame.set_index(['id_baa', 'id_foo'], inplace=True)
        result = sut._fix_id_column_order_after_multiplication(
            indexed_data_frame,
            'mocked_factor_table',
        )
        assert list(result.index.names) == ['id_foo', 'id_baa']

    @patch(list_utils.difference, ['id_qux'])
    def test_id_column_order_after_multiplication(self, sut):
        factor_table = Mock()
        factor_table.column_names = (['id_foo', 'id_baa', 'id_qux'], [], [])
        result = sut._id_column_order_after_multiplication(factor_table)
        assert result == ['id_foo', 'id_baa', 'id_qux']

    @staticmethod
    def mocked_table():
        series = pd.Series([33], index=[1])
        return Table(series)

    @patch(Table.aggregate_to, mocked_table())
    def test_index_entries(self, sut):
        result = sut._index_entries(['id_foo'])
        assert len(result) == 1
        assert result[0] == 1

    class TestReduceDataFrame:
        @patch(Table._reduce_data_frame_by_id, 'mocked_result')
        def test_with_id_value(self, sut):
            result = sut._reduce_data_frame('mocked_id_name', 1)
            assert result == 'mocked_result'

        @patch(
            Table._reduce_data_frame_by_id_array,
            'mocked_result',
        )
        def test_with_id_array(self, sut):
            result = sut._reduce_data_frame('mocked_id_name', [1, 2])
            assert result == 'mocked_result'

    class TestReduceDataFrameById:
        def test_with_existing_value(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 33},
                    {'id_foo': 1, 'id_baa': 2, '2000': 34},
                ]
            )
            data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

            sut._data_frame = data_frame
            reduced_data_frame = sut._reduce_data_frame_by_id('id_baa', 2)

            index_columns = reduced_data_frame.index.names
            assert index_columns == ['id_foo']

            columns = list(reduced_data_frame.columns)
            assert columns == ['2000']

            assert reduced_data_frame['2000'][1] == 34

        def test_without_existing_value(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 33},
                    {'id_foo': 1, 'id_baa': 2, '2000': 34},
                ]
            )
            data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

            sut._data_frame = data_frame
            result = sut._reduce_data_frame_by_id('id_baa', 3)
            assert result is None

    class TestReduceDataFrameByIdArray:
        def test_with_existing_values(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 33},
                    {'id_foo': 1, 'id_baa': 2, '2000': 34},
                    {'id_foo': 1, 'id_baa': 3, '2000': 35},
                ]
            )
            data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

            sut._data_frame = data_frame
            reduced_data_frame = sut._reduce_data_frame_by_id_array('id_baa', [1, 3])

            index_columns = reduced_data_frame.index.names
            assert index_columns == ['id_foo', 'id_baa']

            columns = list(reduced_data_frame.columns)
            assert columns == ['2000']

            assert len(reduced_data_frame) == 2

            assert reduced_data_frame['2000'][1, 1] == 33
            assert reduced_data_frame['2000'][1, 3] == 35

        def test_without_existing_value(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id_foo': 1, 'id_baa': 1, '2000': 33},
                    {'id_foo': 1, 'id_baa': 2, '2000': 34},
                    {'id_foo': 1, 'id_baa': 3, '2000': 35},
                ]
            )
            data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

            sut._data_frame = data_frame
            result = sut._reduce_data_frame_by_id_array('id_baa', [4])
            assert result is None

    def mocked_annual_series_init(self, _series_or_series_argument):
        self._series = 'mocked_series'  # pylint: disable = attribute-defined-outside-init

    @patch(
        AnnualSeries.__init__,
        mocked_annual_series_init,
    )
    def test_convert_single_row_reduction_result(self, sut):
        result = sut._convert_single_row_reduction_result('mocked_single_row_data_frame')
        assert result._series == 'mocked_series'

    class TestValidateFactorTableForColumnMultiplication:
        def test_with_nan(self, sut):
            factor_table = Mock()
            factor_table.contains_nan = Mock(True)
            with raises(ValueError):
                sut._validate_value_table_for_multiplication(factor_table)

        @patch(
            list_utils.intersection,
            ['id_foo', 'id_baa'],
        )
        def test_with_extra_entries(self, sut):
            factor_table = Mock()
            factor_table.contains_nan = Mock(False)
            factor_table.column_names = (['id_foo', 'id_baa', 'id_qux'], [], [])
            factor_table.unique_multi_index_tuples = Mock(['mocked_tuple'])

            sut.unique_multi_index_tuples = Mock([])

            with patch(Logger.warn) as mocked_warn:
                sut._validate_value_table_for_multiplication(factor_table)
                mocked_warn.assert_called_once()

        @patch(
            list_utils.intersection,
            ['id_foo', 'id_baa'],
        )
        def test_without_extra_entries(self, sut):
            factor_table = Mock()
            factor_table.contains_nan = Mock(False)
            factor_table.column_names = (['id_foo', 'id_baa', 'id_qux'], [], [])
            factor_table.unique_multi_index_tuples = Mock(['mocked_tuple'])

            sut.unique_multi_index_tuples = Mock(['mocked_tuple'])

            with patch(Logger.warn) as mocked_warn:
                sut._validate_value_table_for_multiplication(factor_table)
                mocked_warn.assert_not_called()

    class TestValidateFactorTableForMultiplication:
        def test_with_nan_value(self, sut):
            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(True)
            with raises(ValueError):
                sut._validate_factor_table_for_multiplication(mocked_factor_table)

        def test_with_different_year_column_names(self, sut):
            patch.object(sut, 'column_names', property(([], ['2000'], [])))

            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(False)
            mocked_factor_table.column_names = ([], ['2000', '2020'], [])

            with raises(ValueError):
                sut._validate_factor_table_for_multiplication(mocked_factor_table)

        def test_with_different_value_column_names(self, sut):
            patch.object(sut, 'column_names', property(([], ['2000'], ['foo'])))

            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(False)
            mocked_factor_table.column_names = ([], ['2000'], ['baa'])

            with raises(ValueError):
                sut._validate_factor_table_for_multiplication(mocked_factor_table)

        def test_with_intersecting_id_column_names(self, sut):
            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(False)
            mocked_factor_table.column_names = (['id_baa'], ['2000'], [])

            with patch_property(
                Table.column_names,
                (['id_foo', 'id_baa'], ['2000'], []),
            ):
                with raises(ValueError):
                    sut._validate_factor_table_for_multiplication(mocked_factor_table)

        def test_with_dummy_column(self, sut):
            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(False)
            mocked_factor_table.column_names = (['id_foo'], ['2000'], [])

            with patch_property(
                Table.column_names,
                (['id_dummy', 'id_baa'], ['2000'], []),
            ):
                with raises(KeyError):
                    sut._validate_factor_table_for_multiplication(mocked_factor_table)

        def test_with_dummy_column_in_factor_table(self, sut):
            mocked_factor_table = Mock()
            mocked_factor_table.contains_nan = Mock(False)
            mocked_factor_table.column_names = (['id_dummy'], ['2000'], [])

            with patch_property(
                Table.column_names,
                (['id_baa'], ['2000'], []),
            ):
                with raises(KeyError):
                    sut._validate_factor_table_for_multiplication(mocked_factor_table)
