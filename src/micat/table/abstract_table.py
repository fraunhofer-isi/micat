# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from sqlite3 import IntegrityError

import numpy as np
import pandas as pd

from micat.log.logger import Logger


class AbstractTable:
    def __init__(self, data_frame):
        if data_frame.empty:
            raise ValueError("Empty tables are not supported. Please provide non-empty data columns.")
        self._data_frame = data_frame

    @staticmethod
    def _apply_mapping_table(data_frame, mapping_table):
        source_column = mapping_table.source_column
        if source_column not in data_frame.columns:
            message = (
                'Source column "'
                + source_column
                + '" of mapping does not exist in dataframe. '
                + 'Maybe use "apply_reversely_for" instead of "apply_for"?'
            )
            raise KeyError(message)
        data_frame = AbstractTable._handle_unmapped_entries(data_frame, mapping_table)
        # noinspection PyProtectedMember
        result_data_frame = data_frame.merge(
            mapping_table._data_frame,  # pylint: disable=protected-access
            how="left",
            on=mapping_table.source_column,
        )
        del result_data_frame[mapping_table.source_column]
        return result_data_frame

    @staticmethod
    def _apply_mapping_table_reversely(data_frame, mapping_table):
        target_column = mapping_table.target_column
        if target_column not in data_frame.columns:
            message = (
                'Target column "'
                + target_column
                + '" of mapping does not exist in dataframe. '
                + 'Maybe use "apply_for" instead of "apply_reversely_for" ?'
            )
            raise KeyError(message)

        data_frame = AbstractTable._handle_unmapped_reverse_entries(data_frame, mapping_table)
        # noinspection PyProtectedMember
        result_data_frame = data_frame.merge(
            mapping_table._data_frame,  # pylint: disable=protected-access
            how="left",
            on=mapping_table.target_column,
        )
        del result_data_frame[mapping_table.target_column]
        return result_data_frame

    @staticmethod
    def _check_for_special_values_and_remove_them(df, dummy_value, table_name):
        contains_dummy_value = AbstractTable._contains(df, dummy_value)
        if contains_dummy_value:
            message = "Removing special values " + str(dummy_value) + " from table " + table_name
            Logger.debug(message)
            cleaned_df = AbstractTable._remove_rows_containing_value(df, dummy_value)
            return cleaned_df
        else:
            return df

    @staticmethod
    def _create(data_frame_or_array):
        return AbstractTable(data_frame_or_array)

    @staticmethod
    def _column_names(data_frame):
        id_column_names = []
        if AbstractTable._is_indexed(data_frame):
            id_column_names = list(data_frame.index.names)
        year_column_names = []
        value_column_names = []

        for column_name in data_frame.columns:
            if "id_" in str(column_name):
                id_column_names.append(column_name)
            else:
                if str(column_name).isdigit():
                    year_column_names.append(column_name)
                else:
                    value_column_names.append(column_name)
        return id_column_names, year_column_names, value_column_names

    @staticmethod
    def _construct_data_frame(data_frame_or_series_or_array):
        if isinstance(data_frame_or_series_or_array, pd.DataFrame):
            return data_frame_or_series_or_array
        else:
            return pd.DataFrame(data_frame_or_series_or_array)

    @staticmethod
    def _contains_inf(data_frame):
        return np.isinf(data_frame).values.any()

    @staticmethod
    def _contains_nan(data_frame):
        return data_frame.isnull().values.any()

    @staticmethod
    def _contains_object(data_frame):
        return (data_frame.dtypes == "object").any()

    @staticmethod
    def _contains(data_frame, value):
        return data_frame.isin([value]).any().any()

    @staticmethod
    def _data_frame_from_json(custom_json):
        headers = custom_json["headers"]
        rows = custom_json["rows"]
        if len(rows) < 1:
            Logger.warn("Creating empty table from json data.")

        data_frame = pd.DataFrame(
            columns=headers,
            data=rows,
        )

        return data_frame

    @staticmethod
    def _drop_if_exists(data_frame, column_name):
        if column_name in data_frame.columns:
            return data_frame.drop([column_name], axis=1)
        else:
            return data_frame

    @staticmethod
    def _enable_foreign_key_constraints(connection: object) -> object:
        # sqlite3 has the foreign key feature disabled by default and
        # pandas does not have an option to enable it automatically
        # => we do it here
        # Also see
        # https://stackoverflow.com/questions/
        # 75308818/pandas-to-sql-ignores-foreign-key-constrains-when-appending-to-sqlite-table/
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _handle_unmapped_entries(data_frame, mapping_table):
        source_column = mapping_table.source_column
        source_series = data_frame[source_column]
        non_existing_ids = ~source_series.isin(mapping_table.source_values)
        contains_non_exiting_ids = non_existing_ids.any()
        if contains_non_exiting_ids:
            unmapped_id_values = set(source_series[non_existing_ids].values)
            message = (
                "Dataframe includes id values for " + source_column + " that wont be mapped: " + str(unmapped_id_values)
            )
            Logger.warn(message)

            is_mapped_row = source_series.isin(mapping_table.source_values)
            data_frame = data_frame[is_mapped_row]
        return data_frame

    @staticmethod
    def _handle_unmapped_reverse_entries(data_frame, mapping_table):
        reverse_source_column = mapping_table.target_column
        reverse_source_series = data_frame[reverse_source_column]
        non_existing_ids = ~reverse_source_series.isin(mapping_table.target_values)
        contains_non_exiting_ids = non_existing_ids.any()
        if contains_non_exiting_ids:
            unmapped_id_values = set(reverse_source_series[non_existing_ids].values)
            message = (
                "Dataframe includes id values for "
                + reverse_source_column
                + " that wont be mapped: "
                + str(unmapped_id_values)
            )
            Logger.warn(message)

            is_mapped_row = reverse_source_series.isin(mapping_table.target_values)
            data_frame = data_frame[is_mapped_row]
        return data_frame

    @staticmethod
    def _has_multi_index(data_frame):
        has_multi_index = len(data_frame.index.names) > 1
        return has_multi_index

    @staticmethod
    def _is_indexed(data_frame):
        return data_frame.index.names[0] is not None

    @staticmethod
    def _other_value(other):
        # import is here to avoid circular dependency
        from micat.series.abstract_series import (  # pylint: disable=import-outside-toplevel
            AbstractSeries,
        )

        if isinstance(other, AbstractTable):
            # noinspection PyProtectedMember
            return other._data_frame  # pylint: disable=protected-access
        elif isinstance(other, AbstractSeries):
            # noinspection PyProtectedMember
            return other._series  # pylint: disable=protected-access
        else:
            return other

    @staticmethod
    def _remove_rows_containing_value(data_frame, value):
        row_contains_dummy_value = data_frame.isin([value]).any(axis=1)
        cleaned_data_frame = data_frame[~row_contains_dummy_value]
        return cleaned_data_frame

    def iterrows(self):
        # import is here to avoid circular import dependencies
        from micat.series.annual_series import (  # pylint: disable=import-outside-toplevel
            AnnualSeries,
        )

        for index, row_series in self._data_frame.iterrows():
            yield index, AnnualSeries(row_series)

    def set_values_by_index_table(
        self,
        indices_of_values_to_be_replaced,
        index_order,
        value,
    ):
        result_data_frame = self._data_frame.copy()
        for index, row_series in indices_of_values_to_be_replaced.iterrows():
            for column_name, index_tuple in row_series.items():
                index = self._create_index_entry(index_tuple, index_order)
                result_data_frame[column_name][index] = value
        return self._create(result_data_frame)

    def to_string(self):
        return self._data_frame.to_string()

    def to_sql(self, *args, **kwargs):
        connection = args[1]
        self._enable_foreign_key_constraints(connection)
        data_frame = self._data_frame
        if "id" not in data_frame.index.names:
            data_frame = data_frame.reset_index()

        try:
            data_frame.to_sql(*args, **kwargs)
        except IntegrityError as error:
            duplicated = self._data_frame[self._data_frame.index.duplicated()]
            Logger.warn("!! Duplicate entries in index !!")
            Logger.warn(duplicated)
            raise error

    def to_data_frame(self):
        return self._data_frame.copy()

    def __add__(self, other):
        self._validate_tables_for_add_operation(other)
        result_data_frame = self._data_frame + AbstractTable._other_value(other)
        return self._create(result_data_frame)

    def __delitem__(self, column_name):
        if column_name in self.columns:
            self._data_frame.__delitem__(column_name)
        else:
            id_names = self._data_frame.index.names
            if column_name in id_names:
                self._data_frame = self._data_frame.droplevel(column_name)
            else:
                raise KeyError('Unknown column "' + column_name + '"')

    def __eq__(self, obj):  # ==
        return self._data_frame == AbstractTable._other_value(obj)

    def __ge__(self, obj):  # >=
        return self._data_frame >= AbstractTable._other_value(obj)

    def __getitem__(self, key):  # implements [] access
        item = self._data_frame[key]
        if isinstance(item, pd.DataFrame):
            return self._create(item)
        else:
            return item

    def __gt__(self, obj):  # >
        return self._data_frame > AbstractTable._other_value(obj)

    def __invert__(self):
        result_data_frame = ~self._data_frame
        return self._create(result_data_frame)

    def __iter__(self):
        return self._data_frame.__iter__()

    def __le__(self, obj):  # <=
        return self._data_frame <= AbstractTable._other_value(obj)

    def __len__(self):
        return len(self._data_frame)

    def __lt__(self, obj):  # <
        return self._data_frame < AbstractTable._other_value(obj)

    def __ne__(self, obj):  # !=
        return self._data_frame != AbstractTable._other_value(obj)

    def __neg__(self):
        result_data_frame = -self._data_frame
        return self._create(result_data_frame)

    def __radd__(self, other):
        result_data_frame = self._data_frame + AbstractTable._other_value(other)
        return self._create(result_data_frame)

    def __repr__(self):
        return self._data_frame.__repr__()

    def __rmul__(self, other):
        result_data_frame = AbstractTable._other_value(other) * self._data_frame
        return self._create(result_data_frame)

    def __rsub__(self, other):
        result = AbstractTable._other_value(other) - self._data_frame
        if isinstance(result, pd.DataFrame):
            return self._create(result)
        else:
            raise ValueError("This subtraction is not yet implemented")

    def __rtruediv__(self, other):
        result_data_frame = AbstractTable._other_value(other) / self._data_frame
        return self._create(result_data_frame)

    def __setitem__(self, key, value):  # implements [] access
        self._data_frame[key] = value

    def __sub__(self, other):
        result_data_frame = self._data_frame - AbstractTable._other_value(other)
        return self._create(result_data_frame)

    def _create_index_entry(self, index_tuple, index_order):
        multi_index_value = []
        id_column_names, _, _ = self.column_names
        for id_column_name in id_column_names:
            if id_column_name in index_order:
                index = index_order.index(id_column_name)
                index_value = index_tuple[index]
                multi_index_value.append(index_value)

        if len(multi_index_value) > 1:
            return tuple(multi_index_value)
        else:
            return multi_index_value[0]

    def _fix_column_order_after_multiplication(self, data_frame):
        id_column_names = list(self.index.names)
        new_id_column_names = list(data_frame.index.names)
        for column_name in new_id_column_names:
            if column_name not in id_column_names:
                id_column_names.append(column_name)
        data_frame = data_frame.reset_index().set_index(id_column_names)
        return data_frame

    def _multi_index_lookup_for_column(self, column, index_order):
        column_result = column.apply(
            lambda index_value_or_tuple: self._multi_index_lookup_for_cell(
                index_value_or_tuple,
                column.name,
                index_order,
            ),
        )
        return column_result

    def _multi_index_lookup_for_cell(self, index_value_or_tuple, column_name, index_order):
        if isinstance(index_value_or_tuple, tuple):
            index_value = self._create_index_entry(index_value_or_tuple, index_order)
        else:
            index_value = index_value_or_tuple
        cell_result = self[column_name][index_value]
        return cell_result

    def _validate_tables_for_add_operation(self, other):
        left_index = self.index
        left_length = len(left_index)
        right_index = other.index
        right_length = len(right_index)
        if left_length != right_length:
            message = (
                "Tables must have same lengths but they are different ("
                + str(left_length)
                + " vs. "
                + str(right_length)
                + ")"
            )
            raise KeyError(message)

        left_index_values = list(left_index.values)
        left_index_values.sort()

        right_index_values = list(right_index.values)
        right_index_values.sort()

        if left_index_values != right_index_values:
            print("## left:")
            print(str(left_index_values))

            print("## right:")
            print(str(right_index_values))

            message = "Tables must have same index entries but they are different."
            raise KeyError(message)

    @property
    def a_preview(self):
        # the purpose of this is to help with debugging because
        # the custom type rendering feature of PyCharm does not seem to work
        # Also see
        # https://stackoverflow.com/questions/74195566/pycharm-community-editon-does-not-apply-custom-type-rendering
        return self._data_frame

    @property
    def column_names(self):
        return self._column_names(self._data_frame)

    @property
    def columns(self):
        return list(self._data_frame.columns)

    @property
    def index(self):
        return self._data_frame.index
