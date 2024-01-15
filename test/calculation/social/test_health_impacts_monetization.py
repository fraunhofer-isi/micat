# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
from test_utils.mock import Mock, patch

from calculation.extrapolation import extrapolate
from calculation.social import health_impacts_monetization
from series.annual_series import AnnualSeries
from table import table

mocked_annual_table = table.Table([{'id_measure': 1, 'id_subsector': 2, 'id_action_type': 3, '2000': 100}])
mocked_series = AnnualSeries({'2000': 2})


def _mocked_table():
    mocked_table = Mock()
    mocked_table.to_data_frame = Mock()
    mocked_table.copy = Mock(return_value='mocked_table')
    mocked_table.isna = Mock(return_value='mocked_boolean_index')
    mocked_table.index = Mock()
    mocked_table.index.get_level_values = Mock(return_value=5)
    mocked_table.loc = Mock()
    mocked_table.reduce = Mock(return_value='mocked_reduce')
    return mocked_table


def _mocked_data_source():
    mocked_data_source = Mock()
    mocked_data_source.extrapolated_annual_series = Mock(return_value=mocked_series)
    return mocked_data_source


@patch(health_impacts_monetization._value_of_life_years, Mock(return_value=mocked_series))
def test_monetization_of_health_costs_linked_to_dampness_and_mould_related_asthma_cases():
    result = health_impacts_monetization.monetization_of_health_costs_linked_to_dampness_and_mould_related_asthma_cases(
        mocked_annual_table, _mocked_data_source(), 1
    )
    assert result['2000'][1, 2, 3] == 200


@patch(extrapolate, Mock(return_value=_mocked_table()))
def test_value_of_life_years():
    result = health_impacts_monetization._value_of_life_years(_mocked_data_source(), 1, ['2000'])
    assert result['2000'] == 2


@patch(health_impacts_monetization._value_of_statistical_life, Mock(return_value=mocked_series))
def test_monetization_of_cold_weather_mortality():
    result = health_impacts_monetization.monetization_of_cold_weather_mortality(
        mocked_annual_table, _mocked_data_source(), 1
    )
    assert result['2000'][1, 2, 3] == 200


def test_value_of_statistical_life():
    result = health_impacts_monetization._value_of_statistical_life(_mocked_data_source(), 1, ['2000'])
    assert result['2000'] == 2
