# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.table.table import AbstractTable


class IdTable(AbstractTable):
    def __init__(self, data_frame_or_array, name=None):
        data_frame = AbstractTable._construct_data_frame(data_frame_or_array)
        data_frame.set_index(["id"], inplace=True)
        data_frame.name = name
        super().__init__(data_frame)

    @staticmethod
    def from_json(custom_json, name=None):
        data_frame = AbstractTable._data_frame_from_json(custom_json)
        return IdTable(data_frame, name)

    @staticmethod
    def _create(data_frame_or_array):
        return IdTable(data_frame_or_array)

    @staticmethod
    def _check_if_all_labels_can_be_replaced(
        data_frame,
        column_name,
        mapping,
    ):
        source_series = data_frame[column_name]
        mapping_series = mapping[column_name]
        non_existing_labels = ~source_series.isin(mapping_series)
        contains_non_exiting_labels = non_existing_labels.any()
        if contains_non_exiting_labels:
            unmapped_label_values = set(source_series[non_existing_labels].values)
            message = "Table includes values for " + column_name + " that cant be mapped: " + str(unmapped_label_values)
            raise KeyError(message)

    def get(self, id_value):
        return self._data_frame.loc[id_value]

    def id_by_description(self, description):
        entry = self._data_frame.query('description == "' + description + '"')
        if entry.empty:
            message = "Id table " + self._data_frame.name + ' does not contain description "' + description + '"'
            raise KeyError(message)
        id_value = entry.index.values[0]
        return id_value

    def label(self, id_value):
        filtered_frame = self._data_frame.query("id == " + str(id_value))
        if filtered_frame.empty:
            message = "Id table " + self._data_frame.name + " does not contain id value " + str(id_value)
            raise KeyError(message)
        label = filtered_frame["label"].values[0]
        return label

    def label_to_id(self, source_data_frame, source_column_name):
        label_mapping = self._data_frame.reset_index()
        del label_mapping["description"]
        id_name = self._name

        # note: if we would keep the names, we would need to do more
        # postprocessing after the merge, e.g. delete extra, unwanted label column, also see
        # https://stackoverflow.com/questions/22208218/pandas-merge-columns-but-not-the-key-column
        label_mapping.rename(
            columns={
                "label": source_column_name,
                "id": id_name,
            },
            inplace=True,
        )

        IdTable._check_if_all_labels_can_be_replaced(source_data_frame, source_column_name, label_mapping)

        df = source_data_frame.merge(
            label_mapping,
            how="left",
            on=source_column_name,
            validate="many_to_one",
        )
        del df[source_column_name]

        return df

    def labels(self, ids):
        filtered_frame = self._data_frame.query("id in " + str(ids))
        labels = list(filtered_frame["label"].values)
        return labels

    @property
    def id_values(self):
        return list(self._data_frame.index.values)

    @property
    def _name(self):
        return self._data_frame.name
