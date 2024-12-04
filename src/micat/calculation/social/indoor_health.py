# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.social import affected_dwellings

# pylint: disable=unused-variable


def avoided_excess_cold_weather_mortality_due_to_indoor_cold(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
):
    years = final_energy_saving_by_action_type.years

    where_clause = {'id_parameter': '26', 'id_region': str(id_region)}

    cold_weather_deaths_to_indoor_cold_per_household = data_source.annual_series_from_value(
        '26_53_54_55_excess_cold_weather_mortality_coefficients', years, where_clause
    )

    number_of_affected_buildings = affected_dwellings.determine_number_of_affected_dwellings(
        final_energy_saving_by_action_type, data_source, id_region
    )

    energy_poverty_targetedness_factor = 0.01 * data_source.annual_parameters_per_measure(
        final_energy_saving_by_action_type,
        '25_29_30_31_32_33_34_35_energy_poverty_coefficients',
        25,
        _provide_default_energy_poverty_targetedness_factor,
        id_region,
    ) #0.01 accout for value in %

    where_clause = {'id_parameter': '53', 'id_region': str(id_region)}

    medium_and_deep_renovations_share = data_source.annual_series_from_value(
        '26_53_54_55_excess_cold_weather_mortality_coefficients', years, where_clause
    )

    avoided_excess_cold_weather_deaths = (
        cold_weather_deaths_to_indoor_cold_per_household
        * number_of_affected_buildings
        * energy_poverty_targetedness_factor
        * medium_and_deep_renovations_share
    )

    del avoided_excess_cold_weather_deaths['id_subsector']
    del avoided_excess_cold_weather_deaths['id_action_type']

    return avoided_excess_cold_weather_deaths


def _provide_default_energy_poverty_targetedness_factor(
    id_region,
    id_parameter,
    _id_measure,
    _id_subsector,
    _id_action_type,
    year,
    _saving,
    default_parameters_table,
):
    parameter_specific_table = default_parameters_table.reduce('id_parameter', id_parameter)
    parameters_by_region = parameter_specific_table.reduce('id_region', id_region)
    value = parameters_by_region[str(year)]
    return value
