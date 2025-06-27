# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import (
    buildings,
    calculation_economic,
    employment,
    energy_cost,
    energy_efficiency,
    energy_intensity,
    grid,
    gross_available_energy,
    gross_domestic_product,
    import_dependency,
    production,
    supplier_diversity,
)

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch


@patch(gross_available_energy.gross_available_energy)
@patch(production.primary_production)
@patch(energy_cost.reduction_of_energy_cost_by_final_energy_carrier)
@patch(gross_domestic_product.gross_domestic_product)
@patch(gross_domestic_product.gross_domestic_product_2015)
@patch(gross_domestic_product.impact_on_gross_domestic_product)
@patch(energy_intensity.energy_intensity)
@patch(import_dependency.impact_on_import_dependency)
@patch(employment.additional_employment)
@patch(buildings.added_asset_value_of_buildings)
@patch(production.change_in_unit_costs_of_production)
@patch(energy_efficiency.turnover_of_energy_efficiency_goods)
@patch(grid.monetization_of_reduction_of_additional_capacities_in_grid)
@patch(supplier_diversity.change_in_supplier_diversity_by_energy_efficiency_impact)
class TestEconomicIndicators:
    def test_indicators(self):
        mocked_interim_data = Mock()
        mocked_ecologic_indicators = Mock()

        result = calculation_economic.economic_indicators(
            "mocked_final_energy_saving_by_action_type",
            "mocked_population_of_municipality",
            mocked_interim_data,
            mocked_ecologic_indicators,
            "mocked_data_source",
            "mocked_id_region",
            "mocked_years",
        )
        assert len(result) == 10
