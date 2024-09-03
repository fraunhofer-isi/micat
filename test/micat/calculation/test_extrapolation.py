# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
# pylint: disable=protected-access
import pandas as pd

from micat.calculation import extrapolation
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table
from micat.test_utils.isi_mock import patch, raises

years = [2010, 2020, 2030]

mocked_extrapolated_table = Table(
    [
        {'id_parameter': 1, 'id_final_energy_carrier': 1, 2010: 1, 2020: 2, 2030: 3},
        {'id_parameter': 1, 'id_final_energy_carrier': 2, 2010: 10, 2020: 20, 2030: 30},
    ]
)


class TestExtrapolate:
    def test_without_table(self):
        with raises(ValueError):
            extrapolation.extrapolate(None, 'mocked_years')

    def test_with_wrong_argument(self):
        support_point = AnnualSeries({'2000': 1})
        with raises(ValueError):
            extrapolation.extrapolate(support_point, 'mocked_years')

    @patch(
        Table.to_table_with_numeric_column_names,
        'mocked_table',
    )
    @patch(
        extrapolation._create_nan_entries_for_missing_year_columns,
        mocked_extrapolated_table,
    )
    @patch(
        Table.fill_nan_values_by_extrapolation,
        mocked_extrapolated_table,
    )
    @patch(
        Table.to_table_with_string_column_names,
        'mocked_result',
    )
    def test_normal_usage(self):
        support_point = Table(
            [
                {'id_parameter': 1, 'id_final_energy_carrier': 1, '2010': 1, '2020': 2},
                {'id_parameter': 1, 'id_final_energy_carrier': 2, '2010': 10, '2020': 20},
            ]
        )

        result = extrapolation.extrapolate(support_point, years)
        assert result == 'mocked_result'

    def test_full_usage(self):
        support_point = Table(
            [
                {'id_parameter': 1, 'id_final_energy_carrier': 1, '2011': 18993114, '2012': 17507752, '2013': 16914282, '2014': 16672871, '2015': 15301375},
            ]
        )

        years = range(2016, 2022)

        result = extrapolation.extrapolate(support_point, years)
        assert result[2016][1][1] != 15301375

    def test_pandas_interpolate(self):

        df = pd.DataFrame([{2011: 18993114, 2012: 17507752, 2013: 16914282, 2014: 16672871, 2015: 15301375, 2016: np.nan, 2017: np.nan, 2018: np.nan, 2019: np.nan, 2020: np.nan}])

        result = df.interpolate(method="spline", axis=1, order=1, s=0, limit_direction="both")
        assert result[2016] != 15301375

extrapolated_series = pd.Series([1, 2, 3], index=[2010, 2020, 2030])
mocked_extrapolated_series = AnnualSeries(extrapolated_series)


class TestExtrapolateSeries:
    @patch(
        AnnualSeries.to_series_with_numeric_column_names,
        'mocked_series',
    )
    @patch(
        extrapolation._create_nan_entries_for_missing_year_columns,
        mocked_extrapolated_series,
    )
    @patch(
        AnnualSeries.fill_nan_values_by_extrapolation,
        mocked_extrapolated_series,
    )
    @patch(
        AnnualSeries.to_series_with_string_column_names,
        'mocked_result',
    )
    def test_normal_usageg(self):
        series = pd.Series([1, 2], index=['2000', '2020'])
        annual_series = AnnualSeries(series)
        result = extrapolation.extrapolate_series(annual_series, years)
        assert result == 'mocked_result'

    def test_without_series(self):
        with raises(ValueError):
            extrapolation.extrapolate_series(None, 'mocked_years')


class TestNanEntriesForMissingYearColumns:
    def test_with_string_years(self):
        with raises(ValueError):
            extrapolation._create_nan_entries_for_missing_year_columns(
                mocked_extrapolated_table,
                ['2011', '2005'],
            )

    def test_normal_usage(self):
        result = extrapolation._create_nan_entries_for_missing_year_columns(
            mocked_extrapolated_table,
            [2011, 2005],
        )
        _id_column_names, year_column_names, _ = result.column_names

        assert year_column_names == [2010, 2020, 2030, 2005, 2011]
