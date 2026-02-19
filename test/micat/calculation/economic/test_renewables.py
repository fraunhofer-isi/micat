# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import renewables
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch


def test_material_demand():
    final_energy_saving_or_capacities = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 1},
        ]
    )

    wuppertal_material_intensity = ValueTable(
        [
            {
                "id_parameter": 39,
                "id_action_type": 1,
                "id_subsector": 1,
                "id_crm": 1,
                "value": 3,
            },
            {
                "id_parameter": 39,
                "id_action_type": 1,
                "id_subsector": 1,
                "id_crm": 1,
                "value": 5,
            },
        ]
    )

    data_source = Mock()
    data_source.table = Mock(wuppertal_material_intensity)

    result = renewables.material_demand(
        final_energy_saving_or_capacities,
        data_source,
    )
    assert result._data_frame["2020"].loc[(1, 1)]


def test_supply_risk_factor():
    final_energy_saving_or_capacities = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 10},
        ]
    )

    wuppertal_supply_risk_factor = ValueTable(
        [
            {
                "id_parameter": 39,
                "id_action_type": 1,
                "id_subsector": 1,
                "value": 3,
            },
        ]
    )

    data_source = Mock()
    data_source.table = Mock(wuppertal_supply_risk_factor)

    result = renewables.supply_risk_factor(
        final_energy_saving_or_capacities,
        data_source,
    )
    assert result["2020"][1] == 30
