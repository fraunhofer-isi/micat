# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later


def measure_specific_lifetime(
    final_energy_saving_or_capacities,
    data_source,
):
    subsector_ids = final_energy_saving_or_capacities.unique_index_values("id_subsector")
    action_type_ids = final_energy_saving_or_capacities.unique_index_values("id_action_type")
    default_lifetime = _default_lifetime(data_source, subsector_ids, action_type_ids)

    def provide_default_lifetime(_id_measure, id_subsector, id_action_type, _savings):
        value = default_lifetime["value"][id_subsector, id_action_type]
        return value

    id_parameter = 36  # lifetime
    lifetime = data_source.measure_specific_parameter(
        final_energy_saving_or_capacities,
        id_parameter,
        provide_default_lifetime,
        is_value_table=True,
    )
    del lifetime["id_subsector"]
    del lifetime["id_action_type"]

    return lifetime


def _default_lifetime(
    data_source,
    subsector_ids,
    action_type_ids,
):
    where_clause = {
        "id_subsector": subsector_ids,
        "id_action_type": action_type_ids,
    }
    wuppertal_sector_parameters = data_source.table("wuppertal_sector_parameters", where_clause)
    lifetime = wuppertal_sector_parameters.reduce("id_parameter", [36])
    del lifetime["id_parameter"]
    return lifetime
