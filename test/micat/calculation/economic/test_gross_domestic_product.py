# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import (
    gross_domestic_product,
    investment,
    population,
    primes,
)
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch

annual_investment_in_euro = Table(
    [
        {"id_measure": 1, "id_action_type": 1, "2020": 10000, "2030": 20000},
    ]
)


@patch(
    investment.annual_investment_cost_in_euro,
    annual_investment_in_euro,
)
def test_impact_on_gross_domestic_product():
    final_energy_saving_or_capacities = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 10, "2030": 20},
        ]
    )

    e3m_parameters = ValueTable(
        [
            {"id_parameter": 38, "id_action_type": 1, "value": 0.01},
        ]
    )

    data_source = Mock()
    data_source.table = Mock(e3m_parameters)

    result = gross_domestic_product.impact_on_gross_domestic_product(
        final_energy_saving_or_capacities,
        data_source,
        "mocked_id_region",
    )

    assert result["2020"][1] == 0.01 * 10000
    assert result["2030"][1] == 0.01 * 20000


@patch(primes.parameters)
@patch(population.scale_by_population, "mocked_result")
def test_gross_domestic_product():
    result = gross_domestic_product.gross_domestic_product(
        "mocked_data_source",
        "mocked_id_region",
        "mocked_years",
    )
    assert result == "mocked_result"


@patch(primes.parameters)
@patch(population.scale_by_population, "mocked_result")
def test_gross_domestic_product_2015():
    result = gross_domestic_product.gross_domestic_product_2015(
        "mocked_data_source",
        "mocked_id_region",
    )
    assert result == "mocked_result"
