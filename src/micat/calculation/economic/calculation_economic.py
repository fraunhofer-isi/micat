# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import (
    buildings,
    employment,
    energy_cost,
    energy_efficiency,
    energy_intensity,
    grid,
    gross_available_energy,
    gross_domestic_product,
    import_dependency,
    production,
)


def economic_indicators(  # pylint: disable=too-many-locals
    final_energy_saving_or_capacities,
    population_of_municipality,
    interim_data,
    ecologic_indicators,
    data_source,
    id_region,
    years,
):
    total_primary_energy_saving = interim_data["total_primary_energy_saving"]
    energy_saving_by_final_energy_carrier = interim_data["energy_saving_by_final_energy_carrier"]

    scaled_gross_available_energy = gross_available_energy.gross_available_energy(
        data_source,
        id_region,
        years,
        population_of_municipality,
    )

    primary_production = production.primary_production(
        data_source,
        id_region,
        years,
    )

    additional_primary_energy_saving = interim_data["additional_primary_energy_saving"]

    reduction_of_energy_cost = interim_data["reduction_of_energy_cost"]

    reduction_of_energy_cost_by_final_energy_carrier = energy_cost.reduction_of_energy_cost_by_final_energy_carrier(
        reduction_of_energy_cost,
    )

    scaled_gross_domestic_product = gross_domestic_product.gross_domestic_product(
        data_source,
        id_region,
        years,
        population_of_municipality,
    )

    #    scaled_gross_domestic_product_2015 = gross_domestic_product.gross_domestic_product_2015(
    #        data_source,
    #        id_region,
    #        population_of_municipality,
    #    )

    impact_on_gross_domestic_product = gross_domestic_product.impact_on_gross_domestic_product(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    )

    # TO DO: use different sources for non_energy_use, depending on id_mode? #268
    # eurostat_primary_parameters = interim_data["eurostat_primary_parameters"]
    # primary_non_energy_use = eurostat_primary_parameters.reduce("id_parameter", 3)

    #    energy_intensity_table = energy_intensity.energy_intensity(
    #        scaled_gross_available_energy,
    #        scaled_gross_domestic_product,
    #        impact_on_gross_domestic_product,
    #        primary_non_energy_use,
    #        additional_primary_energy_saving,
    #    )

    energy_intensity_difference = energy_intensity.energy_intensity_difference(
        scaled_gross_available_energy,
        scaled_gross_domestic_product,
        impact_on_gross_domestic_product,
        # primary_non_energy_use,
        additional_primary_energy_saving,
    )

    reduction_of_import_dependency_table = import_dependency.impact_on_import_dependency(
        total_primary_energy_saving,
        primary_production,
        scaled_gross_available_energy,
        # primary_non_energy_use,
    )

    additional_employment = employment.additional_employment(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    )

    added_asset_value_of_buildings = buildings.added_asset_value_of_buildings(
        reduction_of_energy_cost,
        data_source,
        id_region,
        years,
    )

    #    change_in_unit_costs_of_production = production.change_in_unit_costs_of_production(
    #        reduction_of_energy_cost,
    #        scaled_gross_domestic_product,
    #        scaled_gross_domestic_product_2015,
    #        data_source,
    #        id_region,
    #    )

    turnover_of_energy_efficiency_goods = energy_efficiency.turnover_of_energy_efficiency_goods(
        final_energy_saving_or_capacities,
        data_source,
    )

    reduction_of_additional_capacities_in_grid = ecologic_indicators["reductionOfAdditionalCapacitiesInGrid"]

    monetization_of_reduction_of_additional_capacities_in_grid = (
        grid.monetization_of_reduction_of_additional_capacities_in_grid(
            reduction_of_additional_capacities_in_grid,
            data_source,
        )
    )
    #
    #    change_in_supplier_diversity_by_energy_efficiency_impact = (
    #        supplier_diversity.change_in_supplier_diversity_by_energy_efficiency_impact(
    #            energy_saving_by_final_energy_carrier,
    #            data_source,
    #            id_region,
    #        )
    #    )

    return {
        "addedAssetValueOfBuildings": added_asset_value_of_buildings,
        "additionalEmployment": additional_employment,
        # "changeInUnitCostsOfProduction": change_in_unit_costs_of_production,
        # "changeInSupplierDiversityByEnergyEfficiencyImpact": change_in_supplier_diversity_by_energy_efficiency_impact,
        "energyIntensity": energy_intensity_difference,
        "impactOnGrossDomesticProduct": impact_on_gross_domestic_product,
        "reductionOfAdditionalCapacitiesInGridMonetization": monetization_of_reduction_of_additional_capacities_in_grid,
        "reductionOfEnergyCost": reduction_of_energy_cost_by_final_energy_carrier,
        "reductionOfImportDependency": reduction_of_import_dependency_table,
        "turnoverOfEnergyEfficiencyGoods": turnover_of_energy_efficiency_goods,
    }
