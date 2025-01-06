# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.economic import energy_efficiency
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


@patch(energy_efficiency._specific_turnover, 2)
def test_turnover_of_energy_efficiency_goods():
    final_energy_savings = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 1,
                'id_action_type': 1,
                '2000': 1,
            }
        ]
    )

    result = energy_efficiency.turnover_of_energy_efficiency_goods(
        final_energy_savings,
        'mocked_data_source',
    )
    assert result['2000'][1] == 2


@patch(extrapolation.extrapolate, 'mocked_result')
def test_specific_turnover():
    data_source = Mock()

    result = energy_efficiency._specific_turnover(
        data_source,
        'mocked_action_type_ids',
        'mocked_years',
    )
    assert result == 'mocked_result'
