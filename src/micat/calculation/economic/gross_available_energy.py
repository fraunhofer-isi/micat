# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from micat.calculation.economic import eurostat, population, primes
from micat.table.table import merge_tables


def gross_available_energy(
    data_source,
    id_region,
    years,
    population_of_municipality=None,
):
    eurostat_primary_parameters = eurostat.primary_parameters(data_source, id_region, years)
    primes_primary_parameters = primes.primary_parameters(data_source, id_region, years)
    raw_gross_available_energy = merge_tables(
        eurostat_primary_parameters,
        primes_primary_parameters,
        False,
    )

    raw_gross_available_energy = raw_gross_available_energy.reduce("id_parameter", 2)

    scaled_gross_available_energy = population.scale_by_population(
        raw_gross_available_energy,
        population_of_municipality,
        data_source,
        id_region,
        years,
    )

    return scaled_gross_available_energy
