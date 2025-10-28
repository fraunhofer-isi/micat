# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable = import-self
from urllib.parse import parse_qs

from micat.calculation import air_pollution, conversion, cost_benefit_analysis, extrapolation
from micat.calculation.conversion import convert_units_of_measure_specific_parameters
from micat.calculation.ecologic import calculation_ecologic, energy_saving
from micat.calculation.economic import (
    calculation_economic,
    energy_cost,
    eurostat,
    population,
)
from micat.calculation.social import calculation_social
from micat.input.data_source import DataSource
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table


def calculate_energy_produced(final_energy_saving_or_capacities, data_source, id_region):
    capacity_factors = data_source.table("fraunhofer_capacity_factors", {})
    # Interpolate capacity factors for missing years
    _capacity_factors = extrapolation.extrapolate(capacity_factors, final_energy_saving_or_capacities.years)

    # Multiply capacities with capacity factors
    df1 = final_energy_saving_or_capacities._data_frame.reset_index()
    df2 = _capacity_factors._data_frame.reset_index()
    df1_long = df1.melt(id_vars=["id_measure", "id_subsector", "id_action_type"], var_name="year", value_name="value")
    df2_long = df2.melt(
        id_vars=["id_parameter", "id_subsector", "id_action_type"], var_name="year", value_name="factor"
    )
    merged = df1_long.merge(df2_long, on=["id_subsector", "id_action_type", "year"], how="left")
    merged["result"] = (
        merged["value"] * merged["factor"] * (365 * 24 * 0.00008598)
    )  # (365d/yr⋅24h/d⋅0.00008598ktoe/MWh)
    energy_produced = merged.pivot_table(
        index=["id_measure", "id_subsector", "id_action_type"], columns="year", values="result", aggfunc="first"
    )

    final_energy_saving_or_capacities._data_frame = energy_produced.sort_index(axis=1)  # Jahre sortieren
    return final_energy_saving_or_capacities


# pylint: disable=too-many-locals
def calculate_indicator_data(
    http_request,
    database,
    confidential_database,
):
    print("Calculating indicator data for request")

    # The arguments include:
    # id_region,
    # final_energy_saving_or_capacities (dataframe including id_measure, id_subsector, id_action_type as index)
    # measure_specific_parameters (dictionary using id_measure as key)
    # parameters ( maps parameter_name => dataframe )
    # population_of_municipality (as int)
    arguments = _front_end_arguments(http_request)

    id_region = arguments["id_region"]

    # maps from id_measure to {'parameters': [...], 'finalParameters': [...], 'constants': [...]}
    measure_specific_parameters = arguments["measure_specific_parameters"]
    measure_specific_parameters = convert_units_of_measure_specific_parameters(measure_specific_parameters)

    parameters = arguments["parameters"]
    population_of_municipality = arguments["population_of_municipality"]

    data_source = DataSource(
        database,
        id_region,
        confidential_database,
        measure_specific_parameters,
        parameters,
    )

    final_energy_saving_or_capacities = arguments["final_energy_saving_or_capacities"]
    years = final_energy_saving_or_capacities.years

    # Check if subsectors belong to renewables (id >= 30) and calculate energy produced
    if any(
        id_subsector >= 30 for id_subsector in final_energy_saving_or_capacities.unique_index_values("id_subsector")
    ):
        final_energy_saving_or_capacities = calculate_energy_produced(
            final_energy_saving_or_capacities,
            data_source,
            id_region,
        )

    interim_data, heat_saving_final, electricity_saving_final = _interim_data(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        years,
    )

    _validate_data(interim_data)

    social_indicators = calculation_social.social_indicators(
        final_energy_saving_or_capacities,
        population_of_municipality,
        interim_data,
        data_source,
        id_region,
        heat_saving_final,
        electricity_saving_final,
    )
    _validate_data(social_indicators)

    ecologic_indicators = calculation_ecologic.ecologic_indicators(
        interim_data,
        data_source,
        id_region,
        heat_saving_final,
        electricity_saving_final,
    )
    _validate_data(ecologic_indicators)

    economic_indicators = calculation_economic.economic_indicators(
        final_energy_saving_or_capacities,
        population_of_municipality,
        interim_data,
        ecologic_indicators,
        data_source,
        id_region,
        years,
    )
    _validate_data(economic_indicators)

    cost_benefit_analysis_parameters = cost_benefit_analysis.parameters(
        final_energy_saving_or_capacities,
        id_region,
        data_source,
    )
    result_tables = social_indicators | economic_indicators | ecologic_indicators | cost_benefit_analysis_parameters
    translated_result_tables = _translate_result_tables(result_tables, data_source)
    json_result = _convert_result_tables_to_json(translated_result_tables)

    return json_result

    # mapping of indicators to indicator groups:
    # (helps to find indicators in corresponding calculation modules)
    # 1  Energy poverty             1 Social
    # 2  Inequality                 1 Social
    # 3  Workforce performance      1 Social
    # 4  Human health I             1 Social
    # 5  Human health II            1 Social
    # 6  Working days lost          1 Social
    #
    # 7  GDP                        2 Economic
    # 8  Employment                 2 Economic
    # 9  Public budgets             2 Economic
    # 10 Energy prices              2 Economic
    # 11 ETS prices                 2 Economic
    # 12 Terms of trade             2 Economic
    # 13 Energy intensity           2 Economic
    # 14 Industrial productivity    2 Economic
    # 15 Asset value                2 Economic
    # 16 Investments                2 Economic
    # 17 Turnover of EE goods       2 Economic
    # 18 Competitiveness            2 Economic
    # 19 Innovation                 2 Economic
    # 20 Import dependency          2 Economic
    # 21 Supplier diversity         2 Economic
    # 22 Renewables integration     2 Economic
    #
    # 23 Avoided capacity expansion 3 Ecologic
    # 24 Energy savings             3 Ecologic
    # 25 Material resources         3 Ecologic
    # 26 RES targets                3 Ecologic
    # 27 GHG savings                3 Ecologic
    # 28 Air pollutants             3 Ecologic


