# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import renewables
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock


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


def _voe_data_source():
    wuppertal_value_of_energy = Table(
        [
            {"id_parameter": 77, "id_primary_energy_carrier": 1, "2020": 10, "2030": 10},
            {"id_parameter": 78, "id_primary_energy_carrier": 1, "2020": 5, "2030": 5},
            {"id_parameter": 79, "id_primary_energy_carrier": 1, "2020": 2, "2030": 2},
            {"id_parameter": 80, "id_primary_energy_carrier": 1, "2020": 3, "2030": 3},
        ]
    )

    conversion_efficiency = Table(
        [
            {"id_final_energy_carrier": 1, "id_parameter": 65, "id_primary_energy_carrier": 1, "2020": 0.4, "2030": 0.4},
            {"id_final_energy_carrier": 6, "id_parameter": 65, "id_primary_energy_carrier": 1, "2020": 0.9, "2030": 0.9},
        ]
    )

    def table_side_effect(name, where):
        if name == "wuppertal_value_of_energy":
            return wuppertal_value_of_energy
        if name == "fraunhofer_conversion_efficiency":
            return conversion_efficiency
        return None

    data_source = Mock()
    data_source.table = table_side_effect
    return data_source


def test_value_of_energy():
    total_primary_energy_saving = Table(
        [
            {
                "id_measure": 1,
                "id_subsector": 30,
                "id_action_type": 30,
                "id_primary_energy_carrier": 1,
                "2020": 100,
                "2030": 200,
            },
        ]
    )

    data_source = _voe_data_source()

    result = renewables.value_of_energy(
        total_primary_energy_saving,
        data_source,
        id_action_type=30,
    )
    # VOE = 100 * (10 + 5 + 2 * 0.4) = 100 * 15.8 = 1580
    assert result["2020"][1] == 1580.0
    # VOE = 200 * (10 + 5 + 2 * 0.4) = 200 * 15.8 = 3160
    assert result["2030"][1] == 3160.0


def test_value_of_energy_district_heat():
    total_primary_energy_saving = Table(
        [
            {
                "id_measure": 1,
                "id_subsector": 30,
                "id_action_type": 37,
                "id_primary_energy_carrier": 1,
                "2020": 100,
                "2030": 200,
            },
        ]
    )

    data_source = _voe_data_source()

    result = renewables.value_of_energy(
        total_primary_energy_saving,
        data_source,
        id_action_type=37,
    )
    # VOE = 100 * (10 + 5 + 3 * 0.9) = 100 * 17.7 = 1770
    assert result["2020"][1] == 1770.0
    # VOE = 200 * (10 + 5 + 3 * 0.9) = 200 * 17.7 = 3540
    assert result["2030"][1] == 3540.0
