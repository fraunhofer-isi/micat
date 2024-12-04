# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.social import affected_dwellings


def reduction_in_disability_adjusted_life_years(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
):
    years = final_energy_saving_by_action_type.years

    daly_per_damp_and_mouldy_building_ratio = _daly_per_damp_and_mouldy_building_ratio(
        data_source,
        id_region,
        years,
    )

    medium_and_deep_renovations_share = _medium_and_deep_renovations_share(
        data_source,
        id_region,
        years,
    )

    damp_and_mouldy_buildings_targetedness_factor = _damp_and_mouldy_buildings_targetedness_factor(
        data_source,
        id_region,
        years,
    )

    number_of_affected_buildings = affected_dwellings.determine_number_of_affected_dwellings(
        final_energy_saving_by_action_type, data_source, id_region
    )

    reduction_in_disability_adjusted_life_years_due_to_air_quality = (
        daly_per_damp_and_mouldy_building_ratio
        * number_of_affected_buildings
        * medium_and_deep_renovations_share
        * damp_and_mouldy_buildings_targetedness_factor
    )

    return reduction_in_disability_adjusted_life_years_due_to_air_quality


def _daly_per_damp_and_mouldy_building_ratio(data_source, id_region, years):
    where_clause = {'id_region': str(id_region), 'id_parameter': '55'}
    daly_per_damp_and_mouldy_building_ratio = data_source.annual_series_from_value(
        '26_53_54_55_excess_cold_weather_mortality_coefficients',
        years,
        where_clause,
    )
    return daly_per_damp_and_mouldy_building_ratio


def _medium_and_deep_renovations_share(data_source, id_region, years):
    where_clause = {'id_region': str(id_region), 'id_parameter': '53'}
    medium_and_deep_renovations_share = data_source.annual_series_from_value(
        '26_53_54_55_excess_cold_weather_mortality_coefficients',
        years,
        where_clause,
    )
    return medium_and_deep_renovations_share


def _damp_and_mouldy_buildings_targetedness_factor(
    data_source,
    id_region,
    years,
):
    where_clause = {'id_region': str(id_region), 'id_parameter': '54'}
    damp_and_mouldy_buildings_targetedness_factor = 0.01 * data_source.annual_series_from_value(
        '26_53_54_55_excess_cold_weather_mortality_coefficients',
        years,
        where_clause,
    )
    return damp_and_mouldy_buildings_targetedness_factor
