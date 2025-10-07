# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.table.table import AbstractTable


class MappingTable(AbstractTable):
    # Maps from source column (id or label) to target id column.
    # Several source values might be mapped to several target values:
    # many to many, many to one, one to many, one to one.
    # Therefore, the source id might not be unique.
    # Therefore, all mapping tables must include a primary key column 'id'
    #
    # Mapping tables must not contain missing/null values.
    # If you would like to denote that a source value should not be mapped,
    # use following special entries in the imported Excel file:
    #  -99: redundant
    # -999: unmapped
    # Those are automatically removed.

    def __init__(self, indexed_data_frame, name=None):
        data_frame = self._validate_and_filter(indexed_data_frame, name)
        data_frame.name = name
        super().__init__(data_frame)

    @staticmethod
    def from_json(custom_json, name=None):
        data_frame = AbstractTable._data_frame_from_json(custom_json)
        data_frame.set_index(["id"], inplace=True)
        return MappingTable(data_frame, name)

    @staticmethod
    def _create(data_frame_or_array):
        return MappingTable(data_frame_or_array)

    @staticmethod
    def _check_for_special_values_and_remove_them(data_frame, name):
        data_frame = AbstractTable._check_for_special_values_and_remove_them(
            data_frame, -99, name
        )  # -99: redundant
        data_frame = AbstractTable._check_for_special_values_and_remove_them(
            data_frame, -999, name
        )  # -999: unmapped
        return data_frame

    @staticmethod
    def _validate_and_filter(indexed_data_frame, name):
        MappingTable._validate_index(indexed_data_frame)
        data_frame = MappingTable._check_for_special_values_and_remove_them(
            indexed_data_frame, name
        )
        MappingTable._validate_entries(data_frame)
        return data_frame

    @staticmethod
    def _validate_entries(data_frame):
        if AbstractTable._contains_nan(data_frame):
            message = (
                "Input for mapping table must not include NaN/Null/missing values."
                + "Use special values instead (-99: redundant, -999: unmapped)."
            )
            raise ValueError(message)

    @staticmethod
    def _validate_index(data_frame):
        if list(data_frame.index.names) != ["id"]:
            message = 'Input for mapping table must include a column "id" that serves as primary key.'
            raise ValueError(message)

    def apply_for(self, table_or_data_frame):
        data_frame = AbstractTable._other_value(table_or_data_frame)
        if AbstractTable._has_multi_index(data_frame):
            data_frame = data_frame.reset_index()
        df = AbstractTable._apply_mapping_table(data_frame, self)
        return df

    def apply_reversely_for(self, table_or_data_frame):
        data_frame = AbstractTable._other_value(table_or_data_frame)
        if AbstractTable._has_multi_index(data_frame):
            data_frame = data_frame.reset_index()
        df = AbstractTable._apply_mapping_table_reversely(data_frame, self)
        return df

    def single_target_id(self, source_value):
        target_ids = self.target_ids(source_value)
        if len(target_ids) < 1:
            raise ValueError("Unknown source value " + source_value)

        if len(target_ids) > 1:
            raise ValueError(
                "Source value "
                + source_value
                + " is mapped to more then one target values."
            )

        id_subsector = target_ids[0]
        return id_subsector

    def target_ids(self, source_value):
        query = self._target_query(source_value)
        sub_frame = self._data_frame.query(query)
        ids = list(sub_frame[self.target_column].values)
        return ids

    def _target_query(self, source_value):
        query = self.source_column + "=="
        if isinstance(source_value, str):
            query += '"' + source_value + '"'
        else:
            query += str(source_value)
        return query

    @property
    def source_column(self):
        return self.columns[0]

    @property
    def source_values(self):
        source_series = self._data_frame[self.source_column]
        values = list(source_series.values)
        return values

    @property
    def target_column(self):
        return self.columns[1]

    @property
    def target_values(self):
        target_series = self._data_frame[self.target_column]
        values = list(target_series.values)
        return values
