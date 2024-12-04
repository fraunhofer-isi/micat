# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable = no-name-in-module

from micat.calculation import air_pollution
from micat.calculation.ecologic import (
    energy_saving,
    reduction_of_green_house_gas_emission_monetization,
    targets,
)
from micat.calculation.economic import grid


# pylint: disable=too-many-locals
def ecologic_indicators(
    interim_data,
    data_source,
    id_mode,
    id_region,
):
    air_pollution_parameters = interim_data["air_pollution_parameters"]
    energy_saving_by_final_energy_carrier = interim_data["energy_saving_by_final_energy_carrier"]
    total_primary_energy_saving = interim_data["total_primary_energy_saving"]

    energy_saving_table = energy_saving.energy_saving(total_primary_energy_saving)

    reduction_of_air_pollution_table = air_pollution.reduction_of_air_pollution(
        air_pollution_parameters,
        energy_saving_by_final_energy_carrier,
    )

    reduction_of_green_house_gas_emission_table = air_pollution.reduction_of_green_house_gas_emission(
        air_pollution_parameters,
        energy_saving_by_final_energy_carrier,
    )

    reduction_of_mortality_morbidity_table = air_pollution.reduction_of_mortality_morbidity(
        air_pollution_parameters,
        energy_saving_by_final_energy_carrier,
    )

    reduction_of_mortality_morbidity_monetization_table = air_pollution.reduction_of_mortality_morbidity_monetization(
        reduction_of_mortality_morbidity_table,
        data_source,
        id_region,
    )

    reduction_of_green_house_gas_emission_monetization_table = (
        reduction_of_green_house_gas_emission_monetization.monetize(
            reduction_of_green_house_gas_emission_table,
            data_source,
            id_region,
        )
    )

    eurostat_primary_parameters = interim_data["1_2_3_20_21_GAE_PP_NEU_k-coefficients"]
    gross_available_energy = eurostat_primary_parameters.reduce("id_parameter", 2)

    renewable_energy_directive_targets = targets.impact_on_res_targets(
        gross_available_energy,
        total_primary_energy_saving,
    )

    fraunhofer_constant_parameters = data_source.table("61_cost_of_RES_statistical_transfers", {"id_region": str(id_region)})
    cost_of_res_statistical_transfer = fraunhofer_constant_parameters.reduce("id_parameter", 61)

    impact_on_res_targets_monetization = targets.impact_on_res_targets_monetization(
        renewable_energy_directive_targets,
        gross_available_energy,
        total_primary_energy_saving,
        cost_of_res_statistical_transfer,
    )

    final_energy_saving_electricity = energy_saving_by_final_energy_carrier.reduce("id_final_energy_carrier", [1])
    del final_energy_saving_electricity["id_final_energy_carrier"]

    reduction_of_additional_capacities_in_grid = grid.reduction_of_additional_capacities_in_grid(
        final_energy_saving_electricity,
        data_source,
        id_mode,
        id_region,
    )

    return {
        "energySaving": energy_saving_table,
        "impactOnResTargetsMonetization": impact_on_res_targets_monetization,
        "reductionOfAdditionalCapacitiesInGrid": reduction_of_additional_capacities_in_grid,
        "reductionOfMortalityMorbidity": reduction_of_mortality_morbidity_table,
        "reductionOfMortalityMorbidityMonetization": reduction_of_mortality_morbidity_monetization_table,
        "reductionOfAirPollution": reduction_of_air_pollution_table,
        "reductionOfGreenHouseGasEmission": reduction_of_green_house_gas_emission_table,
        "reductionOfGreenHouseGasEmissionMonetization": reduction_of_green_house_gas_emission_monetization_table,
        "renewableEnergyDirectiveTargets": renewable_energy_directive_targets,
    }
