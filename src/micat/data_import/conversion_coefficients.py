# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/47
import numpy as np

from micat.table.table import Table


def conversion_coefficients(inout):
    # pylint: disable=too-many-locals
    heat_in_carriers = inout["heat_in"]
    heat_out = inout["heat_out"]
    electricity_in_carriers = inout["electricity_in"]
    electricity_out = inout["electricity_out"]
    chp_in_carriers = inout["chp_in"]
    chp_heat_out = inout["chp_heat_out"]
    chp_electricity_out = inout["chp_electricity_out"]

    sigma_heat = _input_output_ratio(heat_in_carriers, heat_out)
    sigma_electricity = _input_output_ratio(electricity_in_carriers, electricity_out)

    # note: tau_heat and tau_electricity might contain NaN values (for the case that both outputs are zero).
    # However, those Nan values will not be applied, because there is a special handling for this case
    # in the calculation of the coefficients.
    # The input for tau_heat and tau_electricity must not contain NaN values.
    tau_heat = _chp_usage_share(
        sigma_heat,
        chp_heat_out,
        sigma_electricity,
        chp_electricity_out,
    )

    tau_electricity = _chp_usage_share(
        sigma_electricity,
        chp_electricity_out,
        sigma_heat,
        chp_heat_out,
    )

    table = None
    primary_energy_carrier_ids = heat_in_carriers.unique_index_values("id_primary_energy_carrier")
    for carrier_id in primary_energy_carrier_ids:
        heat_in = heat_in_carriers.reduce("id_primary_energy_carrier", carrier_id)
        chp_in = chp_in_carriers.reduce("id_primary_energy_carrier", carrier_id)
        k_heat = _coefficient(heat_in, tau_heat, chp_in, heat_out, chp_heat_out)
        k_heat = k_heat.insert_index_column("id_parameter", 1, 20)
        k_heat = k_heat.insert_index_column("id_primary_energy_carrier", 2, carrier_id)
        if table is None:
            table = k_heat
        else:
            table = Table.concat([table, k_heat])

        electricity_in = electricity_in_carriers.reduce("id_primary_energy_carrier", carrier_id)
        k_electricity = _coefficient(electricity_in, tau_electricity, chp_in, electricity_out, chp_electricity_out)
        k_electricity = k_electricity.insert_index_column("id_parameter", 1, 21)
        k_electricity = k_electricity.insert_index_column("id_primary_energy_carrier", 2, carrier_id)
        table = Table.concat([table, k_electricity])

    return table


def _coefficient(
    energy_input,
    chp_share,
    chp_input,
    energy_output,
    chp_output,
):
    normal_result = (energy_input + chp_share * chp_input) / (energy_output + chp_output)

    special_result = energy_input / energy_output

    is_zero = chp_output.eq(0)
    result = normal_result.where(~is_zero, special_result)

    return result


def _chp_usage_share(
    input_output_ratio_left,
    chp_output_left,
    input_output_ratio_right,
    chp_output_right,
):
    input_left = input_output_ratio_left * chp_output_left
    input_right = input_output_ratio_right * chp_output_right
    result = input_left / (input_left + input_right)
    return result


def _input_output_ratio(
    energy_input_table,
    energy_output_table,
):
    total_energy_input = energy_input_table.aggregate_to(["id_region"])
    normal_result = total_energy_input.divide_without_checks(energy_output_table)
    normal_result = normal_result.replace([np.inf, -np.inf], np.nan)
    mean = normal_result.mean()
    result = normal_result.fillna(mean)
    return result
