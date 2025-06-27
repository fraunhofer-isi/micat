# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import numpy as np

from micat.calculation import mode
from micat.calculation.economic import eurostat, primes, production
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch, raises


class TestPrimaryProduction:
    @patch(mode.is_eurostat_mode, True)
    def test_for_eurostat_mode(self):
        mocked_parameters = Mock()
        mocked_parameters.reduce = Mock("mocked_result")

        with patch(eurostat.primary_parameters, Mock(mocked_parameters)):
            result = production.primary_production("mocked_data_source", "mocked_id_region", "mocked_years")
            assert result == "mocked_result"

    @patch(mode.is_eurostat_mode, False)
    def test_for_primes_mode(self):
        mocked_parameters = Mock()
        mocked_parameters.reduce = Mock("mocked_result")

        with patch(primes.primary_parameters, Mock(mocked_parameters)):
            result = production.primary_production("mocked_data_source", "mocked_id_region", "mocked_years")
            assert result == "mocked_result"


class TestChangeInUnitCostsOfProduction:
    change_in_energy_purchase = Table(
        [
            {"id_measure": 1, "id_subsector": 10, "2020": 1, "2030": 20},
        ]
    )

    output = Table(
        [
            {"id_subsector": 10, "2020": 2, "2030": 0},
        ]
    )

    @patch(
        production._change_in_energy_purchase,
        change_in_energy_purchase,
    )
    @patch(
        production._output,
        Mock(output),
    )
    def test_normal_usage(self):
        result = production.change_in_unit_costs_of_production(
            "mocked_reduction_of_energy_cost",
            "mocked_gross_domestic_product_primes",
            "mocked_gross_domestic_product_primes_2015",
            "mocked_data_source",
            "mocked_id_region",
        )
        assert result["2020"][1] == -1 / 2
        assert result["2030"][1] == 0

    infinite_change_in_energy_purchase = Table(
        [
            {"id_measure": 1, "id_subsector": 10, "2020": 1, "2030": np.inf},
        ]
    )

    @patch(
        production._change_in_energy_purchase,
        infinite_change_in_energy_purchase,
    )
    def test_with_infinite_values(self):
        with raises(ValueError):
            production.change_in_unit_costs_of_production(
                "mocked_reduction_of_energy_cost",
                "mocked_gross_domestic_product_primes",
                "mocked_gross_domestic_product_primes_2015",
                "mocked_data_source",
                "mocked_id_region",
            )


def test_change_in_energy_purchase():
    reduction_of_energy_cost = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_foo": 1, "2000": 1},
            {"id_measure": 1, "id_subsector": 1, "id_foo": 2, "2000": 1},
        ]
    )
    result = production._change_in_energy_purchase(reduction_of_energy_cost)
    assert result["2000"][1, 1] == 2


output_2015 = ValueTable(
    [
        {"id_subsector": 1, "value": 10_000_000},
        {"id_subsector": 2, "value": 20_000_000},
    ]
)


@patch(
    production._output_2015,
    output_2015,
)
def test_output():
    gross_domestic_product = AnnualSeries({"2020": 1, "2025": 2})

    gross_domestic_product_2015 = 2

    result = production._output(
        gross_domestic_product,
        gross_domestic_product_2015,
        "mocked_data_source",
        "mocked_id_region",
        "mocked_subsector_ids",
    )
    assert result["2020"][1] == 1 / 2 * 10_000_000
    assert result["2020"][2] == 1 / 2 * 20_000_000


def test_output_2015():
    eurostat_sector_parameters = Table(
        [
            {"id_parameter": 50, "id_subsector": 1, "2000": 1},
            {"id_parameter": 999, "id_subsector": 1, "2000": 2},
        ]
    )

    data_source = Mock()
    data_source.table = Mock(eurostat_sector_parameters)
    result = production._output_2015(
        data_source,
        "mocked_id_region",
        "mocked_subsector_ids",
    )
    assert result["2000"] == 1
