# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/42
import pandas as pd

from micat.calculation.ecologic import fuel_split
from micat.table.table import Table


def energy_saving(primary_energy_saving_by_action_type):
    aggregated_saving = _aggregate_primary_energy_saving(primary_energy_saving_by_action_type)
    return aggregated_saving


def efficiency_res_by_action_type(final_energy_saving_or_capacities, data_source):
    efficiency_res = data_source.table(
        "fraunhofer_efficiency_res",
        {
            "id_parameter": "66",  # RES energy allocation
        },
    )
    efficiency_res_df = efficiency_res._data_frame
    capacities = final_energy_saving_or_capacities._data_frame
    results = []

    # Iterate through each measure in your first DataFrame
    for (id_measure, id_subsector, id_action_type), values in capacities.iterrows():
        # Filter efficiency_res for matching subsector & action_type
        subset = efficiency_res_df[
            (efficiency_res_df.index.get_level_values("id_subsector") == id_subsector)
            & (efficiency_res_df.index.get_level_values("id_action_type") == id_action_type)
        ]

        # Multiply efficiencies by energy savings (broadcasted)
        multiplied = subset.values * values.values  # shape broadcasting
        multiplied_df = pd.DataFrame(multiplied, index=subset.index, columns=capacities.columns)

        # Add measure ID info to the MultiIndex
        multiplied_df["id_measure"] = id_measure
        multiplied_df = multiplied_df.set_index(["id_measure"], append=True)
        # Drop the 'id_parameter' level from the index
        multiplied_df = multiplied_df.droplevel("id_parameter")

        # Reorder the index levels to have 'id_measure' first
        multiplied_df = multiplied_df.reorder_levels(
            ["id_measure", "id_subsector", "id_action_type", "id_final_energy_carrier"]
        )
        multiplied_df = multiplied_df.sort_index()

        results.append(multiplied_df)

    # Concatenate all results
    saving_by_final_energy_carrier = pd.concat(results)
    return Table(saving_by_final_energy_carrier)


# pylint: disable=duplicate-code
def energy_saving_by_final_energy_carrier(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
    subsector_ids,
):
    if subsector_ids[0] >= 30:
        # For renewables, use efficiency_res table
        return efficiency_res_by_action_type(final_energy_saving_or_capacities, data_source)

    fuel_split_by_action_type = fuel_split.fuel_split_by_action_type(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        subsector_ids,
    )

    return _final_energy_saving_or_capacities_and_energy_carrier(
        fuel_split_by_action_type,
        final_energy_saving_or_capacities,
    )


def _final_energy_saving_or_capacities_and_energy_carrier(
    fuel_split_by_action_type,
    final_energy_saving_or_capacities,
):
    final_energy_saving_by_energy_carrier = final_energy_saving_or_capacities * fuel_split_by_action_type
    return final_energy_saving_by_energy_carrier


def _aggregate_primary_energy_saving(primary_energy_saving_by_action_type):
    aggregated_saving = primary_energy_saving_by_action_type.aggregate_to(["id_measure", "id_primary_energy_carrier"])
    return aggregated_saving
