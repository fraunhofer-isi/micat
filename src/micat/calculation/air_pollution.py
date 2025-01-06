# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/46
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/29
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/45
# pylint: disable = duplicate-code

from micat.calculation import extrapolation
from micat.utils import list as list_utils


def reduction_of_air_pollution(
    iiasa_parameters,
    energy_saving_by_final_energy_carrier,
):
    air_pollution_factor_in_kt_per_ktoe = iiasa_parameters.reduce("id_parameter", [5, 6, 7])
    reduction_in_kt = _factorial_reduction(air_pollution_factor_in_kt_per_ktoe, energy_saving_by_final_energy_carrier)
    return reduction_in_kt


def reduction_of_green_house_gas_emission(
    iiasa_parameters,
    energy_saving_by_final_energy_carrier,
):
    ghg_factor_in_kt_per_ktoe = iiasa_parameters.query("id_parameter==4")
    reduction_in_kt = _factorial_reduction(
        ghg_factor_in_kt_per_ktoe,
        energy_saving_by_final_energy_carrier,
    )
    reduction_in_kt = reduction_in_kt.reduce("id_parameter", [4])
    del reduction_in_kt["id_parameter"]
    return reduction_in_kt


def reduction_of_mortality_morbidity(  # = id_indicator 4, human_health_I
    iiasa_parameters,
    energy_saving_by_final_energy_carrier,
):
    mortality_morbidity_factor = iiasa_parameters.reduce("id_parameter", [8, 9])
    reduction = _factorial_reduction(
        mortality_morbidity_factor,
        energy_saving_by_final_energy_carrier,
    )
    # TO DO: can this include two values for id_parameter? If not, remove id_parameter from result
    # it seems that id_parameter = 9 is missing in iiasa data?
    return reduction


def reduction_of_mortality_morbidity_monetization(
    reduction_of_mortality_morbidity_table,
    data_source,
    id_region,
):
    years = reduction_of_mortality_morbidity_table.years

    who_parameters = data_source.table("who_parameters", {"id_region": str(id_region)})

    value_of_statistical_life = who_parameters.reduce("id_parameter", 37)
    extrapolated_value_of_statistical_life = extrapolation.extrapolate_series(value_of_statistical_life, years)
    health_costs = reduction_of_mortality_morbidity_table * extrapolated_value_of_statistical_life
    del health_costs["id_parameter"]
    return health_costs


def reduction_of_lost_work_days(
    iiasa_parameters,
    energy_saving_by_final_energy_carrier,
):
    lost_work_days_factor = iiasa_parameters.query("id_parameter==23")
    reduction = _factorial_reduction(
        lost_work_days_factor,
        energy_saving_by_final_energy_carrier,
    )
    reduction = reduction.reduce("id_parameter", [23])
    del reduction["id_parameter"]
    return reduction


def subsector_parameters(
    data_source,
    id_region,
    subsector_ids,
):
    where_clause = {
        "id_region": str(id_region),
        "id_subsector": subsector_ids,
    }
    table = data_source.table("iiasa_final_subsector_parameters", where_clause)
    return table


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
