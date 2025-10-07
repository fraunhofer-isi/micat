# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

from micat.calculation.conversion import (
    primary_energy_saving,
    total_primary_energy_saving,
)
from micat.table.mapping_table import MappingTable
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock


def mocked_final_energy():
    return Table(
        [
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 2, "2020": 5},
            {"id_subsector": 1, "id_action_type": 2, "id_final_energy_carrier": 3, "2020": 6},
        ]
    )


def mocked_mapping():
    return MappingTable(
        pd.DataFrame(
            [
                {"id": 1, "id_final_energy_carrier": 2, "id_primary_energy_carrier": 1},
                {"id": 2, "id_final_energy_carrier": 3, "id_primary_energy_carrier": 2},
            ]
        ),
    )


def test_total_primary_energy_saving():
    primary_energy_saving_ = Table([{"id_primary_energy_carrier": 1, "2020": 10, "2030": 20}])

    additional_primary_energy_saving = Table([{"id_primary_energy_carrier": 1, "2020": 20, "2030": 40}])

    result = total_primary_energy_saving(
        primary_energy_saving_,
        additional_primary_energy_saving,
    )

    assert result["2020"][1] == 10 + 20
    assert result["2030"][1] == 20 + 40


def test_primary_energy_saving():
    eurostat_primary_parameters = Table(
        [
            {"id_parameter": 20, "id_primary_energy_carrier": 1, "2020": 0.5, "2030": 0.7},
            {"id_parameter": 20, "id_primary_energy_carrier": 2, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 20, "id_primary_energy_carrier": 3, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 20, "id_primary_energy_carrier": 4, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 20, "id_primary_energy_carrier": 5, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 20, "id_primary_energy_carrier": 6, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 20, "id_primary_energy_carrier": 7, "2020": 0.6, "2030": 0.8},
            {"id_parameter": 21, "id_primary_energy_carrier": 1, "2020": 0.1, "2030": 0.3},
            {"id_parameter": 21, "id_primary_energy_carrier": 2, "2020": 0.2, "2030": 0.4},
            {"id_parameter": 21, "id_primary_energy_carrier": 3, "2020": 0.2, "2030": 0.4},
            {"id_parameter": 21, "id_primary_energy_carrier": 4, "2020": 0.2, "2030": 0.4},
            {"id_parameter": 21, "id_primary_energy_carrier": 5, "2020": 0.2, "2030": 0.4},
            {"id_parameter": 21, "id_primary_energy_carrier": 6, "2020": 0.2, "2030": 0.4},
            {"id_parameter": 21, "id_primary_energy_carrier": 7, "2020": 0.2, "2030": 0.4},
        ]
    )

    h2_coefficient = Table(
        [
            {"id_parameter": 22, "id_primary_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 2, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 3, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 4, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 5, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_parameter": 22, "id_primary_energy_carrier": 7, "2020": 5, "2030": 10},
        ]
    )

    final_energy_savings_by_action_type = Table(
        [
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 1, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 2, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 3, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 4, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 5, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 6, "2020": 6, "2030": 60},
            {"id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 7, "2020": 6, "2030": 60},
        ]
    )

    conversion_efficiency = Table(
        [
            {"id_primary_energy_carrier": 1, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 2, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 3, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 4, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 5, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 6, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 7, "id_final_energy_carrier": 1, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 1, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 2, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 3, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 4, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 5, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 6, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 7, "id_final_energy_carrier": 6, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 1, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 2, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 3, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 4, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 5, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 6, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
            {"id_primary_energy_carrier": 7, "id_final_energy_carrier": 7, "2020": 5, "2030": 10},
        ]
    )

    result = primary_energy_saving(
        final_energy_savings_by_action_type,
        eurostat_primary_parameters,
        h2_coefficient,
        conversion_efficiency,
    )

    assert result.columns == ["2020", "2030"]
