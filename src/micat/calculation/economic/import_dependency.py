# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/23


# pylint: disable=too-many-locals
def impact_on_import_dependency(
    primary_energy_saving_by_action_type,
    primary_production,
    gross_available_energy,
    primary_non_energy_use,
):
    filtered_primary_production = _filter_for_relevant_primary_energy_carriers(primary_production)
    filtered_gross_available_energy = _filter_for_relevant_primary_energy_carriers(gross_available_energy)
    filtered_primary_non_energy_use = _filter_for_relevant_primary_energy_carriers(primary_non_energy_use)
    filtered_primary_energy_saving_by_action_type = _filter_for_relevant_primary_energy_carriers(
        primary_energy_saving_by_action_type,
    )

    reference_table = _import_dependency(
        filtered_primary_production,
        filtered_gross_available_energy,
        filtered_primary_non_energy_use,
    )

    table = _import_dependency_with_savings(
        filtered_primary_production,
        filtered_gross_available_energy,
        filtered_primary_non_energy_use,
        filtered_primary_energy_saving_by_action_type,
    )
    difference = reference_table - table

    return difference


def _filter_for_relevant_primary_energy_carriers(table):
    # noinspection PyUnusedLocal
    id_values = [  # pylint: disable=unused-variable
        # Only oil, coal and gas should be considered here,
        # also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/23
        1,  # Oil
        2,  # Coal
        3,  # Gas
    ]
    filtered_df = table.reduce('id_primary_energy_carrier', id_values)
    return filtered_df


def _import_dependency(primary_production, gross_available_energy, primary_non_energy_use):
    result = 1 - primary_production / (gross_available_energy - primary_non_energy_use)
    return result


def _import_dependency_with_savings(
    primary_production,
    gross_available_energy,
    primary_non_energy_use,
    primary_energy_saving_by_action_type,
):
    primary_energy_saving_by_action_type = primary_energy_saving_by_action_type.aggregate_to(
        ['id_measure', 'id_primary_energy_carrier'],
    )
    reduced_gross_available_energy = gross_available_energy - primary_energy_saving_by_action_type
    result = 1 - primary_production / (reduced_gross_available_energy - primary_non_energy_use)
    return result
