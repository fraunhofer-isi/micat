# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import energy_cost
from micat.calculation.social import affected_dwellings, energy_poverty_national
from micat.table.table import Table, merge_tables


def alleviation_of_energy_poverty_on_eu_level(final_energy_saving_or_capacities, data_source, id_region):
    # pylint: disable-msg=too-many-locals
    if id_region != 0:
        raise ValueError("Energy poverty on EU level can only be calculated for id_region == 0.")

    population_table = _population_table(final_energy_saving_or_capacities, data_source)

    population_eu = population_table.reduce("id_region", 0)
    population_by_country = population_table.drop(0)

    eu_country_ids = population_by_country.index.values
    alleviation_of_energy_poverties_m2 = []
    alleviation_of_energy_poverties_2m = []
    for country_id in eu_country_ids:
        population_country = population_by_country.reduce("id_region", country_id)
        energy_savings_allocated_to_country = _energy_savings_allocated_to_country(
            final_energy_saving_or_capacities,
            population_country,
            population_eu,
        )
        number_of_affected_dwellings_allocated_to_country = _number_of_affected_dwellings_allocated_to_country(
            final_energy_saving_or_capacities,
            data_source,
            population_country,
            population_eu,
        )
        reduction_of_energy_cost = energy_cost.reduction_of_energy_cost(
            energy_savings_allocated_to_country,
            data_source,
            country_id,
        )
        alleviation_of_energy_poverty_m2 = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            energy_savings_allocated_to_country,
            population_country,
            reduction_of_energy_cost,
            data_source,
            country_id,
            False,
            number_of_affected_dwellings_allocated_to_country,
        )
        alleviation_of_energy_poverty_2m = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            energy_savings_allocated_to_country,
            population_country,
            reduction_of_energy_cost,
            data_source,
            country_id,
            True,
            number_of_affected_dwellings_allocated_to_country,
        )

        alleviation_of_energy_poverties_m2.append(alleviation_of_energy_poverty_m2)
        alleviation_of_energy_poverties_2m.append(alleviation_of_energy_poverty_2m)

    alleviation_of_energy_poverty_m2_per_country = Table.concat(alleviation_of_energy_poverties_m2)
    alleviation_of_energy_poverty_2m_per_country = Table.concat(alleviation_of_energy_poverties_2m)

    alleviation_of_energy_poverty_m2 = alleviation_of_energy_poverty_m2_per_country.aggregate_to(["id_measure"])
    alleviation_of_energy_poverty_2m = alleviation_of_energy_poverty_2m_per_country.aggregate_to(["id_measure"])
    return alleviation_of_energy_poverty_m2, alleviation_of_energy_poverty_2m


def _population_table(final_energy_saving_or_capacities, data_source):
    eurostat = data_source.table("eurostat_parameters", {"id_parameter": "24"})
    primes = data_source.table("primes_parameters", {"id_parameter": "24"})
    population_table = merge_tables(eurostat, primes, False).reduce("id_parameter", 24)
    joined_years = population_table.columns + list(
        set(final_energy_saving_or_capacities.columns) - set(population_table.columns)
    )
    population_table = population_table.reindex(columns=joined_years)
    population_table = population_table.fill_nan_values_by_extrapolation()
    population_table = population_table.reindex(columns=final_energy_saving_or_capacities.columns)
    return population_table


def _energy_savings_allocated_to_country(
    final_energy_saving_or_capacities,
    population_country,
    population_eu,
):
    energy_savings_allocated_to_country = final_energy_saving_or_capacities * population_country / population_eu
    return energy_savings_allocated_to_country


def _number_of_affected_dwellings_allocated_to_country(
    final_energy_saving_or_capacities,
    data_source,
    population_country,
    population_eu,
):
    number_of_affected_dwellings_eu = affected_dwellings.determine_number_of_affected_dwellings(
        final_energy_saving_or_capacities, data_source, 0
    )
    number_of_affected_dwellings_allocated_to_country = (
        number_of_affected_dwellings_eu * population_country / population_eu
    )
    return number_of_affected_dwellings_allocated_to_country
