# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/56
import math

import pandas as pd

from micat.series.annual_series import AnnualSeries


def extrapolate(table, year_numbers):
    if table is None:
        raise ValueError("Table must not be None.")
    if isinstance(table, AnnualSeries):
        raise ValueError("Wrong argument. Please use function extrapolate_series to extrapolate series.")

    table_with_integer_years = table.to_table_with_numeric_column_names()
    table_with_nan_values = _create_nan_entries_for_missing_year_columns(table_with_integer_years, year_numbers)
    extrapolated_data_frame = table_with_nan_values.fill_nan_values_by_extrapolation()
    filtered_table = extrapolated_data_frame[year_numbers]
    table_with_string_years = filtered_table.to_table_with_string_column_names()
    return table_with_string_years


def extrapolate_series(annual_series, year_numbers):
    if annual_series is None:
        raise ValueError("Annual series must not be None.")
    series_with_integer_years = annual_series.to_series_with_numeric_column_names()
    series_with_nan_values = _create_nan_entries_for_missing_year_columns(series_with_integer_years, year_numbers)
    extrapolated_series = series_with_nan_values.fill_nan_values_by_extrapolation()
    filtered_series = extrapolated_series[year_numbers]
    series_with_string_years = filtered_series.to_series_with_string_column_names()
    return series_with_string_years


def _create_nan_entries_for_missing_year_columns(table_or_annual_series, year_numbers):
    new_table_or_annual_series = table_or_annual_series.copy()
    sorted_year_numbers = sorted(year_numbers)
    for year in sorted_year_numbers:
        if isinstance(year, str):
            raise ValueError("Year numbers must not be passed as strings!")
        if year not in table_or_annual_series.columns:
            new_table_or_annual_series[year] = math.nan
    # If first year is NaN, set the year before to zero to allow extrapolation
    first_year = sorted_year_numbers[0]
    val = new_table_or_annual_series[first_year]
    if isinstance(val, float) and pd.isna(val) or isinstance(val, pd.Series) and val.isna().any():
        year_before = first_year - 1
        new_table_or_annual_series[year_before] = 0.0
    return new_table_or_annual_series
