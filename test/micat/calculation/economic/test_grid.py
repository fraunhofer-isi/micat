# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from micat.calculation.economic import eurostat, grid, primes
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.template import mocks

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch


@patch(grid._capacity_reduction_factor, 2)
def test_reduction_of_additional_capacities_in_grid():
    final_energy_saving_electricity = Table(
        [
            {
                "id_subsector": 1,
                "id_action_type": 1,
                "id_measure": 1,
                "id_technology": 1,
                "2000": 10,
            }
        ]
    )

    result = grid.reduction_of_additional_capacities_in_grid(
        final_energy_saving_electricity, "mocked_data_source", "mocked_id_region"
    )

    assert result["2000"][1].iloc[0] == 20


def test_monetization_of_reduction_of_additional_capacities_in_grid():
    reduction_of_additional_capacities = Table(
        [
            {
                "id_measure": 11,
                "id_technology": 1,
                "2000": 10,
            }
        ]
    )

    mocked_investment_costs = ValueTable([{"id_technology": 1, "value": 2}])
    data_source = Mock()
    data_source.parameter = Mock(mocked_investment_costs)

    result = grid.monetization_of_reduction_of_additional_capacities_in_grid(
        reduction_of_additional_capacities,
        data_source,
    )

    assert result["2000"][11] == 20


class TestCapacityReductionFactor:
    mocked_parameters = Mock()
    mocked_parameters.reduce = Mock("mocked_result")

    @patch(eurostat.technology_parameters, Mock(mocked_parameters))
    def test_capacity_reduction_factor(self):
        result = grid._capacity_reduction_factor(mocks.mocked_database(), "mocked_id_region", [2015, 2020])
        assert result == "mocked_result"
