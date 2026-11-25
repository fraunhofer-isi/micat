# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/24
from micat.calculation import extrapolation
from micat.table.table import Table, merge_tables


# pylint: disable=too-many-locals
def fuel_split_by_action_type(final_energy_saving_or_capacities, data_source, id_region, subsector_ids, round=False):
    raw_lambda = _raw_lambda(
        data_source,
        id_region,
        subsector_ids,
    )
    years = final_energy_saving_or_capacities.years
    basic_lambda = extrapolation.extrapolate(raw_lambda, years)

    fuel_switch_defaults = _load_fuel_switch_defaults(data_source, subsector_ids, years)

    measure_specific_lambda = data_source.measure_specific_calculation(
        final_energy_saving_or_capacities,
        _determine_lambda_for_measure,
        lambda id_measure, id_subsector, id_sector, id_action_type, savings: _provide_default_lambda(
            id_measure,
            id_subsector,
            id_sector,
            id_action_type,
            savings,
            basic_lambda,
            fuel_switch_defaults,
        ),
    )

    action_type_ids = final_energy_saving_or_capacities.unique_index_values("id_action_type")

    basic_chi = _basic_chi(
        data_source,
        id_region,
        subsector_ids,
        action_type_ids,
    )

    measure_specific_chi = data_source.measure_specific_calculation(
        final_energy_saving_or_capacities,
        lambda id_measure, id_subsector, _id_sector, id_action_type, savings, _first, _second, _third: _determine_chi_for_measure(
            id_measure,
            id_subsector,
            id_action_type,
            basic_chi,
        ),
        lambda id_measure, id_subsector, _id_sector, id_action_type, savings: _provide_default_chi(
            id_measure,
            id_subsector,
            id_action_type,
            savings,
            basic_chi,
        ),
    )
    fuel_split = _measure_specific_fuel_split(measure_specific_lambda, measure_specific_chi)

    if round:
        fuel_split = _round_values(fuel_split, years)
    return fuel_split


def _round_values(fuel_split, years):
    for _index, row in fuel_split.iterrows():
        for year in years:
            key = str(year)
            value = row[key]
            row[key] = round(value, 2)
    return fuel_split


def _basic_chi(
    data_source,
    id_region,
    subsector_ids,
    action_type_ids,
):
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": "12",  # Chi
        "id_subsector": subsector_ids,
        "id_action_type": action_type_ids,
    }
    table = data_source.table("mixed_final_constant_parameters", where_clause)
    chi = table.reduce("id_parameter", 12)
    return chi


def _determine_lambda_for_measure(
    _id_measure,
    id_subsector,
    _id_sector,
    id_action_type,
    energy_saving,
    extrapolated_final_parameters,
    _extrapolated_parameters,
    _constants,
):
    non_effected_action_type_ids = [
        2,  # Heating fuel switch
        10,  # Fuel switch
        17,  # Fuel switch
    ]
    if id_action_type in non_effected_action_type_ids:
        # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/264

        _lambda = _lambda_for_measure_with_non_effected_action_type(
            id_subsector,
            energy_saving,
            extrapolated_final_parameters,
        )
        return _lambda
    else:
        # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/279
        _lambda = _lambda_for_measure_with_effected_action_type(
            id_subsector,
            extrapolated_final_parameters,
        )
        return _lambda


def _determine_chi_for_measure(
    id_measure,
    id_subsector,
    id_action_type,
    basic_chi,
):
    # The corresponding lambda value will be derived from measure specific parameters
    # The chi value is 1. We just need to create it in a compatible tabular format,
    # for which we use the basic_chi data.
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/264

    query = "id_subsector==" + str(id_subsector) + " & id_action_type==" + str(id_action_type)
    chi = basic_chi.query(query)
    chi = chi.insert_index_column("id_measure", 0, id_measure)
    chi["value"] = 1
    return chi


def _energy_consumption(
    energy_saving,
    extrapolated_final_parameters,
    lambda_ante,
    lambda_post,
):
    eta_ante = _eta_ante(extrapolated_final_parameters, lambda_ante)
    eta_post = _eta_post(extrapolated_final_parameters, lambda_post)
    eta_factor = eta_ante / (eta_post - eta_ante)  # TO DO: handle case where eta_post == eta_ante
    energy_consumption = energy_saving * eta_factor
    return energy_consumption


def _energy_consumption_difference(
    energy_saving,
    energy_consumption,
    lambda_ante,
    lambda_post,
):
    fuel_mix_ante = lambda_ante * (energy_consumption + energy_saving)
    fuel_mix_post = lambda_post * energy_consumption
    energy_consumption_difference = fuel_mix_ante - fuel_mix_post
    return energy_consumption_difference


def _eta_ante(extrapolated_final_parameters, lambda_ante):
    eta_ante_input = extrapolated_final_parameters.reduce("id_parameter", 14)
    eta_times_lambda_ante = eta_ante_input * lambda_ante
    eta_ante = eta_times_lambda_ante.sum()
    return eta_ante


