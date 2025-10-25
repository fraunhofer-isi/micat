# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/46
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/29
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/45
# pylint: disable = duplicate-code
import pandas as pd

from micat.calculation import extrapolation
from micat.utils import list as list_utils
from micat.table.table import Table


def reduction_of_air_pollution(
    iiasa_parameters,
    iiasa_parameters_generation,
    energy_saving_by_final_energy_carrier,
    heat_saving_final,
    electricity_saving_final,
):
    air_pollution_factor_in_kt_per_ktoe = iiasa_parameters.reduce("id_parameter", [5, 6, 7])
    reduction_in_kt = _factorial_reduction(air_pollution_factor_in_kt_per_ktoe, energy_saving_by_final_energy_carrier)

    # Adjust for electricity generation savings
    electricity_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [5, 6, 7])
    electricity_adjustment = _factorial_reduction(
        electricity_generation_factor,
        electricity_saving_final,
    )

    # Adjust for heat generation savings
    heat_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [5, 6, 7])
    heat_adjustment = _factorial_reduction(
        heat_generation_factor,
        heat_saving_final,
    )

    return reduction_in_kt + electricity_adjustment + heat_adjustment


def reduction_of_green_house_gas_emission(
    iiasa_parameters,
    iiasa_parameters_generation,
    energy_saving_by_final_energy_carrier,
    heat_saving_final,
    electricity_saving_final,
):
    ghg_factor_in_kt_per_ktoe = iiasa_parameters.query("id_parameter==4")
    reduction_in_kt = _factorial_reduction(
        ghg_factor_in_kt_per_ktoe,
        energy_saving_by_final_energy_carrier,
    )

    # Adjust for electricity generation savings
    electricity_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [4])
    electricity_adjustment = _factorial_reduction(
        electricity_generation_factor,
        electricity_saving_final,
    )

    # Adjust for heat generation savings
    heat_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [4])
    heat_adjustment = _factorial_reduction(
        heat_generation_factor,
        heat_saving_final,
    )

    result = reduction_in_kt + electricity_adjustment + heat_adjustment
    del result["id_parameter"]

    return result


def reduction_of_mortality_morbidity(  # = id_indicator 4, human_health_I
    iiasa_parameters,
    iiasa_parameters_generation,
    energy_saving_by_final_energy_carrier,
    heat_saving_final,
    electricity_saving_final,
):
    mortality_morbidity_factor = iiasa_parameters.reduce("id_parameter", [8, 9])
    reduction = _factorial_reduction(
        mortality_morbidity_factor,
        energy_saving_by_final_energy_carrier,
    )

    # Adjust for electricity generation savings
    electricity_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [8, 9])
    electricity_adjustment = _factorial_reduction(
        electricity_generation_factor,
        electricity_saving_final,
    )

    # Adjust for heat generation savings
    heat_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [8, 9])
    heat_adjustment = _factorial_reduction(
        heat_generation_factor,
        heat_saving_final,
    )
    return reduction + electricity_adjustment + heat_adjustment


def reduction_of_mortality_morbidity_monetization(
    reduction_of_mortality_morbidity_table,
    data_source,
    id_region,
):
    years = reduction_of_mortality_morbidity_table.years

    who_parameters = data_source.table("who_parameters", {"id_region": str(id_region)})
    value_of_statistical_life = who_parameters.reduce("id_parameter", 37)
    extrapolated_value_of_statistical_life = extrapolation.extrapolate_series(value_of_statistical_life, years)

    iiasa_lost_working_days_monetization_factors = data_source.table(
        "iiasa_lost_working_days_monetization_factors", {"id_region": str(id_region)}
    )
    hospitalisation_admission = iiasa_lost_working_days_monetization_factors.reduce("id_parameter", 63)
    extrapolated_hospitalisation_admission = extrapolation.extrapolate_series(
        hospitalisation_admission,
        years,
    )
    mortality = (
        reduction_of_mortality_morbidity_table.query("id_parameter == [8]") * extrapolated_value_of_statistical_life
    )

    hospitalisation = (
        reduction_of_mortality_morbidity_table.query("id_parameter == [9]") * extrapolated_hospitalisation_admission
    )
    health_costs = Table(pd.concat([mortality._data_frame, hospitalisation._data_frame]))
    del health_costs["id_parameter"]
    return health_costs


def reduction_of_lost_work_days(
    iiasa_parameters,
    iiasa_parameters_generation,
    energy_saving_by_final_energy_carrier,
    heat_saving_final,
    electricity_saving_final,
):
    lost_work_days_factor = iiasa_parameters.query("id_parameter==23")
    reduction = _factorial_reduction(
        lost_work_days_factor,
        energy_saving_by_final_energy_carrier,
    )

    # Adjust for electricity generation savings
    electricity_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [23])
    electricity_adjustment = _factorial_reduction(
        electricity_generation_factor,
        electricity_saving_final,
    )

    # Adjust for heat generation savings
    heat_generation_factor = iiasa_parameters_generation.reduce("id_parameter", [23])
    heat_adjustment = _factorial_reduction(
        heat_generation_factor,
        heat_saving_final,
    )
    results = reduction + electricity_adjustment + heat_adjustment
    del results["id_parameter"]
    return results


def _factorial_reduction(
    conversion_factor_by_final_energy_carrier,
    energy_saving_by_final_energy_carrier,
):
    year_numbers = list_utils.string_to_integer(energy_saving_by_final_energy_carrier.columns)
    extrapolated_factor = extrapolation.extrapolate(conversion_factor_by_final_energy_carrier, year_numbers)
    output = energy_saving_by_final_energy_carrier * extrapolated_factor

    if output.contains_nan():
        message = (
            "Result of multiplication contains NaN values. " + "Factors need to be provided for all energy carriers."
        )
        raise KeyError(message)

    table = output.aggregate_to(["id_measure", "id_parameter"])
    return table
