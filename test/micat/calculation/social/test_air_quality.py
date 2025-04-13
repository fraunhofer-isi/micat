# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.social import affected_dwellings, air_quality
from micat.series import annual_series
from micat.table import table
from micat.test_utils.isi_mock import Mock, patch

# pylint: disable=protected-access


def _mocked_years():
    return [2020, 2025, 2030]


def _mocked_final_energy_savings_by_action_type():
    mocked_final_energy_savings_by_action_type = table.Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 10, "2025": 20, "2030": 30},
            {"id_measure": 2, "id_subsector": 2, "id_action_type": 2, "2020": 100, "2025": 200, "2030": 300},
        ]
    )
    return mocked_final_energy_savings_by_action_type


def _mocked_annual_series(value):
    mocked_annual_series = annual_series.AnnualSeries({"2020": value, "2025": value, "2030": value})
    return mocked_annual_series


def _mocked_data_source():
    mocked_data_source = Mock()
    mocked_data_source.annual_series_from_value = Mock(
        return_value=annual_series.AnnualSeries({"2020": 1, "2025": 1, "2030": 1})
    )
    return mocked_data_source


@patch(air_quality._daly_per_damp_and_mouldy_building_ratio, Mock(return_value=_mocked_annual_series(1)))
@patch(air_quality._medium_and_deep_renovations_share, Mock(return_value=_mocked_annual_series(2)))
@patch(air_quality._damp_and_mouldy_buildings_targetedness_factor, Mock(return_value=_mocked_annual_series(3)))
@patch(
    affected_dwellings.determine_number_of_affected_dwellings,
    Mock(return_value=_mocked_final_energy_savings_by_action_type()),
)
def test_reduction_in_disability_adjusted_life_years():
    result = air_quality.reduction_in_disability_adjusted_life_years(
        _mocked_final_energy_savings_by_action_type(),
        "mocked_data_source",
        1,
    )
    assert result["2020"][1, 1, 1] == 60


def test_daly_per_damp_and_mouldy_building_ratio():
    result = air_quality._daly_per_damp_and_mouldy_building_ratio(_mocked_data_source(), 1, _mocked_years())
    assert result.columns == ["2020", "2025", "2030"]


def test_medium_and_deep_renovations_share():
    result = air_quality._medium_and_deep_renovations_share(_mocked_data_source(), 1, _mocked_years())
    assert result.columns == ["2020", "2025", "2030"]


def test_damp_and_mouldy_buildings_targetedness_factor():
    result = air_quality._damp_and_mouldy_buildings_targetedness_factor(_mocked_data_source(), 1, _mocked_years())
    assert result.columns == ["2020", "2025", "2030"]
