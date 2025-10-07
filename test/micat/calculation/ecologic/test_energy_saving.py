# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.ecologic import energy_saving, fuel_split
from micat.table.table import Table

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/42
# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch

mocked_primary_energy = Table(
    [
        {"id_primary_energy_carrier": 1, "id_subsector": 1, "id_action_type": 1, "2020": 5},
        {"id_primary_energy_carrier": 1, "id_subsector": 1, "id_action_type": 2, "2020": 6},
        {"id_primary_energy_carrier": 8, "id_subsector": 1, "id_action_type": 2, "2020": 7},
        {"id_primary_energy_carrier": 8, "id_subsector": 2, "id_action_type": 2, "2020": 8},
    ]
)


def mocked_table_init(self, _data_frame):
    self._data_frame = "mocked_frame"


@patch(
    energy_saving._aggregate_primary_energy_saving,
    "mocked_result",
)
def test_energy_savings():
    result = energy_saving.energy_saving(mocked_primary_energy)
    assert result == "mocked_result"


@patch(fuel_split.fuel_split_by_action_type)
@patch(
    energy_saving._final_energy_saving_or_capacities_and_energy_carrier,
    "mocked_result",
)
def test_energy_saving_by_final_energy_carrier():
    mocked_final_energy_saving_or_capacities = Mock()

    result = energy_saving.energy_saving_by_final_energy_carrier(
        mocked_final_energy_saving_or_capacities,
        "mocked_data_source",
        "mocked_id_region",
        "mocked_subsector_ids",
    )
    assert result == "mocked_result"


def test_final_energy_saving_or_capacities_and_energy_carrier():
    fuel_split_by_action_type = 2
    final_energy_savings_by_action_type = 3

    result = energy_saving._final_energy_saving_or_capacities_and_energy_carrier(
        fuel_split_by_action_type,
        final_energy_savings_by_action_type,
    )
    assert result == 2 * 3


@patch(Table.aggregate_to, "mocked_result")
def test_aggregate_primary_energy_savings():
    result = energy_saving._aggregate_primary_energy_saving(mocked_primary_energy)
    assert result == "mocked_result"
