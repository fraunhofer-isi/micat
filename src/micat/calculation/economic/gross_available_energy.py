# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import eurostat, population, primes


def gross_available_energy(
    data_source,
    id_region,
    years,
    population_of_municipality=None,
):
    eurostat_primary_parameters = eurostat.primary_parameters(
        data_source, id_region, years
    )
    primes_primary_parameters = primes.primary_parameters(data_source, id_region, years)
    primes_primary_parameters._data_frame = (
        primes_primary_parameters._data_frame.combine_first(
            eurostat_primary_parameters._data_frame
        )
    )
    raw_gross_available_energy = primes_primary_parameters

    raw_gross_available_energy = raw_gross_available_energy.reduce("id_parameter", 2)

    scaled_gross_available_energy = population.scale_by_population(
        raw_gross_available_energy,
        population_of_municipality,
        data_source,
        id_region,
        years,
    )

    return scaled_gross_available_energy
