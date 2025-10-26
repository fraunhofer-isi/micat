# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/31

from micat.calculation.economic import investment


def additional_employment(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
):
    action_type_ids = final_energy_saving_or_capacities.unique_index_values("id_action_type")
    subsector_ids = final_energy_saving_or_capacities.unique_index_values("id_subsector")
    annual_investment_cost_in_euro = investment.annual_investment_cost_in_euro(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    )

    table_name = "e3m_parameters"
    where_clause = {
        "id_region": str(id_region),
        "id_action_type": action_type_ids,
    }
    if action_type_ids[0] >= 30:
        table_name = "e3m_parameters_res"
        where_clause["id_subsector"] = subsector_ids

    e3m_parameters = data_source.table(
        table_name,
        where_clause,
    )
    employment_coefficient_in_number_per_euro = e3m_parameters.reduce("id_parameter", 39)

    extra_employment = annual_investment_cost_in_euro * employment_coefficient_in_number_per_euro
    del extra_employment["id_action_type"]

    return extra_employment
