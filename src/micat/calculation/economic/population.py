# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def population_of_municipality(measure):
    population = None
    if 'population' in measure:
        population = int(measure['population'])
    return population


def scale_by_population(
    value_or_table,
    optional_population_of_municipality,
    data_source,
    id_region,
    year_or_years,
):
    if optional_population_of_municipality is None:
        return value_or_table

    population_for_region = _population_for_region(data_source, id_region, year_or_years)
    scaled__value_or_table = value_or_table * optional_population_of_municipality / population_for_region
    return scaled__value_or_table


def _population_for_region(
    data_source,
    id_region,
    year_or_years,
):
    primes_parameters = data_source.table('primes_parameters', {'id_region': str(id_region)})
    raw_population = primes_parameters.reduce('id_parameter', 24)

    if isinstance(year_or_years, list):
        years = year_or_years
        population = extrapolation.extrapolate_series(raw_population, years)
    else:
        year = year_or_years
        population = raw_population[str(year)]
    return population
