# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import mode
from micat.calculation.economic import eurostat, grid, primes
from micat.table.table import Table
from micat.table.value_table import ValueTable

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch


@patch(grid._capacity_reduction_factor, 2)
def test_reduction_of_additional_capacities_in_grid():
    final_energy_saving_electricity = Table(
        [
            {
                'id_mode': 11,
                'id_subsector': 1,
                'id_action_type': 1,
                '2000': 10,
            }
        ]
    )

    result = grid.reduction_of_additional_capacities_in_grid(
        final_energy_saving_electricity, 'mocked_data_source', 'mocked_id_mode', 'mocked_id_region'
    )

    assert result['2000'][11] == 20


def test_monetization_of_reduction_of_additional_capacities_in_grid():
    reduction_of_additional_capacities = Table(
        [
            {
                'id_measure': 11,
                'id_technology': 1,
                '2000': 10,
            }
        ]
    )

    mocked_investment_costs = ValueTable([{'id_technology': 1, 'value': 2}])
    data_source = Mock()
    data_source.parameter = Mock(mocked_investment_costs)

    result = grid.monetization_of_reduction_of_additional_capacities_in_grid(
        reduction_of_additional_capacities,
        data_source,
    )

    assert result['2000'][11] == 20


class TestCapacityReductionFactor:
    mocked_parameters = Mock()
    mocked_parameters.reduce = Mock('mocked_result')

    @patch(eurostat.technology_parameters, Mock(mocked_parameters))
    @patch(mode.is_eurostat_mode, True)
    def test_for_eurostat_mode(self):
        result = grid._capacity_reduction_factor(
            'mocked_data_source', 'mocked_id_mode', 'mocked_id_region', 'mocked_years'
        )
        assert result == 'mocked_result'

    @patch(primes.technology_parameters, Mock(mocked_parameters))
    @patch(mode.is_eurostat_mode, False)
    def test_for_primes_mode(self):
        result = grid._capacity_reduction_factor(
            'mocked_data_source', 'mocked_id_mode', 'mocked_id_region', 'mocked_years'
        )
        assert result == 'mocked_result'
