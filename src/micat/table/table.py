# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

import numpy as np
import pandas as pd

from micat.log.logger import Logger
from micat.table.abstract_table import (
    AbstractTable,  # pylint: disable=import-error, no-name-in-module
)
from micat.utils import list as list_utils


class Table(AbstractTable):
    # pylint: disable = too-many-public-methods

    def __init__(self, data_frame_or_series_or_array):
        data_frame = AbstractTable._construct_data_frame(data_frame_or_series_or_array)
        if Table._is_indexed(data_frame):
            super().__init__(data_frame)
        else:
            id_column_names, _, _ = Table._column_names(data_frame)
            if len(id_column_names) > 0:
                indexed_data_frame = data_frame.set_index(id_column_names)
                super().__init__(indexed_data_frame)
            else:
                super().__init__(data_frame)

    @staticmethod
    def concat(tables_or_data_frames):
        data_frames = list(map(AbstractTable._other_value, tables_or_data_frames))
        id_names = list(data_frames[0].index.names)
        for data_frame in data_frames:
            current_id_names = list(data_frame.index.names)
            if current_id_names != id_names:
                raise KeyError('Order of index column names must be equal for concatenation')
                # Also see
                # https://stackoverflow.com/questions/75434950/how-to-correctly-consider-multi-index-column-names-for-pandas-concat

        data_frame = pd.concat(data_frames)
        return Table._create(data_frame)

    @staticmethod
    def concat_years(tables_or_data_frames):
        data_frames = list(map(AbstractTable._other_value, tables_or_data_frames))
        merged_frame = pd.concat(data_frames, axis=1)
        table = Table._create(merged_frame)
        return table

    # noinspection PyDefaultArgument
    @staticmethod
    def from_json(custom_json, where_clause={}):  # pylint: disable=dangerous-default-value
        data_frame = AbstractTable._data_frame_from_json(custom_json)
        data_frame = AbstractTable._drop_if_exists(data_frame, 'id')
        if 'id_region' in where_clause:
            data_frame = AbstractTable._drop_if_exists(data_frame, 'id_region')
        data_frame = AbstractTable._drop_if_exists(data_frame, 'id_unit')
        return Table._create(data_frame)

    @staticmethod
    def from_json_string(json_string):
        rows = json.loads(json_string)
        data_frame = pd.DataFrame(rows)
        details = data_frame['details']  # pylint: disable=unused-variable
        # TO DO : handle details
        del data_frame['details']
        data_frame = Table._fix_integer_year_columns(data_frame)
        table = Table._create(data_frame)
        return table

    @staticmethod
    def read_excel(file_path):
        data_frame = pd.read_excel(file_path)
        table = Table(data_frame)
        return table

    @staticmethod
    def _contains_any_value(values_to_look_for, available_values):
        for value in values_to_look_for:
            if value in available_values:
                return True
        return False

    @staticmethod
    def _create(data_frame_or_array):
        return Table(data_frame_or_array)

    # pylint: disable=too-many-arguments
    @staticmethod
    def _create_data_frame_with_single_row(
        parent_id_names,
        parent_id_values,
        id_name,
        id_value,
        year_column_names,
        value,
    ):
        entries = {}

        for key_name, key_value in zip(parent_id_names, parent_id_values):
            entries[key_name] = key_value

        entries[id_name] = id_value

        for year_column_name in year_column_names:
            entries[year_column_name] = value

        data_frame = pd.DataFrame([entries])

        index_columns = parent_id_names + [id_name]
        data_frame.set_index(index_columns, inplace=True)
        return data_frame

    @staticmethod
    def _fix_integer_year_columns(data_frame):
        _, years, _ = Table._column_names(data_frame)
        year_column_name_mapping = {year: str(year) for year in years}
        fixed_df = data_frame.rename(year_column_name_mapping, axis=1)
        return fixed_df

    # @staticmethod
    # def _key_column_names(id_column_names):
    #     key_column_names = list(filter(lambda id_column_name: id_column_name != 'id_unit', id_column_names))
    #     return key_column_names

    @staticmethod
    def handle_division_by_zero(table: 'Table'):
        # pylint: disable = protected-access
        table._data_frame = table._data_frame.replace([np.inf, -np.inf], np.nan)
        table._data_frame = table._data_frame.fillna(0)
        return table

    @staticmethod
    def _normalize_group(series_or_frame):
        normalized_values = series_or_frame / series_or_frame.sum()
        normalized_values.fillna(0, inplace=True)
        return normalized_values

    @staticmethod
    def _parent_id_column_names(id_column_names, id_column_name):
        if id_column_name not in id_column_names:
            message = 'The id column ' + id_column_name + ' does not exist.'
            raise KeyError(message)

        index = id_column_names.index(id_column_name)

        if index != (len(id_column_names) - 1):
            message = 'The id column ' + id_column_name + ' has to be the last id column.'
            raise KeyError(message)

        parent_names = id_column_names[:index]
        return parent_names

    def aggregate(self, id_column_name_to_remove):
        id_column_names, _, _ = self.column_names
        id_column_names.remove(id_column_name_to_remove)
        if len(id_column_names) > 0:
            table = self.aggregate_to(id_column_names)
            return table
        else:
            series = self._data_frame.sum()
            return series

    def aggregate_to(self, remaining_id_column_names):
        result_frame = self._data_frame.groupby(remaining_id_column_names).sum()
        table = Table(result_frame)
        return table

    def aggregate_by_mean_to(self, remaining_column_names):
        result_frame = self._data_frame.groupby(remaining_column_names).mean()
        result_frame.reset_index(inplace=True)
        table = Table(result_frame)
        return table

    def multi_index_lookup(self, indices_for_wanted_values, index_order):
        # The first argument is a table where each cell contains a multi index tuple, pointing to
        # the row
        # The second argument specified the meaning of the tuple entries. It is a list containing
        # the corresponding id_column names

        # noinspection PyProtectedMember
        result_data_frame = indices_for_wanted_values._data_frame.apply(  # pylint: disable=protected-access
            lambda column: self._multi_index_lookup_for_column(column, index_order),
        )
        return Table(result_data_frame)

    def annual_mean(self):
        mean_series = self._data_frame.mean(axis=1)
        return mean_series

    def astype(self, type_):
        return self._create(self._data_frame.astype(type_))

    def contains_inf(self):
        return AbstractTable._contains_inf(self._data_frame)

    def contains_nan(self):
        return AbstractTable._contains_nan(self._data_frame)

    def contains_non_nan(self):
        return self._data_frame.notnull().values.any()

    def contains_object(self):
        return AbstractTable._contains_object(self._data_frame)

    def contains_negative_values(self):
        return (self < 0).values.any()

    def copy(self):
        return self._create(self._data_frame.copy())

    def divide_without_checks(self, other):
        result_data_frame = self._data_frame / AbstractTable._other_value(other)
        table = self._create(result_data_frame)
        return table

    def droplevel(self, *args, **kwargs):
        result_frame = self._data_frame.droplevel(*args, **kwargs)
        return self._create(result_frame)

    def drop(self, *args, **kwargs):
        result_frame = self._data_frame.drop(*args, **kwargs)
        return self._create(result_frame)

    # def dropna(self):
    # DO NOT implement dropna here but make sure that there are no
    # NaN values that need to be dropped. Our data must not include
    # NaN values.
    # * Clean up the imported Excel sheet by deleting or filling corresponding rows.
    # * Filter the input tables before transposing or multiplying them etc.
    #
    # Automatically dropping NaN values might lead to unexpected behavior
    # because errors could propagate deeper into our business logic
    # without notice.
    # Logger.warn('Avoid using NaN, so that you do not need to drop them!')

    def eq(self, value):  # pylint: disable=invalid-name
        result_data_frame = self._data_frame.eq(value)
        return self._create(result_data_frame)

    def fill_missing_values(
        self,
        id_column_name,
        id_values,
        value,
    ):
        # key_column_names = self.key_column_names
        key_column_names, year_column_names, _ = self.column_names
        parent_id_names = Table._parent_id_column_names(key_column_names, id_column_name)

        index_entries = self._index_entries(parent_id_names)

        for entry in index_entries:
            for id_value in id_values:
                extra_row = self._create_data_frame_with_single_row(
                    parent_id_names,
                    entry,
                    id_column_name,
                    id_value,
                    year_column_names,
                    value,
                )
                self._data_frame = pd.concat([self._data_frame, extra_row])

        self._data_frame = self._data_frame.sort_index()

    def fill_missing_value(self, key_entries, value):
        id_column_names, year_column_names, _ = self.column_names
        row_data = key_entries.copy()
        for year_column_name in year_column_names:
            row_data[year_column_name] = value

        extra_row = pd.DataFrame([row_data])
        extra_row.set_index(id_column_names, inplace=True)

        self._data_frame = pd.concat([self._data_frame, extra_row])

        self._data_frame = self._data_frame.sort_index()

    def fillna(self, series, inplace=False):
        if inplace:
            self._data_frame.fillna(series, inplace=True)
            return None
        else:
            result_data_frame = self._data_frame.fillna(series)
            return self._create(result_data_frame)

    def fill_nan_values_by_extrapolation(self):
        data_frame = self._data_frame
        includes_negative_values = (data_frame < 0).any().any()
        if includes_negative_values:
            Logger.error('Interpolation of negative values is not yet implemented.')

        _, year_column_names, _ = self.column_names
        year_column_names.sort()
        sorted_data_frame = self._data_frame[year_column_names]

        interpolated_data_frame = sorted_data_frame.interpolate(method='linear', axis=1, s=0, limit_direction='both')

        interpolated_data_includes_negative_values = (interpolated_data_frame < 0).any().any()
        if interpolated_data_includes_negative_values:
            Logger.warn('Replacing negative values of extrapolated data with zeros.')
            # We do not allow negative values, also see #125
            interpolated_data_frame.clip(lower=0, inplace=True)

        return self._create(interpolated_data_frame)

    def has_index_column(self, index_column_name):
        index_column_names, _year_column_names, _ = self.column_names
        has_column = index_column_name in index_column_names
        return has_column

    def indices_for_max_annual_values(self, remaining_column_names):
        # searches the max value for each year in a group and determines
        # the index entry corresponding to that max value

        result_data_frame = self._data_frame.groupby(remaining_column_names).idxmax()
        return self._create(result_data_frame)

    def insert_index_column(self, id_column_name, id_column_index, value):
        id_column_names, _year_column_names, _value_column_names = self.column_names
        id_column_names.insert(id_column_index, id_column_name)
        data_frame = self._data_frame.copy().reset_index()
        data_frame[id_column_name] = value
        data_frame = data_frame.set_index(id_column_names)
        return self._create(data_frame)

    def join_id_column(self, id_table, new_column_name, is_keeping_id_column=False):
        id_column_name = 'id_' + new_column_name
        # noinspection PyProtectedMember
        id_data_frame = id_table._data_frame  # pylint: disable=protected-access
        result_data_frame = self._data_frame.merge(
            id_data_frame,
            how='left',
            left_on=id_column_name,
            right_index=True,
        )

        labels_contain_nan = result_data_frame['label'].isna().any()
        if labels_contain_nan:
            raise KeyError("Table contains unknown values for " + id_column_name)

        result_data_frame = result_data_frame.reset_index()

        if not is_keeping_id_column:
            del result_data_frame[id_column_name]
        del result_data_frame['description']
        result_data_frame.rename({'label': new_column_name}, axis=1, inplace=True)
        return self._create(result_data_frame)

    def map(self, mapping_function):
        def _column_mapping_function(column_series):
            column_name = column_series.name
            new_series_data = [mapping_function(value, index, column_name) for index, value in column_series.items()]
            new_series = pd.Series(data=new_series_data, index=column_series.index)
            return new_series

        result_data_frame = self._data_frame.apply(_column_mapping_function)
        return self._create(result_data_frame)

    def map_id_column(self, mapping_table):
        data_frame_without_index = self._data_frame.reset_index()
        result_data_frame = AbstractTable._apply_mapping_table(data_frame_without_index, mapping_table)
        return self._create(result_data_frame)

    def mean(self):
        return self._data_frame.mean()

    def normalize(self, id_column_names=None):
        if id_column_names is None:
            id_column_names = []

        if self.contains_nan():
            raise ValueError('This function does not support handling of NaN input values.')

        if self.contains_object():
            raise ValueError('This function does not support handling of object input values.')

        if len(id_column_names) > 0:
            groups = self._data_frame.groupby(level=id_column_names)
            normalized_data_frame = groups.transform(Table._normalize_group)
        else:
            normalized_data_frame = Table._normalize_group(self._data_frame)
        return self._create(normalized_data_frame)

    def query(self, query):
        result_data_frame = self._data_frame.query(query)
        if len(result_data_frame) < 1:
            return None
        else:
            return self._create(result_data_frame)

    # noinspection PyUnusedLocal
    def query_using_at_syntax(self, query, query_list=None):  # pylint: disable=unused-argument
        # This function is a workaround for a known issue:
        # If you use a query like "foo in @my_array", the variable my_array
        # is not known by the wrapping function.
        # => Use the hard coded variable name "query_list" and
        # pass the list as an additional argument.
        result = self._data_frame.query(query)
        return self._create(result)

    def reduce(self, id_name, id_value_or_list):
        # If id_value is passed as list, we keep the ids for a single row result.
        # Otherwise, the single row result is converted to corresponding data type and
        # redundant id values are removed.
        is_keeping_index = isinstance(id_value_or_list, list)
        reduced_data_frame = self._reduce_data_frame(id_name, id_value_or_list)
        if reduced_data_frame is None:
            return None

        if len(reduced_data_frame) == 0:
            return None

        if (len(reduced_data_frame) == 1) and not is_keeping_index:
            result = self._convert_single_row_reduction_result(reduced_data_frame)
            return result
        else:
            return self._create(reduced_data_frame)

    def reindex(
        self,
        labels=None,
        index=None,
        columns=None,
        axis=None,
        method=None,
        copy=None,
        level=None,
        fill_value=np.nan,
        limit=None,
        tolerance=None,
    ):
        reindexed_data_frame = self._data_frame.reindex(
            labels=labels,
            index=index,
            columns=columns,
            axis=axis,
            method=method,
            copy=copy,
            level=level,
            fill_value=fill_value,
            limit=limit,
            tolerance=tolerance,
        )
        return self._create(reindexed_data_frame)

    def rename(self, *args, **kwargs):
        self._data_frame.rename(*args, **kwargs)

    def replace(self, value_from, value_to):
        result_data_frame = self._data_frame.replace(value_from, value_to)
        return self._create(result_data_frame)

    def replace_negative_values_with_zero(self):
        result_data_frame = self._data_frame.clip(lower=0)
        return self._create(result_data_frame)

    def set_index(self, columns):
        for column_name in columns:
            if column_name not in self._data_frame.columns:
                self._data_frame = self._data_frame.reset_index()
        self._data_frame = self._data_frame.set_index(columns)

    def sort(self):
        id_column_names, _year_column_names, _ = self.column_names
        result_data_frame = self._data_frame.sort_values(by=id_column_names)
        return self._create(result_data_frame)

    def sort_columns(self):
        sorted_dataframe = self._data_frame.reindex(sorted(self._data_frame.columns), axis=1)
        return self._create(sorted_dataframe)

    def sum(self):
        # import needs to be here to avoid circular import dependencies
        from micat.series.annual_series import (  # pylint: disable=import-outside-toplevel
            AnnualSeries,
        )

        sum_series = self._data_frame.sum()
        return AnnualSeries(sum_series)

    def to_custom_json(self):
        id_column_names, year_column_names, _ = self.column_names
        custom_json = {
            'idColumnNames': id_column_names,
            'yearColumnNames': year_column_names,
            'rows': self.rows,
        }
        return custom_json

    def to_numpy(self):
        array = self._data_frame.to_numpy()
        return array

    def to_numpy_with_headers(self):
        data_frame_with_index_columns = self._data_frame.reset_index()
        headers = data_frame_with_index_columns.columns.to_numpy()
        values = data_frame_with_index_columns.to_numpy()
        array = np.vstack((headers, values))
        return array

    def to_table_with_numeric_column_names(self):
        columns = self._data_frame.columns
        column_name_mapping = {column_name: int(column_name) for column_name in columns}
        result_data_frame = self._data_frame.rename(columns=column_name_mapping)
        return self._create(result_data_frame)

    def to_table_with_string_column_names(self):
        columns = self._data_frame.columns
        column_name_mapping = {column_name: str(column_name) for column_name in columns}
        result_data_frame = self._data_frame.rename(columns=column_name_mapping)
        return self._create(result_data_frame)

    def transpose(self, column_for_new_column_names):
        indexed_df = self._data_frame.set_index(column_for_new_column_names)
        indexed_df = Table._fix_integer_year_columns(indexed_df)
        transposed_df = indexed_df.transpose()
        transposed_df.columns.name = ''
        transposed_df.index.name = 'year'
        return self._create(transposed_df)

    def unique_index_values(self, index_column_name):
        index_values = list(set(self.index.get_level_values(index_column_name)))
        index_values.sort()
        return index_values

    def unique_multi_index_tuples(self, column_names):
        unused_column_names = [name for name in self.index.names if name not in column_names]
        sub_index = self.index.droplevel(unused_column_names)
        unique_index_tuples = list(set(sub_index.tolist()))
        return unique_index_tuples

    def update(self, table):
        # noinspection PyProtectedMember
        all_entries = pd.concat([self._data_frame, table._data_frame])  # pylint: disable=protected-access
        unique_entries = all_entries.query('~index.duplicated(keep="last")')
        table = self._create(unique_entries)
        sorted_table = table.sort()
        return sorted_table

    def validate_input_for_division(self):
        if self._data_frame.isnull().any().any():
            raise ValueError("Input for division contains NaN values")

        if not np.isfinite(self._data_frame).all().all():
            raise ValueError("Input for division contains infinite values")

    def where(self, condition_table, fallback_value_table):
        condition = AbstractTable._other_value(condition_table)
        fallback_value = AbstractTable._other_value(fallback_value_table)
        result_data_frame = self._data_frame.where(condition, fallback_value)
        return self._create(result_data_frame)

    def __mul__(self, other):
        # import needs to be here to avoid circular import dependency
        from micat.table.value_table import (  # pylint: disable=import-outside-toplevel, cyclic-import
            ValueTable,
        )

        if isinstance(other, ValueTable):
            table = self._join_and_multiply_value_table(other)
            return table
        else:
            other_value = AbstractTable._other_value(other)
            try:
                data_frame = self._data_frame * other_value
                sorted_data_frame = self._fix_column_order_after_multiplication(data_frame)
                return self._create(sorted_data_frame)
            except ValueError:
                table = self._join_and_multiply(other)
                return table

    def __truediv__(self, other):
        # import needs to be here to avoid circular import dependencies
        from micat.table.value_table import (  # pylint: disable=import-outside-toplevel
            ValueTable,
        )

        Table.validate_input_for_division(self)
        if isinstance(other, ValueTable):
            table = self._join_and_multiply_value_table(1 / other)

            # handle_division_by_zero(table)
        else:
            result_data_frame = self._data_frame / AbstractTable._other_value(other)
            table = self._create(result_data_frame)
        table = Table.handle_division_by_zero(table)
        return table

    def _fix_id_column_order_after_multiplication(self, indexed_data_frame, factor_table):
        data_frame = indexed_data_frame.reset_index()
        ordered_id_column_names = self._id_column_order_after_multiplication(factor_table)
        data_frame.set_index(ordered_id_column_names, inplace=True)
        return data_frame

    def _id_column_order_after_multiplication(self, factor_table):
        id_column_names, _, _ = self.column_names
        factor_id_column_names, _, _ = factor_table.column_names
        extra_id_column_names = list_utils.difference(factor_id_column_names, id_column_names)
        ordered_id_column_names = id_column_names + extra_id_column_names
        return ordered_id_column_names

    def _index_entries(self, id_names):
        table_with_unique_parent_id_entries = self.aggregate_to(id_names)
        unique_index = table_with_unique_parent_id_entries.index
        return unique_index

    def _join_and_multiply(self, factor_table):
        if self.contains_nan():
            raise ValueError('Table must not include NaN values before multiplication.')

        self._validate_factor_table_for_multiplication(factor_table)

        dummy_column_name = 'id_dummy__'
        left_table = self.insert_index_column(dummy_column_name, 0, 0)
        right_table = factor_table.insert_index_column(dummy_column_name, 0, 0)
        product_table = left_table * right_table
        table = product_table.droplevel(dummy_column_name)
        return table

    # pylint: disable=duplicate-code
    def _join_and_multiply_value_table(self, value_table):
        self._validate_value_table_for_multiplication(value_table)

        join_column_names = self._join_column_names(value_table)
        data_frame = self._data_frame
        if len(join_column_names) < 1:
            dummy_column_name = 'id_dummy__'
            data_frame = self.insert_index_column(  # pylint: disable=protected-access
                dummy_column_name,
                0,
                0,
            )._data_frame
            value_table = value_table.insert_index_column(dummy_column_name, 0, 0)

        # noinspection PyProtectedMember
        value_frame = value_table._data_frame  # pylint: disable=protected-access

        merged_frame = data_frame.join(value_frame, validate='one_to_many')

        contains_nan = AbstractTable._contains_nan(merged_frame)
        if contains_nan:
            message = 'Value tables misses some entries. => Product would include NaN values which is not allowed.'
            raise KeyError(message)

        value_series = value_table['value']

        product = merged_frame.multiply(value_series, axis=0)
        del product['value']

        if len(join_column_names) < 1:
            del value_table[dummy_column_name]
            product = product.droplevel(dummy_column_name)

        product = self._fix_id_column_order_after_multiplication(product, value_table)
        table = self._create(product)

        sorted_table = table.sort()
        return sorted_table

    def _reduce_data_frame(self, id_name, id_value_or_array):
        if isinstance(id_value_or_array, list):
            # keeps the id column
            return self._reduce_data_frame_by_id_array(id_name, id_value_or_array)
        else:
            id_value = int(id_value_or_array)
            return self._reduce_data_frame_by_id(id_name, id_value)

    def _reduce_data_frame_by_id(self, id_name, id_value):
        existing_values = self.unique_index_values(id_name)
        if id_value in existing_values:
            query = id_name + ' == ' + str(id_value)
            reduced_data_frame = self._data_frame.query(query)
            index_size = len(reduced_data_frame.index.names)
            if index_size > 1:
                reduced_data_frame = reduced_data_frame.droplevel(id_name)
            return reduced_data_frame
        else:
            return None

    # noinspection PyUnusedLocal
    def _reduce_data_frame_by_id_array(self, id_name, id_array):  # pylint: disable=unused-argument
        existing_values = self.unique_index_values(id_name)
        contains_value = Table._contains_any_value(id_array, existing_values)
        if contains_value:
            query = id_name + ' in @id_array'
            reduced_data_frame = self._data_frame.query(query)
            return reduced_data_frame
        else:
            return None

    # should be overridden by inheriting class, e.g. ValueTable
    def _convert_single_row_reduction_result(self, single_row_data_frame):
        # import needs to be here to avoid circular import dependencies
        from micat.series.annual_series import (  # pylint: disable=import-outside-toplevel
            AnnualSeries,
        )

        series = AnnualSeries(single_row_data_frame)
        return series

    def _validate_value_table_for_multiplication(self, value_table):
        if value_table.contains_nan():
            raise ValueError('Factor table must not include NaN values.')

        join_column_names = self._join_column_names(value_table)
        if len(join_column_names) > 0:
            data_index_tuples = self.unique_multi_index_tuples(join_column_names)
            value_index_tuples = value_table.unique_multi_index_tuples(join_column_names)
            for index_tuple in value_index_tuples:
                if index_tuple not in data_index_tuples:
                    message = 'Not all entries of the value table are used for multiplication: ' + str(index_tuple)
                    Logger.warn(message)

    def _join_column_names(self, other_table):
        id_column_names, _, _ = self.column_names
        other_id_column_names, _, _ = other_table.column_names
        join_column_names = list_utils.intersection(id_column_names, other_id_column_names)
        return join_column_names

    def _validate_factor_table_for_multiplication(self, factor_table):
        if factor_table.contains_nan():
            raise ValueError('Factor table must not include NaN values.')

        index_column_names, year_column_names, value_column_names = self.column_names
        factor_index_column_names, factor_year_column_names, factor_value_column_names = factor_table.column_names
        if factor_year_column_names != year_column_names:
            raise ValueError('Factor table must have the same year columns.')

        if factor_value_column_names != value_column_names:
            raise ValueError('Factor table must have the same value columns.')

        common_columns = list_utils.intersection(index_column_names, factor_index_column_names)
        if len(common_columns) > 0:
            message = (
                'Factor table must not have same index column(s). '
                + 'You might want to use normal multiplication using * operator or '
                + 'specify a factor_column_name.'
            )
            raise ValueError(message)

        if 'id_dummy' in index_column_names:
            raise KeyError('Table must not contain column "id_dummy" because it it used internally.')

        if 'id_dummy' in factor_index_column_names:
            raise KeyError('Factor table must not contain column "id_dummy" because it it used internally.')

    @property
    def first_row(self):
        series = self._data_frame.iloc[0]
        return series

    @property
    def rows(self):
        return self._data_frame.reset_index().values.tolist()

    @property
    def values(self):
        return self._data_frame.values

    @property
    def years(self):
        _, year_column_names, _ = self.column_names
        integer_years = list_utils.string_to_integer(year_column_names)
        return integer_years
