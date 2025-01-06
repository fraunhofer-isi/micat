# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access, duplicate-code
import math

import numpy as np
import pandas as pd

from micat.log.logger import Logger
from micat.series.annual_series import AnnualSeries
from micat.table.abstract_table import AbstractTable
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, fixture, patch, patch_property


@fixture(name='sut')
def sut_fixture():
    series = pd.Series([1, 2, 3], index=['2000', '2020', '2030'])
    sut = AnnualSeries(series)
    return sut


class TestPublicAPI:
    def test_add(self, sut):
        other_series = AnnualSeries({'2000': 10, '2020': 20, '2030': 30})

        result = sut + other_series
        assert result['2000'] == 11
        assert result['2020'] == 22
        assert result['2030'] == 33

    def test_columns(self, sut):
        result = sut.columns
        assert result == ['2000', '2020', '2030']

    class TestContainsInf:
        def test_with_infinity(self):
            series = AnnualSeries({'2000': np.inf})
            result = series.contains_inf()
            assert result

        def test_with_negative_infinity(self):
            series = AnnualSeries({'2000': -np.inf})
            result = series.contains_inf()
            assert result

        def test_with_nan(self):
            series = AnnualSeries({'2000': np.nan})
            result = series.contains_inf()
            assert not result

        def test_without_infinity(self):
            series = AnnualSeries({'2000': 1})
            result = series.contains_inf()
            assert not result

    class TestContainsNaN:
        def test_with_nan(self):
            series = AnnualSeries({'2000': np.nan})
            result = series.contains_nan()
            assert result

        def test_with_infinity(self):
            series = AnnualSeries({'2000': np.inf})
            result = series.contains_nan()
            assert not result

        def test_without_nan(self):
            series = AnnualSeries({'2000': 1})
            result = series.contains_nan()
            assert not result

    def test_copy(self, sut):
        result = sut.copy()
        assert len(result) == 3
        assert result['2000'] == 1
        assert result['2020'] == 2
        assert result['2030'] == 3

    def test_len(self, sut):
        result = len(sut)
        assert result == 3

    class TestDiv:
        def test_series_by_value(self, sut):
            result = sut / 0.5
            series = result._series
            assert series['2000'] == 2
            assert series['2020'] == 4
            assert series['2030'] == 6

        def test_value_by_series(self, sut):
            result = 6 / sut
            series = result._series
            assert series['2000'] == 6
            assert series['2020'] == 3
            assert series['2030'] == 2

    class TestFillNaNValuesByExtrapolation:
        def test_with_existing_negative_values(self):
            series = pd.Series([-1, 1, np.nan], index=['2000', '2020', '2030'])
            annual_series = AnnualSeries(series)
            with patch_property(
                Table.column_names,
                (['id_foo'], ['2000', '2020', '2030']),
            ):
                with patch(Logger.error) as mocked_error:
                    with patch(Logger.warn) as mocked_warn:
                        annual_series.fill_nan_values_by_extrapolation()
                        mocked_error.assert_called_once()
                        mocked_warn.assert_called_once()

        def test_interpolation(self):
            series = pd.Series([10, np.nan, 30], index=['2000', '2020', '2030'])

            with patch_property(
                Table.column_names,
                (['id_foo'], ['2000', '2020', '2030']),
            ):
                annual_series = AnnualSeries(series)
                extrapolated_series = annual_series.fill_nan_values_by_extrapolation()
                assert extrapolated_series['2020'] == 20

        def test_interpolation_with_unsorted_columns(self):
            series = pd.Series([30, 10, np.nan], index=['2030', '2000', '2020'])
            annual_series = AnnualSeries(series)

            with patch_property(
                Table.column_names,
                (['id_foo'], ['2030', '2000', '2020']),
            ):
                extrapolated_series = annual_series.fill_nan_values_by_extrapolation()
                assert extrapolated_series['2020'] == 20

    class TestMul:
        class TestAnnualSeriesTimesAnnualSeries:
            def test_same_years(self):
                left_series = AnnualSeries({'2010': 10, '2020': 20})
                right_series = AnnualSeries({'2010': 2, '2020': 3})

                result = left_series * right_series

                series = result._series
                assert series['2010'] == 20
                assert series['2020'] == 60

            class TestDifferentYears:
                @patch(
                    AbstractTable._fix_column_order_after_multiplication,
                    lambda self, frame: frame,
                )
                def test_left_more_years(self):
                    left_series = AnnualSeries({'2010': 10, '2020': 20, '2030': 30})
                    right_series = AnnualSeries({'2010': 2, '2020': 3})

                    result = left_series * right_series

                    series = result._series
                    assert series['2010'] == 20
                    assert series['2020'] == 60
                    assert math.isnan(series['2030'])

                def test_right_more_years(self):
                    left_series = AnnualSeries({'2010': 10, '2020': 20})
                    right_series = AnnualSeries({'2010': 2, '2020': 3, '2030': 4})

                    result = left_series * right_series

                    series = result._series
                    assert series['2010'] == 20
                    assert series['2020'] == 60
                    assert math.isnan(series['2030'])

                def test_right_with_extra_interim_year(self):
                    left_series = AnnualSeries({'2010': 10, '2020': 20})
                    right_series = AnnualSeries({'2010': 2, '2015': 4, '2020': 3})

                    result = left_series * right_series

                    series = result._series
                    assert series['2010'] == 20
                    assert math.isnan(series['2015'])
                    assert series['2020'] == 60

        def test_annual_series_times_value(self):
            left_series = AnnualSeries({'2010': 1, '2020': 2})
            right_value = 2

            # this is handled by __mul__ function of AnnualSeries
            result = left_series * right_value

            assert isinstance(result, AnnualSeries)

            series = result._series
            assert series['2010'] == 2
            assert series['2020'] == 4

        def test_value_times_annual_series(self):
            left_value = 2
            right_series = AnnualSeries({'2010': 1, '2020': 2})

            # this is handled by __rmul__ function of AnnualSeries
            result = left_value * right_series

            assert isinstance(result, AnnualSeries)

            series = result._series
            assert series['2010'] == 2
            assert series['2020'] == 4

        def test_data_frame_times_annual_series(self):
            left_frame = pd.DataFrame([{'id_foo': 1, '2000': 10, '2020': 20}])
            left_frame.set_index(['id_foo'], inplace=True)

            right_series = AnnualSeries({'2000': 1, '2020': 2})

            result = left_frame * right_series

            assert result['2000'][1] == 10
            assert result['2020'][1] == 20

        def test_annual_series_times_data_frame(self):
            left_series = AnnualSeries({'2000': 1, '2020': 2})

            right_frame = pd.DataFrame([{'id_foo': 1, '2000': 10, '2020': 20}])
            right_frame.set_index(['id_foo'], inplace=True)

            result = left_series * right_frame
            # data frame result is converted to table because we expect to work with tables where possible
            assert isinstance(result, Table)
            assert result['2000'][1] == 10
            assert result['2020'][1] == 40

        def test_table_times_annual_series(self):
            left_table = Table([{'id_foo': 1, '2000': 10, '2020': 20}])
            right_series = AnnualSeries({'2000': 1, '2020': 2})

            # this is handled by __mul__ function of Table class, not of __rmul__ of AnnualSeries
            result = left_table * right_series

            assert isinstance(result, Table)
            assert result['2000'][1] == 10
            assert result['2020'][1] == 40

        def test_annual_series_times_table(self):
            left_series = AnnualSeries({'2000': 1, '2020': 2})
            right_table = Table([{'id_foo': 1, '2000': 10, '2020': 20}])

            # this is handled by __mul__ function of AnnualSeries
            result = left_series * right_table

            assert isinstance(result, Table)
            assert result['2000'][1] == 10
            assert result['2020'][1] == 40

        def test_annual_series_times_value_table(self):
            left_series = AnnualSeries({'2000': 1, '2020': 2})
            right_value_table = ValueTable([{'id_foo': 1, 'value': 10}])

            result = left_series * right_value_table

            assert isinstance(result, Table)
            assert result['2000'][1] == 10
            assert result['2020'][1] == 20

    def test_to_series_with_numeric_column_names(self, sut):
        converted_series = sut.to_series_with_numeric_column_names()
        series = converted_series._series
        columns = series.index.to_list()
        assert columns == [2000, 2020, 2030]

    def test_to_series_with_string_column_names(self):
        series = pd.Series([1, 2], index=[2000, 2020])
        annual_series = AnnualSeries(series)
        converted_series = annual_series.to_series_with_string_column_names()
        series = converted_series._series
        columns = series.index.to_list()
        assert columns == ['2000', '2020']

    def test_transpose(self, sut):
        result = sut.transpose('id_parameter', 10)
        assert result['2000'][10] == 1
        assert result['2020'][10] == 2
        assert result['2030'][10] == 3

    class TestUpdate:
        def test_with_table(self, sut):
            update_table = Table([{'id_foo': 1, '2000': 88}])
            result = sut.update(update_table)
            assert result['2000'] == 88

        def test_with_annual_series(self, sut):
            update_series = AnnualSeries({'2000': 88})
            result = sut.update(update_series)
            assert result['2000'] == 88

        def test_with_series(self, sut):
            update_series = pd.Series({'2000': 88})
            result = sut.update(update_series)
            assert result['2000'] == 88

    def test_set_item(self, sut):
        sut['2040'] = 7
        assert sut['2040'] == 7

    def test_sub(self, sut):
        result = sut - 1
        series = result._series
        assert series['2000'] == 0
        assert series['2020'] == 1
        assert series['2030'] == 2

    def test_repr(self, sut):
        sut._series = Mock()
        sut._series.__repr__ = Mock('mocked_representation')
        result = str(sut)
        assert result == 'mocked_representation'

    def test_rsub(self, sut):
        result = 1 - sut
        series = result._series
        assert series['2000'] == 0
        assert series['2020'] == -1
        assert series['2030'] == -2

    def test_years(self, sut):
        result = sut.years
        assert result == [2000, 2020, 2030]

    def test_values(self, sut):
        result = sut.values
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3


class TestPrivateAPI:
    class TestOtherValue:
        def test_abstract_series(self, sut):
            result = AnnualSeries._other_value(sut)
            assert (result == sut._series).all()

        def test_table(self):
            other = Table([{'id_foo': 1, '2000': 99}])
            result = AnnualSeries._other_value(other)
            assert isinstance(result, pd.DataFrame)
            assert result['2000'][1] == 99

        def test_number(self):
            result = AnnualSeries._other_value(2)
            assert result == 2
