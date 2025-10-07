# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.log.logger import Logger
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table


class TableValidator:
    def __init__(self, database):
        self._database = database

    @staticmethod
    def _check_if_ids_are_present(
        table,
        id_name,
        available_id_values,
        id_table,
        details,
    ):
        missing_id_entries = []
        existing_id_values = table.unique_index_values(id_name)
        if existing_id_values != available_id_values:
            missing_id_entries = TableValidator._missing_id_entries(
                id_name,
                available_id_values,
                id_table,
                details,
                existing_id_values,
            )

        return set(existing_id_values), missing_id_entries

    @staticmethod
    def _missing_id_entries(
        id_name,
        available_id_values,
        id_table,
        details,
        existing_id_values,
    ):
        missing_id_entries = []
        message = "Missing entries for " + id_name
        if details != {}:
            message += " under " + str(details) + ":\n"

        for existing_id_value in existing_id_values:
            if existing_id_value not in available_id_values:
                message += "Unknown id value: " + str(existing_id_value) + "\n"

        for available_id_value in available_id_values:
            if available_id_value not in existing_id_values:
                id_series = id_table.get(available_id_value)
                missing_id_entry = (id_series.name, id_series["label"])
                missing_id_entries.append(missing_id_entry)
                message += str(missing_id_entry) + "\n"

        Logger.warn(message)
        return missing_id_entries

    @staticmethod
    def _include_missing_id_entries(
        missing_entries,
        parent_details,
        id_name,
        missing_id_entries,
    ):
        for missing_id_entry in missing_id_entries:
            missing_entry = parent_details.copy()
            missing_entry[id_name] = missing_id_entry
            missing_entries.append(missing_entry)
        return missing_entries

    def validate(self, table, details={}, missing_entries=[]):  # pylint: disable=dangerous-default-value
        id_column_names, _year_column_names, _ = table.column_names
        if "id_region" in id_column_names:
            missing_entries = self._validate_id_region_and_below(table, details, missing_entries)
        elif "id_parameter" in id_column_names:
            missing_entries = self._validate_id_parameter_and_below(table, details, missing_entries)
        elif "id_subsector" in id_column_names:
            missing_entries = self._validate_id_subsector_and_below(table, details, missing_entries, id_column_names)
        elif "id_final_energy_carrier" in id_column_names:
            missing_entries = self._validate_id_final_energy_carrier(table, details, missing_entries)
        elif "id_primary_energy_carrier" in id_column_names:
            missing_entries = self._validate_id_primary_energy_carrier(table, details, missing_entries)
        return missing_entries

    def _check_if_id_is_complete(self, table, id_name, details):
        id_table = self._database.id_table(id_name)
        available_id_values = id_table.id_values
        return self._check_if_ids_are_present(
            table,
            id_name,
            available_id_values,
            id_table,
            details,
        )

    def _action_type_ids(self, id_subsector):
        mapping_table = self._database.mapping_table("mapping__subsector__action_type")
        action_type_ids = mapping_table.target_ids(id_subsector)
        return action_type_ids

    def _include_missing_sub_entries_for_subsector(
        self,
        missing_entries,
        id_subsector,
        parent_details,
        id_column_names,
    ):
        if "id_action_type" in id_column_names:
            action_type_ids = self._action_type_ids(id_subsector)
            id_action_type_table = self._database.id_table("id_action_type")
            for id_action_type in action_type_ids:
                action_type_label = id_action_type_table.label(id_action_type)
                details = parent_details.copy()
                details["id_action_type"] = (id_action_type, action_type_label)
                missing_entries = self._include_missing_sub_entries_for_action_type(
                    missing_entries,
                    details,
                    id_column_names,
                )
        else:
            missing_entries = self._include_missing_sub_entries_for_action_type(
                missing_entries,
                parent_details,
                id_column_names,
            )

        return missing_entries

    def _include_missing_sub_entries_for_action_type(
        self,
        missing_entries,
        parent_details,
        id_column_names,
    ):
        if "id_final_energy_carrier" in id_column_names:
            id_table = self._database.id_table("id_final_energy_carrier")
            id_values = id_table.id_values
            for id_value in id_values:
                id_label = id_table.label(id_value)
                entry = parent_details.copy()
                entry["id_final_energy_carrier"] = (id_value, id_label)
                missing_entries.append(entry)
        elif "id_primary_energy_carrier" in id_column_names:
            id_table = self._database.id_table("id_primary_energy_carrier")
            id_values = id_table.id_values
            for id_value in id_values:
                id_label = id_table.label(id_value)
                entry = parent_details.copy()
                entry["id_primary_energy_carrier"] = (id_value, id_label)
                missing_entries.append(entry)

        return missing_entries

    def _validate_id_action_type_and_below(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        table,
        available_id_values,
        parent_details,
        id_column_names,
        missing_entries,
    ):
        id_action_type_table = self._database.id_table("id_action_type")
        ids, missing_id_entries = self._check_if_ids_are_present(
            table,
            "id_action_type",
            available_id_values,
            id_action_type_table,
            parent_details,
        )

        for id_entry in missing_id_entries:
            id_action_type = id_entry[0]
            action_type_label = id_entry[1]
            details = parent_details.copy()
            details["id_action_type"] = (id_action_type, action_type_label)
            missing_entries = self._include_missing_sub_entries_for_action_type(
                missing_entries,
                details,
                id_column_names,
            )

        current_id_column_names, _, _ = table.column_names

        if len(current_id_column_names) > 1:
            for id_action_type in ids:
                action_table = table.reduce("id_action_type", [id_action_type])
                del action_table["id_action_type"]
                label = id_action_type_table.label(id_action_type)
                details = parent_details.copy()
                details["id_action_type"] = (id_action_type, label)
                missing_entries = self.validate(action_table, details, missing_entries)

        return missing_entries

    def _validate_id_final_energy_carrier(
        self,
        table,
        details,
        missing_entries,
    ):
        _ids, missing_id_entries = self._check_if_id_is_complete(table, "id_final_energy_carrier", details)
        missing_entries = TableValidator._include_missing_id_entries(
            missing_entries,
            details,
            "id_final_energy_carrier",
            missing_id_entries,
        )
        return missing_entries

    def _validate_id_primary_energy_carrier(
        self,
        table,
        details,
        missing_entries,
    ):
        _ids, missing_id_entries = self._check_if_id_is_complete(table, "id_primary_energy_carrier", details)
        missing_entries = TableValidator._include_missing_id_entries(
            missing_entries,
            details,
            "id_primary_energy_carrier",
            missing_id_entries,
        )
        return missing_entries

    def _validate_id_region_and_below(self, table, parent_details, missing_entries):
        # all values of id_region must be present
        id_region_table = self._database.id_table("id_region")
        available_region_ids = id_region_table.id_values
        existing_region_ids, missing_id_entries = self._check_if_id_is_complete(
            table,
            "id_region",
            parent_details,
        )
        id_column_names, _, _ = table.column_names
        id_column_names.remove("id_region")
        if len(id_column_names) > 0:
            for id_region in available_region_ids:
                if id_region in existing_region_ids:
                    region_table = table.reduce("id_region", [id_region])
                    del region_table["id_region"]
                    label = id_region_table.label(id_region)

                    details = parent_details.copy()
                    details["id_region"] = (id_region, label)

                    missing_entries = self.validate(region_table, details, missing_entries)
                else:
                    message = (
                        "The id_region "
                        + str(id_region)
                        + " is not used. "
                        + "It won´t be added to the autogenerated list of missing rows and "
                        + "has to be manually added."
                    )
                    print(message)
                    #  missing entries have to be created manually because
                    #  we do not want to loop over all values of id_parameter
                    continue
        else:
            missing_entries = TableValidator._include_missing_id_entries(
                missing_entries,
                parent_details,
                "id_region",
                missing_id_entries,
            )

        return missing_entries

    def _validate_id_parameter_and_below(
        self,
        table,
        parent_details,
        missing_entries,
    ):
        # not all values of id_parameter must be present but its
        # sub tables must be complete

        id_parameter_table = self._database.id_table("id_parameter")
        parameter_ids = table.unique_index_values("id_parameter")
        for id_parameter in parameter_ids:
            parameter_table_or_series_or_value = table.reduce("id_parameter", id_parameter)
            if not isinstance(parameter_table_or_series_or_value, Table):
                continue
            parameter_table = parameter_table_or_series_or_value

            label = id_parameter_table.label(id_parameter)
            details = parent_details.copy()
            details["id_parameter"] = (id_parameter, label)
            missing_entries = self.validate(parameter_table, details, missing_entries)

        return missing_entries

    def _validate_id_subsector_and_below(
        self,
        table,
        parent_details,
        missing_entries,
        id_column_names,
    ):  # pylint: disable=too-many-locals
        # all values of id_subsector must be present

        id_subsector_table = self._database.id_table("id_subsector")
        available_subsector_ids = id_subsector_table.id_values
        existing_subsector_ids, missing_id_entries = self._check_if_id_is_complete(
            table,
            "id_subsector",
            parent_details,
        )
        for id_subsector in available_subsector_ids:
            subsector_label = id_subsector_table.label(id_subsector)
            details = parent_details.copy()
            details["id_subsector"] = (id_subsector, subsector_label)

            if id_subsector in existing_subsector_ids:
                subsector_table_or_series = table.reduce("id_subsector", id_subsector)

                if "id_action_type" in id_column_names:
                    action_type_ids = self._action_type_ids(id_subsector)
                    missing_entries = self._validate_id_action_type_and_below(
                        subsector_table_or_series,
                        action_type_ids,
                        details,
                        id_column_names,
                        missing_entries,
                    )
                else:
                    if isinstance(subsector_table_or_series, AnnualSeries):
                        missing_entries = TableValidator._include_missing_id_entries(
                            missing_entries,
                            parent_details,
                            "id_subsector",
                            missing_id_entries,
                        )
                    else:
                        details = parent_details.copy()
                        details["id_subsector"] = (id_subsector, subsector_label)
                        missing_entries = self.validate(
                            subsector_table_or_series,
                            details,
                            missing_entries,
                        )

            else:
                missing_entries = self._include_missing_sub_entries_for_subsector(
                    missing_entries,
                    id_subsector,
                    details,
                    id_column_names,
                )

        return missing_entries
