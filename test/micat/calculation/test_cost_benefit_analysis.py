# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import cost_benefit_analysis, extrapolation
from micat.calculation.economic import investment
from micat.calculation.social import lifetime
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


@patch(
    investment.investment_cost_in_euro,
    Table([{"id_measure": 1, "id_action_type": 1, "2000": 10, "2010": 20, "2020": 30}]),
)
@patch(
    lifetime.measure_specific_lifetime,
    Mock("mocked_lifetime"),
)
@patch(
    cost_benefit_analysis._subsidy_rate_by_measure,
    Mock("mocked_subsidy_rate"),
)
def test_parameters():
    mocked_table = Mock()
    mocked_table.reduce = Mock("mocked_reduce")

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    mocked_final_energy_saving_or_capacities = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2000": 10},
        ]
    )

    mocked_ecologic_indicators = {
        "reductionOfGreenHouseGasEmission": Table(
            [
                {"id_measure": 1, "2000": 1},
            ]
        )
    }

    parameters = cost_benefit_analysis.parameters(
        mocked_final_energy_saving_or_capacities,
        ecologic_indicators=mocked_ecologic_indicators,
        id_region=1,
        data_source=mocked_data_source,
        starting_year=None,
    )
    assert parameters["lifetime"] == "mocked_lifetime"
    assert parameters["subsidyRate"] == "mocked_subsidy_rate"


@patch(
    extrapolation.extrapolate_series,
    Mock("mocked_result"),
)
def test_default_subsidy_rate():
    mocked_table = Mock()
    mocked_table.reduce = Mock("mocked_reduce")

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    result = cost_benefit_analysis._default_subsidy_rate(
        mocked_data_source,
        "mocked_id_region",
        "mocked_years",
    )
    assert result == "mocked_result"


@patch(
    cost_benefit_analysis._default_subsidy_rate,
    Mock(Mock()),
)
def test_subsidy_rate_by_measure():
    mocked_subsidy_rate = Table([{"id_measure": 1, "id_subsector": 2, "id_action_type": 3, "2000": 99}])

    def mocked_measure_specific_parameter(_energy_saving, _id_parameter, provide_default, _is_value_table=False):
        mocked_value = provide_default(1, 2, 3, "mocked_year", "mocked_saving")
        assert mocked_value
        return mocked_subsidy_rate

    mocked_table = Mock()
    mocked_table.reduce = Mock("mocked_reduce")

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)
    mocked_data_source.measure_specific_parameter = mocked_measure_specific_parameter

    mocked_final_energy_saving_or_capacities = Mock()
    mocked_final_energy_saving_or_capacities.years = ["2000"]

    result = cost_benefit_analysis._subsidy_rate_by_measure(
        mocked_final_energy_saving_or_capacities,
        mocked_data_source,
        "mocked_id_region",
    )
    assert result["2000"][1] == 99