def _eta_post(extrapolated_final_parameters, lambda_post):
    eta_post_input = extrapolated_final_parameters.reduce("id_parameter", 15)
    eta_times_lambda_post = eta_post_input * lambda_post
    eta_post = eta_times_lambda_post.sum()
    return eta_post


def _lambda_for_measure_with_effected_action_type(
    id_subsector,
    extrapolated_final_parameters,
):
    lambda_ = extrapolated_final_parameters.reduce("id_parameter", 16)
    lambda_ = lambda_.insert_index_column("id_subsector", 1, id_subsector)
    return lambda_


def _lambda_for_measure_with_non_effected_action_type(
    id_subsector,
    energy_saving,
    extrapolated_final_parameters,
):
    lambda_ante_input = extrapolated_final_parameters.reduce("id_parameter", 17)
    lambda_ante = lambda_ante_input.normalize()

    lambda_post_input = extrapolated_final_parameters.reduce("id_parameter", 18)
    lambda_post = lambda_post_input.normalize()

    energy_consumption = _energy_consumption(
        energy_saving,
        extrapolated_final_parameters,
        lambda_ante,
        lambda_post,
    )

    energy_consumption_difference = _energy_consumption_difference(
        energy_saving,
        energy_consumption,
        lambda_ante,
        lambda_post,
    )

    lambda_ = energy_consumption_difference.normalize()
    lambda_ = lambda_.insert_index_column("id_subsector", 1, id_subsector)
    return lambda_


def _measure_specific_fuel_split(lambda_, chi):
    product = lambda_ * chi
    fuel_split = product.normalize(["id_measure", "id_subsector", "id_action_type"])
    return fuel_split


def _load_fuel_switch_defaults(data_source, subsector_ids, years):
    mapping_df = data_source.mapping_table("mapping__subsector__sector")._data_frame
    defaults_by_sector = {}

    for id_subsector in subsector_ids:
        rows = mapping_df.loc[mapping_df["id_subsector"] == id_subsector, "id_sector"]
        if rows.empty:
            continue
        id_sector = int(rows.item())
        if id_sector in defaults_by_sector:
            continue

        try:
            raw_table = data_source.table(
                "measurement_specific_parameters_fuel_switch",
                {"id_sector": str(id_sector)},
            )
        except Exception:
            continue

        if raw_table is None:
            continue

        df = raw_table._data_frame
        df = df.droplevel("id_sector")
        year_cols = [col for col in df.columns if str(col).isdigit()]
        df = df[year_cols]
        df.index = df.index.set_levels(
            [level.astype(int) for level in df.index.levels]
        )

        fuel_switch_table = Table(df)
        extrapolated = extrapolation.extrapolate(fuel_switch_table, years)
        defaults_by_sector[id_sector] = extrapolated

    return defaults_by_sector


def _provide_default_lambda(
    id_measure,
    id_subsector,
    id_sector,
    id_action_type,
    savings,
    basic_lambda,
    fuel_switch_defaults_by_sector,
):
    non_effected_action_type_ids = [2, 10, 17]
    if id_action_type in non_effected_action_type_ids and id_sector in fuel_switch_defaults_by_sector:
        default_final_params = fuel_switch_defaults_by_sector[id_sector]
        _lambda = _lambda_for_measure_with_non_effected_action_type(
            id_subsector,
            savings,
            default_final_params,
        )
        _lambda = _lambda.insert_index_column("id_measure", 0, id_measure)
        _lambda._data_frame = _lambda._data_frame.reorder_levels(
            ["id_measure", "id_subsector", "id_final_energy_carrier"]
        )
        return _lambda
    else:
        query = "id_subsector==" + str(id_subsector)
        _lambda = basic_lambda.query(query)
        _lambda = _lambda.insert_index_column("id_measure", 0, id_measure)
        return _lambda


def _provide_default_chi(
    id_measure,
    id_subsector,
    id_action_type,
    _savings,
    basic_chi,
):
    non_effected_action_type_ids = [2, 10, 17]
    query = "id_subsector==" + str(id_subsector) + "& id_action_type==" + str(id_action_type)
    chi = basic_chi.query(query)
    chi = chi.insert_index_column("id_measure", 0, id_measure)
    if id_action_type in non_effected_action_type_ids:
        chi["value"] = 1
    return chi


def _raw_lambda(
    data_source,
    id_region,
    subsector_ids,
):
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": "11",  # 11: Lambda
        "id_subsector": subsector_ids,
    }

    eurostat = data_source.table("eurostat_final_sector_parameters", where_clause)
    primes = data_source.table("primes_final_sector_parameters", where_clause)

    table = merge_tables(
        eurostat,
        primes,
    )
    lambda_ = table.reduce("id_parameter", 11)
    return lambda_
