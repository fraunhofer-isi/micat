# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def monetize(
    reduction_of_greenhouse_gas_emission,
    database,
    id_region,
):
    years = reduction_of_greenhouse_gas_emission.years
    monetization_factors = _monetization_factors(database, id_region, years)

    monetization = reduction_of_greenhouse_gas_emission * monetization_factors

    return monetization


def _monetization_factors(database, id_region, years):
    where_clause = {'id_region': str(id_region)}
    raw_monetization_factors = database.annual_series(
        'iiasa_greenhouse_gas_emission_monetization_factors',
        where_clause,
    )
    monetization_factors = extrapolation.extrapolate_series(raw_monetization_factors, years)
    return monetization_factors
