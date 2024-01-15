# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from calculation import air_pollution
from calculation.social import (
    air_quality,
    energy_poverty,
    health_impacts_monetization,
    indoor_health,
    lost_working_days_monetization,
)


def social_indicators(
    final_energy_saving_by_action_type,
    population_of_municipality,
    interim_data,
    data_source,
    id_mode,
    id_region,
):
    # pylint: disable-msg=too-many-locals
    air_pollution_parameters = interim_data['air_pollution_parameters']
    energy_saving_by_final_energy_carrier = interim_data['energy_saving_by_final_energy_carrier']
    reduction_of_energy_cost = interim_data['reduction_of_energy_cost']

    alleviation_of_energy_poverty_m2, alleviation_of_energy_poverty_2m = energy_poverty.alleviation_of_energy_poverty(
        final_energy_saving_by_action_type,
        population_of_municipality,
        reduction_of_energy_cost,
        data_source,
        id_mode,
        id_region,
    )

    reduction_of_lost_work_days_table = air_pollution.reduction_of_lost_work_days(
        air_pollution_parameters,
        energy_saving_by_final_energy_carrier,
    )

    lost_working_days_monetization_table = (
        lost_working_days_monetization.monetization_of_lost_working_days_due_to_air_pollution(
            reduction_of_lost_work_days_table,
            data_source,
            id_region,
        )
    )

    reduction_in_disability_adjusted_life_years_table = air_quality.reduction_in_disability_adjusted_life_years(
        final_energy_saving_by_action_type,
        data_source,
        id_region,
    )

    disability_adjusted_life_years_monetization_table = (
        health_impacts_monetization.monetization_of_health_costs_linked_to_dampness_and_mould_related_asthma_cases(
            reduction_in_disability_adjusted_life_years_table,
            data_source,
            id_region,
        )
    )

    avoided_excess_cold_weather_mortality_table = (
        indoor_health.avoided_excess_cold_weather_mortality_due_to_indoor_cold(
            final_energy_saving_by_action_type,
            data_source,
            id_region,
        )
    )

    excess_cold_weather_mortality_monetization_table = (
        health_impacts_monetization.monetization_of_cold_weather_mortality(
            avoided_excess_cold_weather_mortality_table,
            data_source,
            id_region,
        )
    )

    return {
        'alleviationOfEnergyPovertyM2': alleviation_of_energy_poverty_m2,
        'alleviationOfEnergyPoverty2M': alleviation_of_energy_poverty_2m,
        'reductionOfLostWorkDays': reduction_of_lost_work_days_table,
        'reductionOfLostWorkDaysMonetization': lost_working_days_monetization_table,
        'reductionInDisabilityAdjustedLifeYears': reduction_in_disability_adjusted_life_years_table,
        'reductionInDisabilityAdjustedLifeYearsMonetization': disability_adjusted_life_years_monetization_table,
        'avoidedExcessColdWeatherMortality': avoided_excess_cold_weather_mortality_table,
        'avoidedExcessColdWeatherMortalityMonetization': excess_cold_weather_mortality_monetization_table,
    }
