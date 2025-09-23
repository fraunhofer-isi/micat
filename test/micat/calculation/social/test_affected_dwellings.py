# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np

import micat.input.data_source  # pylint: disable=redefined-builtin
from micat.calculation import extrapolation
from micat.calculation.social import affected_dwellings
from micat.table import table
from micat.test_utils.isi_mock import Mock, patch

# pylint: disable=protected-access


def _mocked_data_source():
    mocked_datasource = Mock()
    mocked_datasource.measure_specific_parameter = Mock(return_value="mocked_measure_specific_parameter")
    mocked_datasource.table = Mock(return_value="mocked_table")
    mocked_datasource.annual_series = Mock(return_value="mocked_annual_series")
    mocked_datasource.annual_parameters_per_measure = Mock()
    return mocked_datasource


mocked_years = ["2020", "2025", "2030"]


def _mocked_final_energy_saving_or_capacities():
    mocked_final_energy_saving_or_capacities = Mock()
    mocked_final_energy_saving_or_capacities.years = mocked_years
    return mocked_final_energy_saving_or_capacities


# pylint: disable=duplicate-code
def _mocked_table():
    mocked_table = Mock()
    mocked_table.to_data_frame = Mock()
    mocked_table.copy = Mock(return_value="mocked_table")
    mocked_table.isna = Mock(return_value="mocked_boolean_index")
    mocked_table.index = Mock()
    mocked_table.index.get_level_values = Mock(return_value=5)
    mocked_table.loc = Mock()
    mocked_table.reduce = Mock(return_value="mocked_reduce")
    return mocked_table


@patch(affected_dwellings._user_input_parameter)
@patch(affected_dwellings._number_of_affected_dwellings, Mock(return_value="mocked_number_of_affected_dwellings"))
def test_determine_number_of_affected_dwellings():
    result = affected_dwellings.determine_number_of_affected_dwellings(
        _mocked_final_energy_saving_or_capacities(), _mocked_data_source(), 1
    )
    assert result == "mocked_number_of_affected_dwellings"


class TestProvideDefaultNumberOfAffectedDwellingsPerKtoe:
    mocked_default_parameters_table = table.Table(
        [
            {"id_parameter": 1, "id_action_type": 1, "2020": 10, "2025": 20},
            {"id_parameter": 1, "id_action_type": 2, "2020": 20, "2025": 20},
        ]
    )

    def test_get_value(self):
        result = affected_dwellings._provide_default_number_of_affected_dwellings_per_ktoe(
            "mocked_id_region",
            1,
            "mocked_id_measure",
            "mocked_id_subsector",
            2,
            2020,
            "mocked_saving",
            self.mocked_default_parameters_table,
        )
        assert result == 20

    def test_get_nan_value(self):
        result = affected_dwellings._provide_default_number_of_affected_dwellings_per_ktoe(
            "mocked_id_region",
            1,
            "mocked_id_measure",
            "mocked_id_subsector",
            3,
            2020,
            "mocked_saving",
            self.mocked_default_parameters_table,
        )
        assert np.isnan(result)


class TestProvideDefaultNationalDwellingStock:
    mocked_default_parameters_table = table.Table(
        [
            {"id_region": 1, "id_parameter": 1, "2020": 10, "2025": 20},
            {"id_region": 2, "id_parameter": 1, "2020": 20, "2025": 20},
        ]
    )

    def test_get_value(self):
        result = affected_dwellings._provide_default_national_dwelling_stock(
            2,
            1,
            "mocked_id_measure",
            "mocked_id_subsector",
            "mocked_id_action_type",
            2020,
            "mocked_saving",
            self.mocked_default_parameters_table,
        )
        assert result == 20

    def test_get_nan_value(self):
        result = affected_dwellings._provide_default_national_dwelling_stock(
            3,
            1,
            "mocked_id_measure",
            "mocked_id_subsector",
            "mocked_id_action_type",
            2020,
            "mocked_saving",
            self.mocked_default_parameters_table,
        )
        assert np.isnan(result)


