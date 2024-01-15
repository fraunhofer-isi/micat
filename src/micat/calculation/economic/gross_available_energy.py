# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import mode
from micat.calculation.economic import eurostat, population, primes


def gross_available_energy(
    data_source,
    id_mode,
    id_region,
    years,
    population_of_municipality=None,
):
    if mode.is_eurostat_mode(id_mode):
        eurostat_primary_parameters = eurostat.primary_parameters(data_source, id_region, years)
        raw_gross_available_energy = eurostat_primary_parameters.reduce('id_parameter', 2)
    else:
        primes_primary_parameters = primes.primary_parameters(data_source, id_region, years)
        raw_gross_available_energy = primes_primary_parameters.reduce('id_parameter', 2)

    scaled_gross_available_energy = population.scale_by_population(
        raw_gross_available_energy,
        population_of_municipality,
        data_source,
        id_region,
        years,
    )

    return scaled_gross_available_energy
