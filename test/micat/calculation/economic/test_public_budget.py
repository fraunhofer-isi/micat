# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.economic import investment, public_budget
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


mocked_investment_cost = Table(
    [{"id_measure": 1, "id_action_type": 1, "2020": 1000, "2030": 1000}]
)


@patch(
    investment.investment_cost_in_euro,
    mocked_investment_cost,
)
@patch(
    public_budget._beta_by_measure,
    Table([{"id_measure": 1, "2020": 0.5, "2030": 0.5}]),
)
@patch(
    public_budget._subsidy_rate_by_measure,
    Table([{"id_measure": 1, "2020": 20, "2030": 20}]),
)
def test_impact_on_public_budget():
    final_energy_saving_or_capacities = Table(
        [{"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 100, "2030": 100}]
    )

    public_revenues_table = Table(
        [{"id_parameter": 82, "id_subsector": 1, "id_action_type": 1, "2020": 50, "2030": 50}]
    )
    unemployment_expenses_table = Table(
        [{"id_parameter": 83, "id_subsector": 1, "id_action_type": 1, "2020": -10, "2030": -10}]
    )

    call_count = {"n": 0}
    tables = [public_revenues_table, unemployment_expenses_table]

    def mock_table(_table_name, _where_clause=None):
        result = tables[call_count["n"]]
        call_count["n"] += 1
        return result

    data_source = Mock()
    data_source.table = mock_table

    result = public_budget.impact_on_public_budget(
        final_energy_saving_or_capacities,
        data_source,
        1,
    )

    # PB = (C/ES * PR) - (C/ES * UE * beta) - (INV * SR / 100)
    # UE is negative in the data (expenses reduce public spending)
    # PB = (100 * 50) - (100 * (-10) * 0.5) - (1000 * 20 / 100)
    # PB = 5000 - (-500) - 200 = 5300
    assert result["2020"][1] == 5300
    assert result["2030"][1] == 5300


@patch(
    extrapolation.extrapolate_series,
    Mock("mocked_result"),
)
def test_default_beta():
    data_source = Mock()
    data_source.annual_series = Mock("mocked_series")

    result = public_budget._default_beta(
        data_source,
        "mocked_id_region",
        "mocked_years",
    )
    assert result == "mocked_result"


@patch(
    public_budget._default_beta,
    Mock(Mock()),
)
def test_beta_by_measure():
    mocked_beta = Table(
        [{"id_measure": 1, "id_subsector": 2, "id_action_type": 3, "2020": 0.5}]
    )

    def mocked_measure_specific_parameter(
        _energy_saving, _id_parameter, provide_default, _is_value_table=False
    ):
        mocked_value = provide_default(1, 2, 3, "mocked_year", "mocked_saving")
        assert mocked_value
        return mocked_beta

    data_source = Mock()
    data_source.measure_specific_parameter = mocked_measure_specific_parameter

    mocked_final_energy_saving_or_capacities = Mock()
    mocked_final_energy_saving_or_capacities.years = ["2020"]

    result = public_budget._beta_by_measure(
        mocked_final_energy_saving_or_capacities,
        data_source,
        "mocked_id_region",
    )
    assert result["2020"][1] == 0.5


@patch(
    extrapolation.extrapolate_series,
    Mock("mocked_result"),
)
def test_default_subsidy_rate():
    data_source = Mock()
    data_source.annual_series = Mock("mocked_series")

    result = public_budget._default_subsidy_rate(
        data_source,
        "mocked_id_region",
        "mocked_years",
    )
    assert result == "mocked_result"


@patch(
    public_budget._default_subsidy_rate,
    Mock(Mock()),
)
def test_subsidy_rate_by_measure():
    mocked_subsidy_rate = Table(
        [{"id_measure": 1, "id_subsector": 2, "id_action_type": 3, "2020": 20}]
    )

    def mocked_measure_specific_parameter(
        _energy_saving, _id_parameter, provide_default, _is_value_table=False
    ):
        mocked_value = provide_default(1, 2, 3, "mocked_year", "mocked_saving")
        assert mocked_value
        return mocked_subsidy_rate

    data_source = Mock()
    data_source.measure_specific_parameter = mocked_measure_specific_parameter

    mocked_final_energy_saving_or_capacities = Mock()
    mocked_final_energy_saving_or_capacities.years = ["2020"]

    result = public_budget._subsidy_rate_by_measure(
        mocked_final_energy_saving_or_capacities,
        data_source,
        "mocked_id_region",
    )
    assert result["2020"][1] == 20
