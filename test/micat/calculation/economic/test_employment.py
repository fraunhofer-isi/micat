# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import employment, investment
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch

annual_investment_in_euro = Table(
    [
        {
            "id_measure": 1,
            "id_action_type": 1,
            "2020": 10,
        }
    ]
)


@patch(
    investment.annual_investment_cost_in_euro,
    annual_investment_in_euro,
)
def test_reduction_of_energy_cost():
    final_energy_saving_or_capacities = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 0},
        ]
    )

    e3m_parameters = ValueTable(
        [
            {"id_parameter": 39, "id_action_type": 1, "value": 3},
        ]
    )

    data_source = Mock()
    data_source.table = Mock(e3m_parameters)

    result = employment.additional_employment(
        final_energy_saving_or_capacities,
        data_source,
        "mocked_id_region",
    )
    assert result["2020"][1] == 30
