# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
import pandas as pd

from micat.log.logger import Logger
from micat.series.abstract_series import AbstractSeries
from micat.table.table import Table  # pylint: disable=cyclic-import
from micat.table.value_table import ValueTable  # pylint: disable=cyclic-import


class AnnualSeries(AbstractSeries):
    @staticmethod
    def _other_value(other):
        if isinstance(other, AbstractSeries):
            # noinspection PyProtectedMember
            return other._series  # pylint: disable=protected-access
        elif isinstance(other, Table):
            # noinspection PyProtectedMember
            return other._data_frame  # pylint: disable=protected-access
        else:
            return other

    @property
    def columns(self):
        columns = self._series.index.to_list()
        return columns

    def contains_inf(self):
        return np.isinf(self._series).values.any()

    def contains_nan(self):
        return self._series.isnull().values.any()

    def copy(self):
        copied_series = self._series.copy()
        return AnnualSeries(copied_series)

    def fill_nan_values_by_extrapolation(self):
        series = self._series
        includes_negative_values = (series < 0).any()
        if includes_negative_values:
            Logger.error("Interpolation of negative values is not yet implemented.")

        year_column_names = self.columns
        year_column_names.sort()
        sorted_series = self._series[year_column_names]

        interpolated_series = sorted_series.interpolate(method="linear", s=0, limit_direction="both")

        interpolated_data_includes_negative_values = (interpolated_series < 0).any()
        if interpolated_data_includes_negative_values:
            Logger.warn("Replacing negative values of extrapolated data with zeros.")
            # We do not allow negative values, also see #125
            interpolated_series.clip(lower=0, inplace=True)

        return AnnualSeries(interpolated_series)

    def items(self):
        return self._series.items()

    def __len__(self):
        return len(self._series)

    def sum(self):
        total = self._series.sum()
        return total

    def map(self, mapping_function):
        series = self._series
        new_series_data = [mapping_function(value, year) for year, value in series.items()]
        result_series = pd.Series(data=new_series_data, index=series.index)
        return AnnualSeries(result_series)

    def to_series_with_numeric_column_names(self):
        columns = self.columns
        column_name_mapping = {column_name: int(column_name) for column_name in columns}
        result_series = self._series.rename(index=column_name_mapping)
        return AnnualSeries(result_series)

    def to_series_with_string_column_names(self):
        columns = self.columns
        column_name_mapping = {column_name: str(column_name) for column_name in columns}
        result_series = self._series.rename(index=column_name_mapping)
        return AnnualSeries(result_series)

    def transpose(self, id_name, id_value):
        frame = pd.DataFrame(self._series)
        transposed_frame = frame.transpose()
        new_index = pd.Index(data=[id_value], name=id_name)
        transposed_frame.index = new_index
        transposed_table = Table(transposed_frame)
        return transposed_table

    def update(self, table_or_series):
        series = table_or_series
        if isinstance(table_or_series, Table):
            series = table_or_series.first_row

        if isinstance(table_or_series, AnnualSeries):
            series = table_or_series._series  # pylint: disable=protected-access

        result_series = self._series.copy()
        result_series.update(series)
        return AnnualSeries(result_series)

    def __add__(self, other):
        result_series = AnnualSeries._other_value(other) + self._series
        return AnnualSeries(result_series)

    def __getitem__(self, key):  # implements [] access
        item = self._series[key]
        if isinstance(item, pd.Series):
            return AnnualSeries(item)
        else:
            return item

    def __repr__(self):
        return self._series.__repr__()

    def __rsub__(self, other):
        result = AnnualSeries._other_value(other) - self._series
        return AnnualSeries(result)

    def __rtruediv__(self, other):
        result = AnnualSeries._other_value(other) / self._series
        return AnnualSeries(result)

    def __setitem__(self, key, value):  # implements [] access
        self._series[key] = value

    def __sub__(self, other):
        result = self._series - AnnualSeries._other_value(other)
        if isinstance(result, pd.DataFrame):
            return Table(result)
        else:
            return AnnualSeries(result)

    def __truediv__(self, other):
        result = self._series / AnnualSeries._other_value(other)
        if isinstance(result, pd.Series):
            return AnnualSeries(result)
        else:
            return Table(result)

    def __mul__(self, other):
        if isinstance(other, ValueTable):
            result = other * self
            return result
        else:
            result = self._series * AnnualSeries._other_value(other)
            if isinstance(result, pd.Series):
                return AnnualSeries(result)
            else:
                return Table(result)

    def __rmul__(self, other):
        result_series = AnnualSeries._other_value(other) * self._series
        return AnnualSeries(result_series)

    @property
    def years(self):
        years = list(map(int, self.columns))
        return years

    @property
    def values(self):
        values = self._series.values
        return values
