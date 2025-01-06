# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.ecologic import targets
from micat.table.table import Table


def test_renewable_energy_directive_targets():
    gross_available_energy = Table(
        [
            {'id_primary_energy_carrier': 1, '2020': 100, '2030': 1000},
            {'id_primary_energy_carrier': 2, '2020': 200, '2030': 2000},
            {'id_primary_energy_carrier': 3, '2020': 300, '2030': 3000},
            {'id_primary_energy_carrier': 4, '2020': 400, '2030': 4000},
            {'id_primary_energy_carrier': 5, '2020': 500, '2030': 5000},
            {'id_primary_energy_carrier': 6, '2020': 600, '2030': 6000},
        ]
    )

    total_primary_energy_saving = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 1,
                'id_action_type': 1,
                'id_primary_energy_carrier': 1,
                '2020': 100,
                '2030': 1000,
            },
        ]
    )

    result = targets.impact_on_res_targets(
        gross_available_energy,
        total_primary_energy_saving,
    )

    # renewable_gae_sum =  900,  9000
    #     total_gae_sum = 2100, 21000
    #     total_pes_sum =  100,  1000

    assert result['2020'][1] == 900 / 2000 - 900 / 2100
    assert result['2030'][1] == 9000 / 20000 - 9000 / 21000


def test_renewable_energy_directive_targets_monetization():
    change_of_share = Table(
        [
            {'id_measure': 1, '2020': 0.01, '2030': 0.02},
        ]
    )

    gross_available_energy = Table(
        [
            {'id_primary_energy_carrier': 1, '2020': 100, '2030': 1000},
            {'id_primary_energy_carrier': 2, '2020': 200, '2030': 2000},
            {'id_primary_energy_carrier': 3, '2020': 300, '2030': 3000},
            {'id_primary_energy_carrier': 4, '2020': 400, '2030': 4000},
            {'id_primary_energy_carrier': 5, '2020': 500, '2030': 5000},
            {'id_primary_energy_carrier': 6, '2020': 600, '2030': 6000},
        ]
    )

    total_primary_energy_saving = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 1,
                'id_action_type': 1,
                'id_primary_energy_carrier': 1,
                '2020': 100,
                '2030': 1000,
            },
        ]
    )

    cost_of_res_statistical_transfer = 2

    result = targets.impact_on_res_targets_monetization(
        change_of_share, gross_available_energy, total_primary_energy_saving, cost_of_res_statistical_transfer
    )

    assert result['2020'][1] == 40
    assert result['2030'][1] == 800