@patch(micat.input.data_source.DataSource.measure_specific_parameter, Mock(return_value="mocked_result"))
def test_user_input_parameter():
    result = affected_dwellings._user_input_parameter(
        "mocked_final_energy_saving_or_capacities", _mocked_data_source(), "mocked_id_parameter"
    )
    assert result == "mocked_measure_specific_parameter"


@patch(extrapolation.extrapolate, Mock(return_value=_mocked_table()))
def test_number_of_affected_dwellings_per_ktoe():
    result = affected_dwellings._number_of_affected_dwellings_per_ktoe(
        _mocked_final_energy_saving_or_capacities(), _mocked_data_source()
    )
    assert result == "mocked_reduce"


mocked_table_dict = {"id_subsector": "mocked_subsectors", "id_action_type": "mocked_id_action_type"}


@patch(affected_dwellings._calculate_annual_renovation_rate)
@patch(affected_dwellings._calculate_number_of_affected_dwellings)
@patch(
    table.Table,
    Mock(return_value=mocked_table_dict),
)
def test_number_of_affected_dwellings():
    mocked_table = _mocked_table()
    result = affected_dwellings._number_of_affected_dwellings(
        mocked_table,
        mocked_table,
        mocked_table,
        mocked_table,
        mocked_table,
    )
    assert len(result) == 0
    assert mocked_table.to_data_frame.call_count == 5


@patch(affected_dwellings._fill_number_of_affected_dwellings_calculated_nan_values)
@patch(affected_dwellings._fill_table_values_for_id_action_type_greater_than_four)
def test_calculate_number_of_affected_dwellings():
    result = affected_dwellings._calculate_number_of_affected_dwellings(_mocked_table(), _mocked_table())
    assert result == "mocked_table"


def test_fill_number_of_affected_dwellings_calculated_nan_values():
    mocked_number_of_affected_dwellings = _mocked_table()
    affected_dwellings._fill_number_of_affected_dwellings_calculated_nan_values(
        mocked_number_of_affected_dwellings, _mocked_table()
    )
    assert mocked_number_of_affected_dwellings.isna.called is True


def test_fill_table_values_for_id_action_type_greater_than_four():
    mocked_table_values = _mocked_table()
    affected_dwellings._fill_table_values_for_id_action_type_greater_than_four(mocked_table_values)
    assert mocked_table_values.index.get_level_values.called is True


@patch(affected_dwellings._fill_annual_renovation_rate_nan_values_for_id_action_type_less_than_four)
@patch(affected_dwellings._fill_annual_renovation_rate_nan_values_for_id_action_type_four)
@patch(affected_dwellings._fill_table_values_for_id_action_type_greater_than_four)
def test_calculate_annual_renovation_rate():
    mocked_annual_renovation_rate = _mocked_table()
    mocked_annual_renovation_rate.copy = Mock(return_value=1)
    result = affected_dwellings._calculate_annual_renovation_rate(
        _mocked_table(), mocked_annual_renovation_rate, _mocked_table(), 1
    )
    assert result == 0.01


def test_fill_annual_renovation_rate_nan_values_for_id_action_type_four():
    mocked_annual_renovation_rate = _mocked_table()
    affected_dwellings._fill_annual_renovation_rate_nan_values_for_id_action_type_four(mocked_annual_renovation_rate)
    assert mocked_annual_renovation_rate.index.get_level_values.called is True


def test_fill_annual_renovation_rate_nan_values_for_id_action_type_less_than_four():
    mocked_annual_renovation_rate = _mocked_table()
    affected_dwellings._fill_annual_renovation_rate_nan_values_for_id_action_type_less_than_four(
        _mocked_table(), mocked_annual_renovation_rate, _mocked_table()
    )
    assert mocked_annual_renovation_rate.index.get_level_values.called is True


def test_provide_default_parameter():
    result = affected_dwellings._provide_default_parameter(
        "mocked_id_measure", "mocked_id_subsector", "mocked_id_action_type", "mocked_year", "mocked_saving"
    )
    assert np.isnan(result)


mocked_national_dwelling_stock = _mocked_table()


@patch(extrapolation.extrapolate, Mock(return_value=mocked_national_dwelling_stock))
def test_national_dwelling_stock():
    result = affected_dwellings._national_dwelling_stock(_mocked_data_source(), 0, mocked_years)
    assert result == "mocked_reduce"