def _add_renewables_and_other(energy_saving_by_primary_energy_carrier):
    table = energy_saving_by_primary_energy_carrier

    id_column_names, _year_column_names, _ = table.column_names
    index_column_names = id_column_names[0:-1]

    index_entries = table.unique_multi_index_tuples(index_column_names)
    columns = table.columns
    for index_entry in index_entries:
        id_measure = index_entry[0]
        id_subsector = index_entry[1]
        id_action_type = index_entry[2]

        extra_nuclear_table = _extra_nuclear_table(
            id_measure,
            id_subsector,
            id_action_type,
            columns,
        )
        table = Table.concat([table, extra_nuclear_table])
    sorted_table = table.sort()
    return sorted_table


def _extra_nuclear_table(
    id_measure,
    id_subsector,
    id_action_type,
    columns,
):
    id_primary_energy_carrier_electricity = 1
    id_primary_energy_carrier_renewables = 5
    id_primary_energy_carrier_other = 6

    base_entry = {
        "id_measure": id_measure,
        "id_subsector": id_subsector,
        "id_action_type": id_action_type,
    }
    for year in columns:
        base_entry[year] = 0
    electricity_entry = base_entry.copy()
    electricity_entry["id_primary_energy_carrier"] = id_primary_energy_carrier_electricity
    renewables_entry = base_entry.copy()
    renewables_entry["id_primary_energy_carrier"] = id_primary_energy_carrier_renewables
    other_entry = base_entry.copy()
    other_entry["id_primary_energy_carrier"] = id_primary_energy_carrier_other
    extra_nuclear_table = Table([electricity_entry, renewables_entry, other_entry])
    return extra_nuclear_table


def _additional_primary_energy_saving(
    energy_saving_by_final_energy_carrier,
    data_source,
):
    mapping = _mapping_from_final_to_primary_energy_carrier(data_source)
    energy_saving_by_primary_energy_carrier = energy_saving_by_final_energy_carrier.map_id_column(
        mapping,
    )
    # The primary energy carriers 5 & 6 (renewables, other) have no corresponding
    # source id_final_energy_carrier to be mapped from.
    # Therefore, the corresponding entries are included in an extra step:
    additional_primary_energy_saving = _add_renewables_and_other(energy_saving_by_primary_energy_carrier)
    return additional_primary_energy_saving


def _check_request_parameters(query_parameters):
    if "id_region" not in query_parameters.keys():
        raise AttributeError('Query parameters must include "id_region"')

    id_region = query_parameters["id_region"]

    if (id_region is None) or (id_region == "undefined"):
        raise AttributeError('Query parameters must include "id_region"')

    if "savings" not in query_parameters.keys():
        raise AttributeError('Query parameters must include "savings"')

    savings = query_parameters["savings"]

    if (savings is None) or (savings == "undefined"):
        raise AttributeError('Query parameters must include "savings"')


def _convert_result_tables_to_json(result_tables):
    result_json = {key: table.to_custom_json() for key, table in result_tables.items()}
    return result_json


