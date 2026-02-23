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
    # 1) Align indices
    # ------------------------------------------------------------

    df1_aligned = df1.reorder_levels(
        ["id_subsector", "id_action_type", "id_measure"]
    ).sort_index()

    intensity = df2["value"].sort_index()

    # ------------------------------------------------------------
    # 2) Multiply while keeping CRM dimension
    # ------------------------------------------------------------

    result = df1_aligned.mul(intensity, axis=0)

    # ------------------------------------------------------------
    # 3) Remove id_subsector from index
    # ------------------------------------------------------------

    result = (
        result.groupby(
            level=[
                "id_measure",
                "id_crm",
            ]
        )
        .sum()
        .sort_index()
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
