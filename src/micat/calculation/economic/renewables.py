# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/31
from micat.calculation import extrapolation
from micat.table.table import Table
from micat.utils import list as list_utils


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


def vre_energy_system_costs(
    energy_produced,
    data_source,
    id_region,
):
    energy_system_cost = data_source.table(
        "wuppertal_energy_system_cost",
        {
            "id_parameter": str(76),
            "id_region": str(id_region),
        },
    )
    extrapolated_energy_system_cost = extrapolation.extrapolate(
        energy_system_cost,
        list_utils.string_to_integer(energy_produced.columns),
    )
    df1 = energy_produced._data_frame
    df2 = extrapolated_energy_system_cost._data_frame
    result = df1.mul(df2.iloc[0], axis=1)
    result = result.droplevel(["id_subsector", "id_action_type"])
    return Table(result)
