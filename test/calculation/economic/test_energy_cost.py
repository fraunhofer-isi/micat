# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd
from test_utils.mock import Mock, patch, raises

from calculation import extrapolation
from calculation.economic import energy_cost
from table.table import Table


def _mocked_energy_saving_by_final_energy_carrier():
    mocked_energy_saving_by_final_energy_carrier = Table(
        [
            {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 1, 'id_final_energy_carrier': 1, '2020': 2},
        ]
    )
    return mocked_energy_saving_by_final_energy_carrier


def _mocked_data_source():
    mocked_data_source = Mock()
    mocked_data_source.table = Mock(return_value='mocked_table')
    return mocked_data_source


def _mocked_table():
    mocked_table = Mock()
    mocked_table.reduce = Mock()
    mocked_table.unique_index_values = Mock()
    return mocked_table


@patch(energy_cost._enerdata_final_sector_parameters, _mocked_table())
@patch(energy_cost._past_reduction_of_energy_costs)
@patch(energy_cost._reduction_of_energy_costs_outlook)
@patch(energy_cost._total_reduction_of_energy_costs_in_euro, 'mocked_total_reduction_of_energy_costs_in_euro')
@patch(energy_cost._reduction_of_energy_costs_in_euro, 'mocked_total_reduction_of_energy_costs_in_euro')
@patch(extrapolation.extrapolate)
def test_reduction_of_energy_cost():
    result = energy_cost.reduction_of_energy_cost(
        _mocked_energy_saving_by_final_energy_carrier(), _mocked_data_source(), 1
    )
    assert result == 'mocked_total_reduction_of_energy_costs_in_euro'


def test_enerdata_final_sector_parameters():
    result = energy_cost._enerdata_final_sector_parameters(
        _mocked_table(),
        _mocked_data_source(),
    )
    assert result == 'mocked_table'


class TestPastReductionOfEnergyCosts:
    mocked_table = Table(
        [
            {'id_subsector': 1, 'id_final_energy_carrier': 1, '2020': 10},
            {'id_subsector': 2, 'id_final_energy_carrier': 2, '2025': 20},
            {'id_subsector': 3, 'id_final_energy_carrier': 3, '2030': 30},
        ]
    )

    def test_with_past_years(self):
        mocked_years = [2020, 2025, 2030]
        result = energy_cost._past_reduction_of_energy_costs(
            mocked_years,
            self.mocked_table,
            self.mocked_table,
        )
        assert result['2020'][1, 1] == 100
        with raises(KeyError):
            pd.isna(result['2025'][2, 2])

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
            {'id_subsector': 1, 'id_final_energy_carrier': 1, '2020': 10},
        ]
    )
    result = energy_cost._reduction_of_energy_costs_in_euro(mocked_table, mocked_table)
    assert result['2020'][1, 1] == 100


class TestReductionOfEnergyCostOutlook:
    mocked_table = Table(
        [
            {'id_subsector': 1, 'id_final_energy_carrier': 1, '2020': 10},
            {'id_subsector': 2, 'id_final_energy_carrier': 2, '2025': 20},
            {'id_subsector': 3, 'id_final_energy_carrier': 3, '2030': 30},
        ]
    )

    def test_with_past_years(self):
        mocked_years = [2010, 2015, 2020]
        result = energy_cost._reduction_of_energy_costs_outlook(
            mocked_years,
            self.mocked_table,
            self.mocked_table,
        )
        assert result is None

    def test_with_future_years(self):
        mocked_years = [2020, 2025, 2030]
        result = energy_cost._reduction_of_energy_costs_outlook(
            mocked_years,
            self.mocked_table,
            self.mocked_table,
        )
        assert result['2030'][3, 3] == 900
        with raises(KeyError):
            pd.isna(result['2020'][1, 1])


class TestTotalReductionOfEnergyCostsInEuro:
    mocked_reduction_of_energy_costs_in_euro = Table(
        [
            {'id_subsector': 1, 'id_final_energy_carrier': 1, '2020': 10},
        ]
    )
    mocked_reduction_of_energy_costs_in_euro_outlook = Table(
        [
            {'id_subsector': 2, 'id_final_energy_carrier': 2, '2025': 20},
            {'id_subsector': 3, 'id_final_energy_carrier': 3, '2030': 30},
        ]
    )

    def test_with_future_and_past_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            self.mocked_reduction_of_energy_costs_in_euro, self.mocked_reduction_of_energy_costs_in_euro_outlook
        )
        assert result.columns == ['2020', '2025', '2030']

    def test_with_past_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            self.mocked_reduction_of_energy_costs_in_euro, None
        )
        assert result.columns == ['2020']

    def test_with_future_results(self):
        result = energy_cost._total_reduction_of_energy_costs_in_euro(
            None, self.mocked_reduction_of_energy_costs_in_euro_outlook
        )
        assert result.columns == ['2025', '2030']


def test_reduction_of_energy_cost_by_final_energy_carrier():
    reduction_of_energy_cost_by_action_type = Table(
        [
            {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 1, 'id_final_energy_carrier': 1, '2020': 2},
            {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 2, 'id_final_energy_carrier': 1, '2020': 2},
        ]
    )

    result = energy_cost.reduction_of_energy_cost_by_final_energy_carrier(
        reduction_of_energy_cost_by_action_type,
    )
    assert result['2020'][1, 1] == 4
