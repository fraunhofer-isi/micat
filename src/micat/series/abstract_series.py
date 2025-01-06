# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

from micat.table import table  # pylint: disable=cyclic-import


class AbstractSeries:
    def __init__(self, series_or_series_argument):
        if isinstance(series_or_series_argument, pd.Series):
            self._series = series_or_series_argument
        elif isinstance(series_or_series_argument, pd.DataFrame):
            self._series = AbstractSeries._create_series_from_data_frame(series_or_series_argument)
        elif isinstance(series_or_series_argument, table.Table):
            # noinspection PyProtectedMember
            data_frame = series_or_series_argument._data_frame  # pylint: disable=protected-access
            self._series = AbstractSeries._create_series_from_data_frame(data_frame)
        else:
            self._series = pd.Series(series_or_series_argument)

    @staticmethod
    def _create_series_from_data_frame(data_frame):
        if len(data_frame) < 1:
            raise ValueError('Dataframe must not be empty to create a series!')

        if len(data_frame) == 1:
            row_series = data_frame.iloc[0]
            return row_series
        else:
            if len(data_frame.columns) > 1:
                raise ValueError('Dataframe must not include multiple rows and multiple columns to create a series!')

            column_series = AbstractSeries._create_series_from_single_column_data_frame(data_frame)
            return column_series

    @staticmethod
    def _create_series_from_single_column_data_frame(data_frame):
        index = data_frame.index
        if len(index.names) > 1:
            raise KeyError('Data frame must not include multi index to create a series from its single column!')

        column_name = data_frame.columns[0]
        column_series = data_frame[column_name]
        column_series.index = column_series.index.map(str)
        return column_series

    def items(self):
        return self._series.items()

    @property
    def a_preview(self):
        # the purpose of this is to help with debugging because
        # the custom type rendering feature of PyCharm does not seem to work
        # Also see
        # https://stackoverflow.com/questions/74195566/pycharm-community-editon-does-not-apply-custom-type-rendering
        return self._series
