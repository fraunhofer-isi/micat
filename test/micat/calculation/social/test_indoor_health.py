# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np

from micat.calculation.social import affected_dwellings, indoor_health
from micat.series import annual_series
from micat.table import table
from micat.test_utils.isi_mock import Mock, patch

# pylint: disable=protected-access


def _mocked_table():
    mocked_table = Mock()
    mocked_table.reduce = Mock(return_value='mocked_reduce')
    return mocked_table


def _mocked_data_source():
    mocked_data_source = Mock()
    mocked_data_source.annual_parameters_per_measure = Mock(return_value=_mocked_annual_parameters_per_measure())
    mocked_data_source.annual_series_from_value = Mock(return_value=_mocked_annual_series(2))
    return mocked_data_source


def _mocked_annual_series(value):
    mocked_annual_series = annual_series.AnnualSeries({'2020': value, '2025': value, '2030': value})
    return mocked_annual_series


def _mocked_annual_parameters_per_measure():
    mocked_annual_parameters_per_measure = table.Table(
        [
            {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 1, '2020': 1, '2025': 1, '2030': 1},
            {'id_measure': 2, 'id_subsector': 2, 'id_action_type': 2, '2020': 2, '2025': 2, '2030': 2},
        ]
    )
    return mocked_annual_parameters_per_measure


def _mocked_final_energy_savings_by_action_type():
    mocked_final_energy_savings_by_action_type = table.Table(
        [
            {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 1, '2020': 10, '2025': 20, '2030': 30},
            {'id_measure': 2, 'id_subsector': 2, 'id_action_type': 2, '2020': 100, '2025': 200, '2030': 300},
        ]
    )
    return mocked_final_energy_savings_by_action_type


def _mocked_parameters_table():
    mocked_parameters_by_region = table.Table(
        [
            {'id_region': 1, 'id_parameter': 1, 'id_action_type': 1, '2020': 10, '2025': 20, '2030': 30},
            {'id_region': 1, 'id_parameter': 1, 'id_action_type': 2, '2020': 40, '2025': 50, '2030': 60},
            {'id_region': 2, 'id_parameter': 2, 'id_action_type': 1, '2020': 100, '2025': 200, '2030': 300},
            {'id_region': 2, 'id_parameter': 2, 'id_action_type': 2, '2020': 400, '2025': 500, '2030': 600},
        ]
    )
    return mocked_parameters_by_region


@patch(
    affected_dwellings.determine_number_of_affected_dwellings,
    Mock(return_value=_mocked_annual_parameters_per_measure()),
)
def test_avoided_excess_cold_weather_mortality_due_to_indoor_cold():
    result = indoor_health.avoided_excess_cold_weather_mortality_due_to_indoor_cold(
        _mocked_final_energy_savings_by_action_type(), _mocked_data_source(), 1
    )
    assert np.all(result.values[0] == 0.04)
    assert np.all(result.values[1] == 0.16)


def test_provide_default_energy_poverty_targetedness_factor():
    result = indoor_health._provide_default_energy_poverty_targetedness_factor(
        2,
        2,
        'mocked_id_measure',
        'mocked_id_subsector',
        'mocked_id_action_type',
        2025,
        'mocked_saving',
        _mocked_parameters_table(),
    )
    assert result[1] == 200
    assert result[2] == 500
