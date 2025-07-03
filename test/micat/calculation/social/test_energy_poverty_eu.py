# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from micat.calculation.economic import energy_cost
from micat.calculation.social import (
    affected_dwellings,
    energy_poverty_eu,
    energy_poverty_national,
)
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch

# pylint: disable=protected-access


def _mocked_alleviation_of_energy_poverty():
    mocked_alleviation_of_energy_poverty = Table(
        [
            {"id_measure": 0, "2000": 0, "2001": 0},
            {"id_measure": 1, "2000": 1, "2001": 1},
            {"id_measure": 1, "2000": 2, "2001": 2},
        ]
    )
    return mocked_alleviation_of_energy_poverty


def _mocked_population_table(id_parameter=True):
    mocked_population_table = Table(
        [
            {"id_region": 0, "id_parameter": 24, "2000": 0, "2001": 0},
            {"id_region": 1, "id_parameter": 24, "2000": 1, "2001": 1},
            {"id_region": 2, "id_parameter": 24, "2000": 2, "2001": 2},
        ]
    )
    if not id_parameter:
        mocked_population_table = mocked_population_table.droplevel(1)
    return mocked_population_table


def _mocked_final_energy_savings_by_action_type():
    mocked_final_energy_savings_by_action_type = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 10, "2025": 20, "2030": 30},
            {"id_measure": 2, "id_subsector": 2, "id_action_type": 2, "2020": 100, "2025": 200, "2030": 300},
        ]
    )
    return mocked_final_energy_savings_by_action_type


def _mocked_number_of_affected_dwellings():
    mocked_final_energy_savings_by_action_type = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 100, "2025": 100, "2030": 100},
            {"id_measure": 2, "id_subsector": 2, "id_action_type": 2, "2020": 200, "2025": 200, "2030": 200},
        ]
    )
    return mocked_final_energy_savings_by_action_type


class TestAlleviationOfEnergyPovertyOnEuLevel:
    def test_national_id_region(self):
        with pytest.raises(ValueError) as error:
            energy_poverty_eu.alleviation_of_energy_poverty_on_eu_level(
                "mocked_final_energy_saving_by_action_type",
                "mocked_data_source",
                1,
            )
            assert error

    @patch(energy_poverty_eu._population_table, _mocked_population_table(False))
    @patch(energy_poverty_eu._energy_savings_allocated_to_country)
    @patch(energy_poverty_eu._number_of_affected_dwellings_allocated_to_country)
    @patch(energy_cost.reduction_of_energy_cost)
    @patch(energy_poverty_national.alleviation_of_energy_poverty_on_national_level)
    @patch(Table.concat, _mocked_alleviation_of_energy_poverty())
    def test_eu(self):
        result = energy_poverty_eu.alleviation_of_energy_poverty_on_eu_level(
            "mocked_final_energy_saving_by_action_type",
            "mocked_data_source",
            0,
        )
        assert result[0]["2000"][1] == 3
        assert result[1]["2000"][1] == 3


class TestPopulationTable:
    mocked_data_source = Mock()
    mocked_data_source.table = Mock(_mocked_population_table())

    def test_table(self):
        result = energy_poverty_eu._population_table(
            _mocked_final_energy_savings_by_action_type(), self.mocked_data_source
        )
        assert result["2030"][2] == 2.0


def test_energy_savings_allocated_to_country():
    result = energy_poverty_eu._energy_savings_allocated_to_country(
        _mocked_final_energy_savings_by_action_type(), 100, 1000
    )
    assert result["2020"][2, 2, 2] == 10


@patch(affected_dwellings.determine_number_of_affected_dwellings, _mocked_number_of_affected_dwellings())
def test_number_of_affected_dwellings_allocated_to_country():
    result = energy_poverty_eu._number_of_affected_dwellings_allocated_to_country(
        _mocked_final_energy_savings_by_action_type(),
        "mocked_data_source",
        100,
        1000,
    )
    assert result["2020"][2, 2, 2] == 20
