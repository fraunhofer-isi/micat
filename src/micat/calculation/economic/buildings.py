# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/299
from micat.table.table import Table


def added_asset_value_of_buildings(
    reduction_of_energy_cost,
    data_source,
    id_region,
    years,
):
    relevant_sector_ids = [
        3,  # tertiary
        4,  # residential
    ]

    relevant_action_type_ids = [
        1,  # Building envelope
        2,  # Heating fuel switch
        3,  # Energy-efficient heating
    ]

    # => relevant subsector ids:
    # 16 Average tertiary
    # 17 Average residential

    includes_relevant_action_types = _includes_relevant_action_types(reduction_of_energy_cost, relevant_action_type_ids)
    if includes_relevant_action_types:
        relevant_cost = reduction_of_energy_cost.reduce('id_action_type', relevant_action_type_ids)
    else:
        zero_result = _create_zero_result(
            reduction_of_energy_cost,
            relevant_sector_ids,
            years,
        )

        return zero_result

    sector_cost_in_euro = _sector_cost(
        data_source,
        relevant_cost,
        relevant_sector_ids,
        years,
    )

    capitalization_rate = _capitalization_rate(data_source, id_region)

    added_asset_value_in_euro = sector_cost_in_euro / capitalization_rate
    added_asset_value_in_mio_euro = added_asset_value_in_euro / 1000000

    return added_asset_value_in_mio_euro


def _sector_cost(data_source, relevant_cost, relevant_sector_ids, years):
    sectorial_cost_frame = _sectorial_cost_frame(relevant_cost, data_source)
    sectorial_cost = Table(sectorial_cost_frame)
    sectorial_cost = _include_default_entries(sectorial_cost, relevant_sector_ids, years)
    relevant_sectorial_cost = sectorial_cost.reduce('id_sector', relevant_sector_ids)
    sector_cost = relevant_sectorial_cost.aggregate_to(['id_measure', 'id_sector'])
    return sector_cost


def _capitalization_rate(data_source, id_region):
    cbre_parameters = data_source.table('cbre_parameters', {'id_region': str(id_region)})
    capitalization_rate = cbre_parameters.reduce('id_parameter', 46)
    return capitalization_rate


def _create_zero_result(
    table,
    relevant_sector_ids,
    years,
):
    existing_measure_ids = table.unique_index_values('id_measure')
    zero_rows = []
    for id_measure in existing_measure_ids:
        for id_sector in relevant_sector_ids:
            extra_entry = {
                'id_measure': id_measure,
                'id_sector': id_sector,
            }
            for year in years:
                extra_entry[str(year)] = 0
            extra_row_table = Table([extra_entry])
            zero_rows.append(extra_row_table)
    zero_result = Table.concat(zero_rows)
    return zero_result


def _include_default_entries(sectorial_cost, relevant_sector_ids, years):
    # ensures that there are zero entries for all relevant sector ids for
    # each measure, so that the grouped/aggregated table will never be empty
    # but contain zero rows.
    existing_measure_ids = sectorial_cost.unique_index_values('id_measure')
    extra_zero_rows = []
    for id_measure in existing_measure_ids:
        measure_cost = sectorial_cost.reduce('id_measure', [id_measure])
        existing_sector_ids = measure_cost.unique_index_values('id_sector')
        for id_sector in relevant_sector_ids:
            if id_sector not in existing_sector_ids:
                extra_entry = {
                    'id_measure': id_measure,
                    'id_sector': id_sector,
                    'id_action_type': 1,
                    'id_final_energy_carrier': 1,
                }
                for year in years:
                    extra_entry[str(year)] = 0
                extra_row_table = Table([extra_entry])
                extra_zero_rows.append(extra_row_table)
    sectorial_cost = Table.concat([sectorial_cost, *extra_zero_rows])
    return sectorial_cost


def _includes_relevant_action_types(reduction_of_energy_cost, relevant_action_type_ids):
    existing_action_type_ids = reduction_of_energy_cost.unique_index_values('id_action_type')
    for id_action_type in relevant_action_type_ids:
        if id_action_type in existing_action_type_ids:
            return True

    return False


def _sectorial_cost_frame(relevant_cost, data_source):
    mapping_subsector_sector = data_source.mapping_table('mapping__subsector__sector')
    sectorial_cost_frame = mapping_subsector_sector.apply_for(relevant_cost)
    sectorial_cost_frame.set_index(
        [
            'id_measure',
            'id_sector',
            'id_action_type',
            'id_final_energy_carrier',
        ],
        inplace=True,
    )
    return sectorial_cost_frame
