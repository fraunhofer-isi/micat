# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from test_utils.mock import Mock, patch

from calculation import air_pollution
from calculation.social import (
    air_quality,
    calculation_social,
    energy_poverty,
    health_impacts_monetization,
    indoor_health,
    lost_working_days_monetization,
)


@patch(
    energy_poverty.alleviation_of_energy_poverty,
    ('mocked_alleviation_of_energy_poverty_m2', 'mocked_alleviation_of_energy_poverty_2m'),
)
@patch(air_pollution.reduction_of_lost_work_days)
@patch(lost_working_days_monetization.monetization_of_lost_working_days_due_to_air_pollution)
@patch(lost_working_days_monetization.monetization_of_lost_working_days_due_to_air_pollution)
@patch(air_quality.reduction_in_disability_adjusted_life_years)
@patch(health_impacts_monetization.monetization_of_health_costs_linked_to_dampness_and_mould_related_asthma_cases)
@patch(indoor_health.avoided_excess_cold_weather_mortality_due_to_indoor_cold)
@patch(health_impacts_monetization.monetization_of_cold_weather_mortality)
def test_social_indicators():
    mocked_interim_data = Mock()

    result = calculation_social.social_indicators(
        'mocked_final_energy_saving_by_action_type',
        'mocked_population_of_municipality',
        mocked_interim_data,
        'mocked_data_source',
        'mocked_id_mode',
        'mocked_id_region',
    )
    assert len(result) == 8