def _extract_details_from_measures(measures):
    details = {}
    measures_without_detail = []
    for measure in measures:
        id_measure = measure["id_measure"]
        detail = measure["details"]
        if detail != {}:
            details[id_measure] = detail
        del measure["details"]
        measures_without_detail.append(measure)
    return details, measures_without_detail


def _front_end_arguments(http_request):
    query_parameters = _parse_request(http_request)
    _check_request_parameters(query_parameters)
    id_region = int(query_parameters["id_region"])
    measures = query_parameters["savings"]
    measure_specific_parameters, measures = _extract_details_from_measures(measures)
    final_energy_saving_or_capacities = Table(measures)

    json = query_parameters["json"]
    parameters = json.get("parameters", {})
    population_of_municipality = population.population_of_municipality(json)

    return {
        "id_region": id_region,
        "final_energy_saving_or_capacities": final_energy_saving_or_capacities,
        "population_of_municipality": population_of_municipality,
        "parameters": parameters,
        "measure_specific_parameters": measure_specific_parameters,
    }


# pylint: disable=duplicate-code
def _interim_data(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
    years,
):
    subsector_ids = final_energy_saving_or_capacities.unique_index_values("id_subsector")

    eurostat_primary_parameters = eurostat.primary_parameters(data_source, id_region, years)

    energy_saving_by_final_energy_carrier = energy_saving.energy_saving_by_final_energy_carrier(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        subsector_ids,
    )
    # Interpolate missing years in h2_coefficient table
    h2_coefficient = data_source.table("fraunhofer_hydrogen_synthetic_fuels_generation", {})
    h2_coefficient._data_frame.columns = h2_coefficient._data_frame.columns.astype(int)
    all_years = range(h2_coefficient._data_frame.columns.min(), h2_coefficient._data_frame.columns.max() + 1)
    h2_coefficient._data_frame = h2_coefficient._data_frame.reindex(columns=all_years).interpolate(axis=1)
    h2_coefficient._data_frame.columns = h2_coefficient._data_frame.columns.astype(str)

    # Clean up and interpolate conversion efficiency table
    conversion_efficiency = data_source.table("fraunhofer_conversion_efficiency", {})
    del conversion_efficiency["id_parameter"]
    conversion_efficiency._data_frame.columns = conversion_efficiency._data_frame.columns.astype(int)
    all_years = range(
        conversion_efficiency._data_frame.columns.min(), conversion_efficiency._data_frame.columns.max() + 1
    )
    conversion_efficiency._data_frame = conversion_efficiency._data_frame.reindex(columns=all_years).interpolate(axis=1)
    conversion_efficiency._data_frame.columns = conversion_efficiency._data_frame.columns.astype(str)

    # Substitution factors
    if subsector_ids[0] >= 30:
        substitution_factors = data_source.table("fraunhofer_substitution_factors", {})
        del substitution_factors["id_parameter"]
        substitution_factors = extrapolation.extrapolate(substitution_factors, final_energy_saving_or_capacities.years)
        # Filter for id_region
        substitution_factors = substitution_factors.reduce("id_region", id_region)
        # Filter for id_subsector
        substitution_factors = substitution_factors.reduce("id_subsector", subsector_ids)
        # Filter for id_action_type
        action_type_ids = final_energy_saving_or_capacities.unique_index_values("id_action_type")
        substitution_factors = substitution_factors.reduce("id_action_type", action_type_ids)
    else:
        substitution_factors = None

    heat_saving_final, electricity_saving_final, h2_saving_final = conversion.primary_energy_saving(
        energy_saving_by_final_energy_carrier,
        eurostat_primary_parameters,
        h2_coefficient,
        conversion_efficiency,
        substitution_factors,
    )
    conventional_primary_energy_saving = heat_saving_final + electricity_saving_final + h2_saving_final

    additional_primary_energy_saving = _additional_primary_energy_saving(
        energy_saving_by_final_energy_carrier,
        data_source,
    )

    total_primary_energy_saving = conversion.total_primary_energy_saving(
        conventional_primary_energy_saving,
        additional_primary_energy_saving,
    )

    if subsector_ids[0] >= 30:
        # Mock iiasa_final_subsector_parameters for renewables to avoid errors in social and ecologic calculations
        iiasa_final_subsector_parameters = data_source.table(
            "iiasa_final_subsector_parameters",
            {
                "id_region": str(id_region),
                "id_subsector": [1],
            },
        )
        iiasa_final_subsector_parameters._data_frame[:] = 0
        iiasa_final_subsector_parameters._data_frame = iiasa_final_subsector_parameters._data_frame.rename(
            index=lambda x: subsector_ids[0], level="id_subsector"
        )
    else:
        iiasa_final_subsector_parameters = data_source.table(
            "iiasa_final_subsector_parameters",
            {
                "id_region": str(id_region),
                "id_subsector": subsector_ids,
            },
        )
    iiasa_final_subsector_parameters_generation = data_source.table(
        "iiasa_final_subsector_parameters_generation",
        {
            "id_region": str(id_region),
        },
    )

    reduction_of_energy_cost = energy_cost.reduction_of_energy_cost(
        energy_saving_by_final_energy_carrier,
        data_source,
        id_region,
    )

    results = {
        "additional_primary_energy_saving": additional_primary_energy_saving,
        "energy_saving_by_final_energy_carrier": energy_saving_by_final_energy_carrier,
        "eurostat_primary_parameters": eurostat_primary_parameters,
        "total_primary_energy_saving": total_primary_energy_saving,
        "iiasa_final_subsector_parameters": iiasa_final_subsector_parameters,
        "iiasa_final_subsector_parameters_generation": iiasa_final_subsector_parameters_generation,
        "reduction_of_energy_cost": reduction_of_energy_cost,
    }

    return results, heat_saving_final, electricity_saving_final


