# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/47


def total_primary_energy_saving(
    conventional_primary_energy_saving,
    additional_primary_energy_saving,
):
    result = conventional_primary_energy_saving + additional_primary_energy_saving
    return result


def primary_energy_saving(
    final_energy_saving,
    eurostat_primary_parameters,
    _h2_coefficient,
):
    heat_saving = final_energy_saving.reduce("id_final_energy_carrier", [6])
    del heat_saving["id_final_energy_carrier"]

    electricity_saving = final_energy_saving.reduce("id_final_energy_carrier", [1])
    del electricity_saving["id_final_energy_carrier"]

    heat_coefficient = eurostat_primary_parameters.reduce("id_parameter", 20)
    electricity_coefficient = eurostat_primary_parameters.reduce("id_parameter", 21)

    # TO DO: remove this is comments if h2 is a constant
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/156

    # h2_saving = final_energy_saving.reduce("id_final_energy_carrier", 8)
    # h2_saving_times_h2_coefficient = multiply_dataframe_with_series(h2_saving, h2_coefficient)
    # h2_saving_times_h2_coefficient_times_electricity_coefficient =\
    #     merge_and_multiply_tables(h2_saving_times_h2_coefficient, electricity_coefficient)

    # TO DO implement equation #47 B when the data is available

    heat_saving_times_coefficient = heat_saving * heat_coefficient
    electricity_saving_times_coefficient = electricity_saving * electricity_coefficient

    result = (
        heat_saving_times_coefficient + electricity_saving_times_coefficient
    )  # + h2_saving_times_h2_coefficient_times_electricity_coefficient
    return result


def convert_units_of_measure_specific_parameters(measure_specific_parameters):
    for id_measure, entry in measure_specific_parameters.items():
        parameters = entry["parameters"]
        for parameter_row in parameters:
            id_parameter = parameter_row["id_parameter"]
            _convert_investment_cost_to_euro(id_parameter, parameter_row)

    return measure_specific_parameters


def _convert_investment_cost_to_euro(id_parameter, parameter_row):
    # Multiply investment cost by 1,000,000, since investment costs are converted beforehand
    # (see investment.py -> investment_cost_in_euro())
    if id_parameter == 40:  # Investment cost
        for key, value in parameter_row.items():
            if key != "id_parameter":
                parameter_row[key] = value * 1000000
