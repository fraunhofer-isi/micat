# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from calculation.social import energy_poverty_eu, energy_poverty_national


def alleviation_of_energy_poverty(
    final_energy_saving_by_action_type,
    population_of_municipality,
    reduction_of_energy_cost,
    data_source,
    id_mode,
    id_region,
):
    if id_region == 0:
        (
            alleviation_of_energy_poverty_m2,
            alleviation_of_energy_poverty_2m,
        ) = energy_poverty_eu.alleviation_of_energy_poverty_on_eu_level(
            final_energy_saving_by_action_type,
            data_source,
            id_mode,
            id_region,
        )
    else:
        alleviation_of_energy_poverty_m2 = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            final_energy_saving_by_action_type,
            population_of_municipality,
            reduction_of_energy_cost,
            data_source,
            id_region,
        )

        alleviation_of_energy_poverty_2m = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            final_energy_saving_by_action_type,
            population_of_municipality,
            reduction_of_energy_cost,
            data_source,
            id_region,
            True,
        )
    return alleviation_of_energy_poverty_m2, alleviation_of_energy_poverty_2m
