# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

from micat.calculation import extrapolation
from micat.table.table import Table


class PopulationUtils:
    @staticmethod
    def extend_european_values(table, database):
        years = table.years
        population = PopulationUtils._population(database, years)
        european_population = PopulationUtils._european_population(population)
        population_without_europe = population.query('id_region != 0')

        european_table = PopulationUtils._european_table(
            table,
            population_without_europe,
            european_population,
        )

        extended_table = Table.concat([table, european_table])
        return extended_table

    @staticmethod
    def _european_table(table, population, european_population):
        product = table * population
        aggregated_product = product.aggregate('id_region')
        if isinstance(aggregated_product, pd.Series):
            raise NotImplementedError
        european_table = 1 / european_population * aggregated_product
        european_table = european_table.insert_index_column('id_region', 0, 0)
        return european_table

    @staticmethod
    def _european_population(population):
        european_population_series = population.reduce('id_region', 0)
        return european_population_series

    @staticmethod
    def _population(database, years=None):
        eurostat_parameters = database.table('eurostat_parameters', {})
        eurostat_population = eurostat_parameters.reduce('id_parameter', 24)

        primes_parameters = database.table('primes_parameters', {})
        primes_population = primes_parameters.reduce('id_parameter', 24)
        future_population = primes_population[['2025', '2030', '2035', '2040', '2045', '2050']]
        population = Table.concat_years([eurostat_population, future_population])

        if years:
            extrapolated_population = extrapolation.extrapolate(population, years)
            return extrapolated_population
        else:
            return population
