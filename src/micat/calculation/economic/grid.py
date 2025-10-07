# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/41
from micat.calculation.economic import eurostat, primes
from micat.table.table import merge_tables


def reduction_of_additional_capacities_in_grid(
    final_energy_saving_electricity,
    data_source,
    id_region,
):
    years = final_energy_saving_electricity.years
    capacity_reduction_factor = _capacity_reduction_factor(
        data_source,
        id_region,
        years,
    )
    product = final_energy_saving_electricity * capacity_reduction_factor

    del product["id_subsector"]
    del product["id_action_type"]
    return product


def monetization_of_reduction_of_additional_capacities_in_grid(
    reduction_of_additional_capacities,
    data_source,
):
    investment_costs_of_renewable_energy_system_technologies = data_source.parameter(
        "irena_technology_parameters",
        None,
        44,
    )

    product = reduction_of_additional_capacities * investment_costs_of_renewable_energy_system_technologies
    aggregated_product = product.aggregate_to("id_measure")
    return aggregated_product


def _capacity_reduction_factor(
    data_source,
    id_region,
    years,
):
    eurostat_res = eurostat.technology_parameters(
        data_source,
        id_region,
        years,
    )

    technology_parameters = primes.technology_parameters(
        data_source,
        id_region,
        years,
    )
    capacity_reduction_factor = merge_tables(
        eurostat_res,
        technology_parameters,
        False,
    )

    capacity_reduction_factor = capacity_reduction_factor.reduce("id_parameter", 47)
    return capacity_reduction_factor
