# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

def monetization_of_health_costs_linked_to_dampness_and_mould_related_asthma_cases(
    reduction_in_disability_adjusted_life_years,
    data_source,
    id_region,
):
    years = reduction_in_disability_adjusted_life_years.years
    value_of_life_years = _value_of_life_years(data_source, id_region, years)
    monetization = reduction_in_disability_adjusted_life_years * value_of_life_years
    return monetization


def _value_of_life_years(data_source, id_region, years):
    where_clause = {'id_region': str(id_region), 'id_parameter': '56'}
    value_of_life_years = data_source.extrapolated_annual_series('37_56_VSL_VOLY_monetisation', years, where_clause)
    return value_of_life_years


def monetization_of_cold_weather_mortality(
    avoided_excess_cold_weather_mortality_table,
    data_source,
    id_region,
):
    years = avoided_excess_cold_weather_mortality_table.years
    value_of_statistical_life = _value_of_statistical_life(
        data_source,
        id_region,
        years,
    )
    monetization = avoided_excess_cold_weather_mortality_table * value_of_statistical_life
    return monetization


def _value_of_statistical_life(data_source, id_region, years):
    where_clause = {'id_region': str(id_region), 'id_parameter': '37'}
    value_of_statistical_life = data_source.extrapolated_annual_series('37_56_VSL_VOLY_monetisation', years, where_clause)
    return value_of_statistical_life
