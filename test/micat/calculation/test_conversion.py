# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
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


def _carriers():
    return [1, 2, 3, 4, 5, 6, 7]


def _eurostat_primary_parameters():
    rows = []
    for param in [20, 21]:
        for carrier in _carriers():
            rows.append({"id_parameter": param, "id_primary_energy_carrier": carrier, "2020": 0.5, "2030": 0.7})
    return Table(rows)


def _h2_coefficient():
    return Table(
        [{"id_parameter": 22, "id_primary_energy_carrier": c, "2020": 5, "2030": 10} for c in _carriers()]
    )


def _conversion_efficiency():
    rows = []
    for carrier in _carriers():
        for final_carrier in [1, 6, 7]:
            rows.append(
                {
                    "id_primary_energy_carrier": carrier,
                    "id_final_energy_carrier": final_carrier,
                    "2020": 5,
                    "2030": 10,
                }
            )
    return Table(rows)


def test_primary_energy_saving_with_two_renewable_measures():
    final_energy_savings = Table(
        [
            {"id_measure": 1, "id_subsector": 30, "id_action_type": 30, "id_final_energy_carrier": fc, "2020": 6, "2030": 60}
            for fc in [1, 6, 7]
        ]
        + [
            {"id_measure": 2, "id_subsector": 30, "id_action_type": 31, "id_final_energy_carrier": fc, "2020": 8, "2030": 80}
            for fc in [1, 6, 7]
        ]
    )

    substitution_factors = Table(
        [
            {
                "id_measure": m,
                "id_parameter": 67,
                "id_subsector": 30,
                "id_action_type": at,
                "id_primary_energy_carrier": c,
                "2020": 0.2,
                "2030": 0.3,
            }
            for m, at in [(1, 30), (2, 31)]
            for c in _carriers()
        ]
    )

    mock_data_source = Mock()
    mock_data_source.table = Mock(return_value=None)

    heat_saving_final, electricity_saving_final, h2_saving_final = primary_energy_saving(
        final_energy_savings,
        _eurostat_primary_parameters(),
        _h2_coefficient(),
        _conversion_efficiency(),
        substitution_factors,
        mock_data_source,
        30,
    )
    result = heat_saving_final + electricity_saving_final + h2_saving_final
    assert result.columns == ["2020", "2030"]
    assert not result._data_frame.isnull().any().any()


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
    substitution_factors = None

    heat_saving_final, electricity_saving_final, h2_saving_final = primary_energy_saving(
        final_energy_savings_by_action_type,
        eurostat_primary_parameters,
        h2_coefficient,
        conversion_efficiency,
        substitution_factors,
        Mock(),
        1,
    )
    result = heat_saving_final + electricity_saving_final + h2_saving_final
    assert result.columns == ["2020", "2030"]
