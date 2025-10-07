# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
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
    conversion_efficiency,
):
    # H2 and sythentic fuels
    h2_saving = final_energy_saving.reduce("id_final_energy_carrier", [7])
    del h2_saving["id_final_energy_carrier"]
    common_years = h2_saving._data_frame.columns.intersection(_h2_coefficient._data_frame.columns)
    h2_coefficient = _h2_coefficient.reduce("id_parameter", 22)
    h2_coefficient._data_frame = h2_coefficient._data_frame[common_years]
    h2_conversion_efficiency = conversion_efficiency.reduce("id_final_energy_carrier", 7)
    h2_conversion_efficiency._data_frame = h2_conversion_efficiency._data_frame[common_years]
    h2_saving_final = h2_saving * h2_coefficient / h2_conversion_efficiency

    # Heat
    heat_saving = final_energy_saving.reduce("id_final_energy_carrier", [6])
    del heat_saving["id_final_energy_carrier"]
    heat_coefficient = eurostat_primary_parameters.reduce("id_parameter", 20)
    heat_conversion_efficiency = conversion_efficiency.reduce("id_final_energy_carrier", 6)
    heat_conversion_efficiency._data_frame = heat_conversion_efficiency._data_frame[common_years]
    heat_saving_final = heat_saving * heat_coefficient / heat_conversion_efficiency

    # Electricity
    # Calculate total energy savings (includes avoided hydrogen and heat generation)
    electricity_saving = final_energy_saving.reduce("id_final_energy_carrier", [1])
    del electricity_saving["id_final_energy_carrier"]
    heat = heat_saving_final.reduce("id_primary_energy_carrier", [7])
    del heat["id_primary_energy_carrier"]
    h2 = h2_saving_final.reduce("id_primary_energy_carrier", [7])
    del h2["id_primary_energy_carrier"]
    electricity_total = electricity_saving + heat + h2
    # Then calculate primary energy savings for electricity
    electricity_coefficient = eurostat_primary_parameters.reduce("id_parameter", 21)
    electricity_conversion_efficiency = conversion_efficiency.reduce("id_final_energy_carrier", 1)
    electricity_conversion_efficiency._data_frame = electricity_conversion_efficiency._data_frame[common_years]
    electricity_saving_final = electricity_total * electricity_coefficient / electricity_conversion_efficiency

    return heat_saving_final + electricity_saving_final + h2_saving_final


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
