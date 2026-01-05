# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd

from micat.calculation import extrapolation
from micat.calculation.economic import energy_cost
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch, raises


def _mocked_energy_saving_by_final_energy_carrier():
    mocked_energy_saving_by_final_energy_carrier = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 1, "2020": 2},
        ]
    )
    return mocked_energy_saving_by_final_energy_carrier


def _mocked_data_source():
    mocked_data_source = Mock()
    mocked_data_source.table = Mock(
        return_value=Table(
            [{"id_sector": 1, "id_parameter": 1, "id_region": 1, "id_final_energy_carrier": 1, "2020": 2}]
        )
    )
    return mocked_data_source


def _mocked_table():
    mocked_table = Mock()
    mocked_table.reduce = Mock()
    mocked_table.unique_index_values = Mock()
    return mocked_table


@patch(energy_cost._e3m_energy_prices, _mocked_table())
@patch(energy_cost._past_reduction_of_energy_costs)
@patch(energy_cost._total_reduction_of_energy_costs_in_euro, "mocked_total_reduction_of_energy_costs_in_euro")
@patch(energy_cost._reduction_of_energy_costs_in_euro, "mocked_total_reduction_of_energy_costs_in_euro")
@patch(extrapolation.extrapolate)
def test_reduction_of_energy_cost():
    result = energy_cost.reduction_of_energy_cost(
        _mocked_energy_saving_by_final_energy_carrier(), _mocked_data_source(), 1
    )
    assert result == "mocked_total_reduction_of_energy_costs_in_euro"


def test_e3m_energy_prices():
    result = energy_cost._e3m_energy_prices(
        _mocked_table(),
        _mocked_data_source(),
    )
    assert result["2020"][1, 1, 1].iloc[0] == 2000000


class TestPastReductionOfEnergyCosts:
    mocked_table = Table(
        [
            {"id_subsector": 1, "id_final_energy_carrier": 1, "2020": 10},
            {"id_subsector": 2, "id_final_energy_carrier": 2, "2025": 20},
            {"id_subsector": 3, "id_final_energy_carrier": 3, "2030": 30},
        ]
    )

    def test_with_past_years(self):
        mocked_years = [2020, 2025, 2030]
        result = energy_cost._past_reduction_of_energy_costs(
            mocked_years,
            self.mocked_table,
            self.mocked_table,
        )
        assert result["2020"][1, 1] == 100
        with raises(KeyError):
            pd.isna(result["2025"][2, 2])

    def test_with_future_years(self):
        mocked_years = [2030, 2035, 2040]
        result = energy_cost._past_reduction_of_energy_costs(
            mocked_years,
            self.mocked_table,
            self.mocked_table,
        )
        assert result is None


def test_reduction_of_energy_costs():
    mocked_table = Table(
        [
            {"id_subsector": 1, "id_final_energy_carrier": 1, "2020": 10},
        ]
    )
    result = energy_cost._reduction_of_energy_costs_in_euro(mocked_table, mocked_table)
    assert result["2020"][1, 1] == 100


class TestTotalReductionOfEnergyCostsInEuro:
    mocked_reduction_of_energy_costs_in_euro = Table(
        [
            {"id_subsector": 1, "id_final_energy_carrier": 1, "2020": 10},
        ]
    )
    mocked_reduction_of_energy_costs_in_euro_outlook = Table(
        [
            {"id_subsector": 2, "id_final_energy_carrier": 2, "2025": 20},
            {"id_subsector": 3, "id_final_energy_carrier": 3, "2030": 30},
        ]
    )

    def test_with_future_and_past_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            self.mocked_reduction_of_energy_costs_in_euro, self.mocked_reduction_of_energy_costs_in_euro_outlook
        )
        assert result.columns == ["2020", "2025", "2030"]

    def test_with_past_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            self.mocked_reduction_of_energy_costs_in_euro, None
        )
        assert result.columns == ["2020"]

    def test_with_future_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            None, self.mocked_reduction_of_energy_costs_in_euro_outlook
        )
        assert result.columns == ["2025", "2030"]


def test_reduction_of_energy_cost_by_final_energy_carrier():
    reduction_of_energy_cost_by_action_type = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "id_final_energy_carrier": 1, "2020": 2},
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 2, "id_final_energy_carrier": 1, "2020": 2},
        ]
    )

    result = energy_cost.reduction_of_energy_cost_by_final_energy_carrier(
        reduction_of_energy_cost_by_action_type,
    )
    assert result["2020"][1, 1] == 4
