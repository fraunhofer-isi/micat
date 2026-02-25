# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable = no-name-in-module

from micat.calculation import air_pollution, extrapolation
from micat.calculation.ecologic import (
    energy_saving,
    reduction_of_green_house_gas_emission_monetization,
    targets,
)
from micat.calculation.economic import grid
from micat.table.table import Table


def land_use_change(
    energy_produced, data_source, id_region, final_energy_saving_or_capacities
):
    action_type_ids = energy_produced.unique_index_values("id_action_type")
    subsector_ids = energy_produced.unique_index_values("id_subsector")

    # RES
    landuse_res = data_source.table(
        "wuppertal_landuse_res",
        {
            "id_subsector": subsector_ids,
            "id_action_type": action_type_ids,
        },
    )
    df1 = energy_produced._data_frame
    df2 = landuse_res._data_frame
    df1_aligned = df1.reorder_levels(
        ["id_subsector", "id_action_type", "id_measure"]
    ).sort_index()
    factor = df2["value"].sort_index()
    result = df1_aligned.mul(factor, axis=0)
    lui_res = (
        result.groupby(
            level=[
                "id_measure",
            ]
        )
        .sum()
        .sort_index()
    )

    # Conventional
    _substitution_factors = data_source.table(
        "fraunhofer_substitution_factors",
        {
            "id_region": str(id_region),
            "id_subsector": str(subsector_ids[0]),
            "id_action_type": str(action_type_ids[0]),
        },
    )
    _substitution_factors = extrapolation.extrapolate(
        _substitution_factors, final_energy_saving_or_capacities.years
    )
    landuse_conventional = data_source.table(
        "wuppertal_landuse_conventional",
        {},
    )
    df1 = _substitution_factors._data_frame
    df2 = landuse_conventional._data_frame
    factor = df2["value"].sort_index()
    # align factor to df1 via id_primary_energy_carrier and multiply
    weighted = df1.mul(
        factor.droplevel("id_parameter"),
        level="id_primary_energy_carrier",
        axis=0,
    )

    # sum over all index levels → one total per year
    result = weighted.sum() * energy_produced._data_frame
    lui_conventional = (
        result.groupby(
            level=[
                "id_measure",
            ]
        )
        .sum()
        .sort_index()
    )

    return Table(lui_res - lui_conventional)


# pylint: disable=too-many-locals
def ecologic_indicators(
    interim_data,
    data_source,
    id_region,
    heat_saving_final,
    electricity_saving_final,
    energy_produced,
):
    iiasa_final_subsector_parameters = interim_data["iiasa_final_subsector_parameters"]
    iiasa_final_subsector_parameters_generation = interim_data[
        "iiasa_final_subsector_parameters_generation"
    ]
    energy_saving_by_final_energy_carrier = interim_data[
        "energy_saving_by_final_energy_carrier"
    ]
    total_primary_energy_saving = interim_data["total_primary_energy_saving"]

    energy_saving_table = energy_saving.energy_saving(total_primary_energy_saving)

    reduction_of_air_pollution_table = air_pollution.reduction_of_air_pollution(
        iiasa_final_subsector_parameters,
        iiasa_final_subsector_parameters_generation,
        energy_saving_by_final_energy_carrier,
        heat_saving_final,
        electricity_saving_final,
    )

    reduction_of_green_house_gas_emission_table = (
        air_pollution.reduction_of_green_house_gas_emission(
            iiasa_final_subsector_parameters,
            iiasa_final_subsector_parameters_generation,
            energy_saving_by_final_energy_carrier,
            heat_saving_final,
            electricity_saving_final,
        )
    )

    reduction_of_mortality_morbidity_table = (
        air_pollution.reduction_of_mortality_morbidity(
            iiasa_final_subsector_parameters,
            iiasa_final_subsector_parameters_generation,
            energy_saving_by_final_energy_carrier,
            heat_saving_final,
            electricity_saving_final,
        )
    )

    reduction_of_mortality_morbidity_monetization_table = (
        air_pollution.reduction_of_mortality_morbidity_monetization(
            reduction_of_mortality_morbidity_table,
            data_source,
            id_region,
        )
    )

    reduction_of_green_house_gas_emission_monetization_table = (
        reduction_of_green_house_gas_emission_monetization.monetize(
            reduction_of_green_house_gas_emission_table,
            data_source,
            id_region,
        )
    )

    eurostat_primary_parameters = interim_data["eurostat_primary_parameters"]
    gross_available_energy = eurostat_primary_parameters.reduce("id_parameter", 2)

    renewable_energy_directive_targets = targets.impact_on_res_targets(
        gross_available_energy,
        total_primary_energy_saving,
    )

    fraunhofer_constant_parameters = data_source.table(
        "fraunhofer_constant_parameters", {"id_region": str(id_region)}
    )
    cost_of_res_statistical_transfer = fraunhofer_constant_parameters.reduce(
        "id_parameter", 61
    )

    impact_on_res_targets_monetization = targets.impact_on_res_targets_monetization(
        renewable_energy_directive_targets,
        gross_available_energy,
        total_primary_energy_saving,
        cost_of_res_statistical_transfer,
    )

    final_energy_saving_electricity = energy_saving_by_final_energy_carrier.reduce(
        "id_final_energy_carrier", [1]
    )
    del final_energy_saving_electricity["id_final_energy_carrier"]

    reduction_of_additional_capacities_in_grid = (
        grid.reduction_of_additional_capacities_in_grid(
            final_energy_saving_electricity,
            data_source,
            id_region,
        )
    )

    results = {
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

    # Check if renewables are selected
    subsector_id = energy_produced.unique_index_values("id_subsector")[0]
    if subsector_id >= 30:
        results["netLandUseChange"] = land_use_change(
            energy_produced,
            data_source,
            id_region,
            energy_saving_by_final_energy_carrier,
        )

    return results
