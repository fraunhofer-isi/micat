# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def turnover_of_energy_efficiency_goods(
    final_energy_saving_or_capacities,
    data_source,
):
    years = final_energy_saving_or_capacities.years
    action_type_ids = final_energy_saving_or_capacities.unique_index_values("id_action_type")
    if action_type_ids[0] >= 30:
        # Return zero values for renewables
        turnover = final_energy_saving_or_capacities.copy()
        turnover._data_frame = turnover._data_frame * 0
    else:
        specific_turnover = _specific_turnover(data_source, action_type_ids, years)
        turnover = specific_turnover * final_energy_saving_or_capacities
    del turnover["id_subsector"]
    del turnover["id_action_type"]
    return turnover


def _specific_turnover(data_source, action_type_ids, years):
    irena_parameters = data_source.table("irena_parameters", {"id_action_type": action_type_ids})
    raw_specific_turnover = irena_parameters.reduce("id_parameter", [49])
    del raw_specific_turnover["id_parameter"]
    specific_turnover = extrapolation.extrapolate(raw_specific_turnover, years)
    return specific_turnover