def _mapping_from_final_to_primary_energy_carrier(database):
    mapping_table = database.mapping_table("mapping__final_energy_carrier__primary_energy_carrier")
    return mapping_table


def _mocked_h2():
    coefficient_h2 = Table(
        [
            {"id_primary_energy_carrier": 1, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 2, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 3, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 4, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 5, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 6, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 7, "2020": 1.5, "2025": 1.5, "2030": 1.5},
            {"id_primary_energy_carrier": 8, "2020": 1.5, "2025": 1.5, "2030": 1.5},
        ]
    )
    return coefficient_h2


def _parse_request(http_request):
    query_string = http_request.query_string
    query_parameters = dict(parse_qs(query_string.decode()))
    query_dict = {k: v[0] for k, v in query_parameters.items()}
    if http_request.content_type == "application/json":
        query_dict["json"] = http_request.json
        if "measures" in http_request.json:
            query_dict["savings"] = [measure["savings"] for measure in http_request.json["measures"]]
        else:
            raise AttributeError("Query must include the measures in the JSON body")
    else:
        raise AttributeError("Unknown content type:" + http_request.content_type)
    return query_dict


def _translate_id_if_exists(table, id_name, data_source):
    id_column_names, _year_column_names, _ = table.column_names
    if id_name not in id_column_names:
        return table

    id_table = data_source.id_table(id_name)
    column_name = id_name[3:]
    translated_table = table.join_id_column(
        id_table,
        column_name,
    )
    index_column_names = id_column_names.copy()
    index_to_replace = id_column_names.index(id_name)
    index_column_names[index_to_replace] = column_name

    translated_table.set_index(index_column_names)
    return translated_table


def _translate_result(key, table, data_source):
    if isinstance(table, AnnualSeries):
        message = 'Argument for key "' + key + '" is an AnnualSeries. Please pass a table instead.'
        raise ValueError(message)
    translated_table = _translate_id_if_exists(table, "id_parameter", data_source)
    translated_table = _translate_id_if_exists(translated_table, "id_sector", data_source)
    translated_table = _translate_id_if_exists(translated_table, "id_final_energy_carrier", data_source)
    translated_table = _translate_id_if_exists(translated_table, "id_primary_energy_carrier", data_source)
    translated_table = _translate_id_if_exists(translated_table, "id_technology", data_source)
    _validate_remaining_index_column_names(translated_table)

    return translated_table


def _translate_result_tables(result_tables, data_source):
    translated_results = {key: _translate_result(key, table, data_source) for key, table in result_tables.items()}
    return translated_results


def _validate_data(tables):
    for table_name, table in tables.items():
        if not isinstance(table, Table):
            continue
        if table.contains_nan():
            message = "Table " + table_name + " contains NaN values!"
            raise ValueError(message)

        if table.contains_inf():
            message = "Table " + table_name + " contains infinite values!"
            raise ValueError(message)


def _validate_remaining_index_column_names(table):
    id_column_names, _year_column_names, _ = table.column_names
    for column_name in id_column_names:
        if column_name == "id_measure":
            continue
        if column_name.startswith("id_"):
            message = (
                'Translated table must not include index column "'
                + column_name
                + '". '
                + "Please translate or remove the column."
            )
            raise KeyError(message)
