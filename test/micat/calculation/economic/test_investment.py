# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.calculation.economic import investment
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch


def test_annual_investment_cost_in_euro():
    investment_cost = Table([{"id_foo": 1, "2000": 10, "2010": 20, "2020": 30}])
    years = [2000, 2010, 2020]
    with patch(investment.investment_cost_in_euro, investment_cost):
        final_energy_saving_by_action_type = Mock()
        final_energy_saving_by_action_type.years = years
        result = investment.annual_investment_cost_in_euro(final_energy_saving_by_action_type, "mocked_data_source")
        assert result.years == years
        assert result["2000"][1] == 10
        assert result["2010"][1] == 1
        assert result["2020"][1] == 1


@patch(investment._default_investment)
def test_investment_cost_in_euro():
    investment_table = Table(
        [
            {
                "id_measure": 1,
                "id_subsector": 1,
                "id_action_type": 1,
                "2000": 10,
            }
        ]
    )

    def mocked_measure_specific_parameter(
        _final_energy_saving_by_action_type,
        _id_parameter,
        provide_default_value,
        _is_value_table=False,
    ):
        provide_default_value(
            "mocked_id_measure",
            "mocked_id_subsector",
            "mocked_id_action_type",
            "mocked_year",
            "mocked_saving",
        )
        return investment_table

    data_source = Mock()
    data_source.measure_specific_parameter = mocked_measure_specific_parameter

    result = investment.investment_cost_in_euro(
        Mock(),
        data_source,
    )
    assert result["2000"][1, 1] == 10


def test_annual_years():
    result = investment._annual_years([2000, 2005])
    assert result == [2000, 2001, 2002, 2003, 2004, 2005]


class TestDifferenceToPreviousYear:
    def test_first_year(self):
        cumulated_data = Table([{"id_foo": 1, "2000": 10, "2010": 40}])
        result = investment._difference_to_previous_year(
            "mocked_value",
            "mocked_index",
            "2000",
            cumulated_data,
        )
        assert result == "mocked_value"

    def test_second_year(self):
        cumulated_data = Table([{"id_foo": 1, "2000": 10, "2001": 40}])
        result = investment._difference_to_previous_year(
            40,
            1,
            "2001",
            cumulated_data,
        )
        assert result == 30


@patch(
    investment._specific_investment_cost,
    100,
)
def test_default_investment():
    saving = 1000
    result = investment._default_investment(
        saving,
        "mocked_investment_cost_per_ktoe",
        "mocked_id_action_type",
        "mocked_year",
    )
    assert result == 1000 * 1000 * 1000 * 100


def test_specific_investment_cost():
    mocked_series = AnnualSeries({"2000": "mocked_result"})

    investment_cost_per_ktoe = Mock()
    investment_cost_per_ktoe.reduce = Mock(mocked_series)
    year = 2000
    result = investment._specific_investment_cost(
        investment_cost_per_ktoe,
        "mocked_id_action_type",
        year,
    )
    assert result == "mocked_result"


@patch(extrapolation.extrapolate, "mocked_result")
def test_investment_cost_per_ktoe():
    data_source = Mock()
    result = investment._investment_cost_per_ktoe(data_source, "mocked_years")
    assert result == "mocked_result"
