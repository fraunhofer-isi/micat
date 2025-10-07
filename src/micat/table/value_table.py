# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.table.table import Table


class ValueTable(Table):
    # A table that contains a single value column "value" instead of multiple annual columns

    def __init__(self, data_frame_or_array, name=None):
        data_frame = Table._construct_data_frame(data_frame_or_array)
        data_frame.name = name
        super().__init__(data_frame)

    @staticmethod
    def concat(tables_or_data_frames):
        combined_table = Table.concat(tables_or_data_frames)
        # noinspection PyProtectedMember
        value_table = ValueTable._create(combined_table._data_frame)  # pylint: disable=protected-access
        return value_table

    @staticmethod
    def from_table(source_table):
        # noinspection PyProtectedMember
        data_frame = source_table._data_frame  # pylint: disable=protected-access
        return ValueTable(data_frame)

    @staticmethod
    def from_index(source_table):
        dummy_table = source_table.copy()
        dummy_table['value'] = 1
        series = dummy_table['value']
        value_table = ValueTable(series)
        return value_table

    # noinspection PyDefaultArgument
    @staticmethod
    def from_json(custom_json, where_clause={}):  # pylint: disable=dangerous-default-value
        data_frame = ValueTable._data_frame_from_json(custom_json)
        data_frame = ValueTable._drop_if_exists(data_frame, 'id')
        if 'id_region' in where_clause:
            data_frame = ValueTable._drop_if_exists(data_frame, 'id_region')
        data_frame = ValueTable._drop_if_exists(data_frame, 'id_unit')
        return ValueTable._create(data_frame)

    def __mul__(self, other):
        # import is there to avoid circular import dependencies
        from micat.series.annual_series import (  # pylint: disable=import-outside-toplevel
            AnnualSeries,
        )

        if isinstance(other, AnnualSeries):
            result_table = self._join_and_multiply_annual_series(other)
            return result_table
        else:
            result_table = super().__mul__(other)
            return result_table

    @property
    def years(self):
        return None

    @staticmethod
    def _create(data_frame_or_array):
        return ValueTable(data_frame_or_array)

    def _convert_single_row_reduction_result(self, single_row_data_frame):
        value = single_row_data_frame.iloc[0]['value']
        return value

    def _join_and_multiply_annual_series(self, annual_factor_series):
        if annual_factor_series.contains_nan():
            raise ValueError('Factor series must not include NaN values.')

        data_frame = self._data_frame.copy()

        for year in annual_factor_series.years:
            data_frame[str(year)] = data_frame['value']
        del data_frame['value']

        result_table = annual_factor_series * data_frame

        return result_table

    def _join_and_multiply_value_table(self, value_table):
        self._validate_value_table_for_multiplication(value_table)

        join_column_names = self._join_column_names(value_table)
        data_frame = self._data_frame
        if len(join_column_names) < 1:
            dummy_column_name = 'id_dummy__'
            # noinspection PyProtectedMember
            data_frame = self.insert_index_column(  # pylint: disable=protected-access
                dummy_column_name,
                0,
                0,
            )._data_frame
            value_table = value_table.insert_index_column(dummy_column_name, 0, 0)

        # noinspection PyProtectedMember
        product = data_frame * value_table._data_frame  # pylint: disable=protected-access

        contains_nan = Table._contains_nan(product)  # pylint: disable=protected-access
        if contains_nan:
            message = 'Value tables misses some entries. => Product would include NaN values which is not allowed.'
            raise KeyError(message)

        if len(join_column_names) < 1:
            del value_table[dummy_column_name]
            product = product.droplevel(dummy_column_name)

        product = self._fix_id_column_order_after_multiplication(product, value_table)
        value_table = self._create(product)

        sorted_table = value_table.sort()
        return sorted_table

    def _multi_index_lookup_for_cell(self, index_value_or_tuple, _column_name, index_order):
        multi_index_value = self._create_index_entry(index_value_or_tuple, index_order)
        cell_result = self['value'][multi_index_value]
        return cell_result
