# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/31

from micat.calculation.economic import investment


def additional_employment(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
):
    annual_investment_cost_in_euro = investment.annual_investment_cost_in_euro(
        final_energy_saving_by_action_type,
        data_source,
    )

    action_type_ids = final_energy_saving_by_action_type.unique_index_values('id_action_type')

    e3m_parameters = data_source.table(
        'e3m_parameters',
        {
            'id_region': str(id_region),
            'id_action_type': action_type_ids,
        },
    )
    employment_coefficient_in_number_per_euro = e3m_parameters.reduce('id_parameter', 39)

    extra_employment = annual_investment_cost_in_euro * employment_coefficient_in_number_per_euro
    del extra_employment['id_action_type']

    return extra_employment
