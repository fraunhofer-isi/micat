# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/31
from micat.table.table import Table


def material_demand(
    final_energy_saving_or_capacities,
    data_source,
):
    action_type_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_action_type"
    )
    subsector_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_subsector"
    )

    table_name = "wuppertal_material_intensity"
    where_clause = {
        "id_subsector": subsector_ids,
        "id_action_type": action_type_ids,
    }
    material_intensity = data_source.table(
        table_name,
        where_clause,
    )

    df1 = final_energy_saving_or_capacities._data_frame
    df2 = material_intensity._data_frame

    # ------------------------------------------------------------
    # 1) Bring both DataFrames to compatible index structure
    # ------------------------------------------------------------

    # df1 index: (id_measure, id_subsector, id_action_type)
    # -> move id_measure to last level so first two match df2
    df1_aligned = df1.reorder_levels(
        ["id_subsector", "id_action_type", "id_measure"]
    ).sort_index()

    # df2 index: (id_subsector, id_action_type, id_parameter, id_crm)
    # -> aggregate material intensity per (id_subsector, id_action_type)
    intensity = df2["value"].groupby(level=["id_subsector", "id_action_type"]).sum()

    # ------------------------------------------------------------
    # 2) Multiply (automatic alignment on shared index levels)
    # ------------------------------------------------------------

    result = (
        df1_aligned.mul(intensity, axis=0)  # broadcast over id_measure
        .groupby(level="id_measure")
        .sum()
    )

    return Table(result)


def supply_risk_factor(
    final_energy_saving_or_capacities,
    data_source,
):
    action_type_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_action_type"
    )
    subsector_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_subsector"
    )

    table_name = "wuppertal_supply_risk_factor"
    where_clause = {
        "id_subsector": subsector_ids,
        "id_action_type": action_type_ids,
    }
    supply_risk_factor = data_source.table(
        table_name,
        where_clause,
    )

    df = final_energy_saving_or_capacities._data_frame
    risk = supply_risk_factor._data_frame.droplevel("id_parameter")

    df_result = (
        df.join(risk, on=["id_subsector", "id_action_type"])
        .pipe(lambda d: d[df.columns].multiply(d["value"], axis=0))
        .groupby(level="id_measure")
        .sum()
    )

    return Table(df_result)
