# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from copy import copy

import numpy as np
import pandas as pd

from micat.calculation import extrapolation
from micat.calculation.ecologic import fuel_split
from micat.calculation.economic import investment, population
from micat.calculation.social import dwelling
from micat.input.data_source import DataSource
from micat.table.table import Table
from micat.utils import api


def measure_specific_parameters_template(
    request,
    database,
    confidential_database,
):
    template_args = _template_args(request)
    return _get_measure_specific_data(
        template_args,
        database,
        confidential_database,
    )


# pylint:disable=too-many-locals
def _get_measure_specific_data(
    template_args,
    database,
    confidential_database,
):
    measure = template_args["measure"]
    population_of_municipality = population.population_of_municipality(measure)

    id_region = int(template_args["id_region"])
    results = {}
    context = {
        "id_region": id_region,
        "id_subsector": int(measure["subsector"]["id"]),
        "id_action_type": int(measure["action_type"]["id"]),
        "unit": measure["unit"],
        "population_of_municipality": population_of_municipality,
    }

    final_energy_saving_or_capacities = _final_energy_saving_or_capacities(measure, context)

    data_source = DataSource(
        database, id_region, confidential_database, global_parameters=template_args["global_parameters"]
    )
    df = data_source.mapping_table("mapping__subsector__sector")._data_frame

    id_sector = None
    is_renewable = int(template_args["id_subsector"]) >= 30
    if not is_renewable:
        id_sector = df.loc[df["id_subsector"] == int(template_args["id_subsector"])]["id_sector"].item()

    wuppertal_parameters = _wuppertal_parameters(
        context,
        final_energy_saving_or_capacities,
        data_source,
    )

    results["main"] = _get_main_data(
        context,
        final_energy_saving_or_capacities,
        wuppertal_parameters,
        data_source,
        is_renewable,
    )

    results["affectedFuels"] = _get_fuel_data(
        context,
        final_energy_saving_or_capacities,
        data_source,
        is_renewable,
    )

    if not is_renewable:
        results["fuelSwitch"] = _get_fuel_switch_data(final_energy_saving_or_capacities.years, id_sector, data_source)

    results["residential"] = _get_residential_data(
        context,
        final_energy_saving_or_capacities,
        wuppertal_parameters,
        data_source,
        is_renewable,
    )

    results["context"] = [
        {"id_region": "id_region", "0": context["id_region"]},
        {"id_region": "id_subsector", "0": context["id_subsector"]},
        {"id_region": "id_action_type", "0": context["id_action_type"]},
        {"id_region": "population", "0": context["population_of_municipality"]},
    ]
    return results


def _wuppertal_parameters(
    context,
    final_energy_saving_or_capacities,
    data_source,
):
    id_region = context["id_region"]
    wuppertal_parameters_raw = data_source.table("wuppertal_parameters", {"id_region": str(id_region)})

    years = final_energy_saving_or_capacities.years
    wuppertal_parameters = extrapolation.extrapolate(wuppertal_parameters_raw, years)
    return wuppertal_parameters


def _get_main_data(
    context,
    final_energy_saving_or_capacities,
    wuppertal_parameters,
    data_source,
    is_renewable=None,
):
    main_data = {
        "subsidy_rate": {
            "id_parameter": 35,
            "id_final_energy_carrier": None,
            "label": "Average subsidy rate",
            "unit": "%",
            "importance": "recommended",
            "constants": None,
        },
        "lifetime": {
            "id_parameter": 36,
            "id_final_energy_carrier": None,
            "label": "Average technology lifetime",
            "unit": "years",
            "importance": "optional",
            "constants": _lifetime(context, data_source),
        },
    }
    subsidy_rate = wuppertal_parameters.reduce("id_parameter", 35)
    main_data["subsidy_rate"] = main_data["subsidy_rate"] | subsidy_rate._series.to_dict()

    if is_renewable:
        id_subsector = final_energy_saving_or_capacities.unique_index_values("id_subsector")[0]
        id_action_type = final_energy_saving_or_capacities.unique_index_values("id_action_type")[0]
        main_data["capacity_factors"] = {
            "id_parameter": 64,
            "id_final_energy_carrier": None,
            "label": "Capacity factors",
            "unit": "",
            "importance": "mandatory",
            "constants": None,
        }
        capacity_factors = data_source.table(
            "fraunhofer_capacity_factors",
            {
                "id_region": str(context["id_region"]),
                "id_parameter": "64",
                "id_subsector": str(id_subsector),
                "id_action_type": str(id_action_type),
            },
        )
        # Interpolate capacity factors for missing years
        _capacity_factors = extrapolation.extrapolate(capacity_factors, final_energy_saving_or_capacities.years)
        main_data["capacity_factors"] = (
            main_data["capacity_factors"] | _capacity_factors._data_frame.to_dict(orient="records")[0]
        )

        main_data["capex"] = {
            "id_parameter": 68,
            "id_final_energy_carrier": None,
            "label": "Capital investments",
            "unit": "\u20ac",
            "importance": "mandatory",
            "constants": None,
        }
        capex = investment.calculate_capex(
            data_source,
            id_subsector,
            id_action_type,
            final_energy_saving_or_capacities,
        )
        capex = capex.droplevel("id_parameter")
        main_data["capex"] = main_data["capex"] | capex._data_frame.to_dict(orient="records")[0]
        main_data["opex"] = {
            "id_parameter": 69,
            "id_final_energy_carrier": None,
            "label": "Running costs",
            "unit": "\u20ac",
            "importance": "mandatory",
            "constants": None,
        }
        opex = investment.calculate_opex(
            data_source,
            id_subsector,
            id_action_type,
            final_energy_saving_or_capacities,
        )
        opex = opex.droplevel("id_parameter")
        main_data["opex"] = main_data["opex"] | opex._data_frame.to_dict(orient="records")[0]
        main_data["vopex"] = {
            "id_parameter": 70,
            "id_final_energy_carrier": None,
            "label": "Variable running costs",
            "unit": "\u20ac",
            "importance": "mandatory",
            "constants": None,
        }
        vopex = investment.calculate_vopex(
            data_source,
            id_subsector,
            id_action_type,
            context["id_region"],
            final_energy_saving_or_capacities,
        )
        vopex = vopex.droplevel("id_parameter")
        main_data["vopex"] = main_data["vopex"] | vopex._data_frame.to_dict(orient="records")[0]
    else:
        main_data["energy_savings"] = {
            "id_parameter": None,
            "id_final_energy_carrier": None,
            "label": "Energy savings",
            "unit": context["unit"]["symbol"],
            "importance": "mandatory",
            "constants": None,
        }
        main_data["investment_costs"] = {
            "id_parameter": 40,
            "id_final_energy_carrier": None,
            "label": "Investment costs",
            "unit": "Mio. \u20ac",
            "importance": "mandatory",
            "constants": None,
        }

        main_data["energy_savings"] = (
            main_data["energy_savings"] | final_energy_saving_or_capacities._data_frame.to_dict(orient="records")[0]
        )

        investment_cost = investment.investment_cost_in_euro(
            final_energy_saving_or_capacities,
            data_source,
            id_region=context["id_region"],
        )

        # Convert to million euros to display the advanced parameter investment cost in mio. €
        investment_cost._data_frame = (
            investment_cost._data_frame.select_dtypes(exclude=["object", "datetime"]) / 1_000_000
        )
        main_data["investment_costs"] = (
            main_data["investment_costs"] | investment_cost._data_frame.to_dict(orient="records")[0]
        )
    return list(main_data.values())


def _get_fuel_data(
    context,
    final_energy_saving_or_capacities,
    data_source,
    is_renewable=None,
):
    id_region = context["id_region"]
    id_subsector = context["id_subsector"]
    subsector_ids = [id_subsector]

    if is_renewable:
        id_subsector = final_energy_saving_or_capacities.unique_index_values("id_subsector")[0]
        id_action_type = final_energy_saving_or_capacities.unique_index_values("id_action_type")[0]
        data = {
            1: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 1,
                "label": "Oil",
                "unit": "%",
                "importance": "recommended",
            },
            2: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 2,
                "label": "Coal",
                "unit": "%",
                "importance": "recommended",
            },
            3: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 3,
                "label": "Gas",
                "unit": "%",
                "importance": "recommended",
            },
            4: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 4,
                "label": "Biomass and renewable waste",
                "unit": "%",
                "importance": "recommended",
            },
            5: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 5,
                "label": "Renewables",
                "unit": "%",
                "importance": "recommended",
            },
            6: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 6,
                "label": "Other",
                "unit": "%",
                "importance": "recommended",
            },
            7: {
                "id_parameter": 67,
                "id_primary_energy_carrier": 7,
                "label": "Electricity",
                "unit": "%",
                "importance": "recommended",
            },
        }
        if id_action_type == 37:
            factors = data_source.table(
                "eurostat_primary_parameters",
                {
                    "id_region": str(context["id_region"]),
                    "id_parameter": "20",
                },
            )
            del factors["id_parameter"]
            factors = extrapolation.extrapolate(factors, final_energy_saving_or_capacities.years)
            for index, values in factors._data_frame.to_dict(orient="index").items():
                data[index] = data[index] | values
        else:
            factors = data_source.table(
                "fraunhofer_substitution_factors",
                {
                    "id_region": str(context["id_region"]),
                    "id_subsector": str(id_subsector),
                    "id_action_type": str(id_action_type),
                },
            )
            del factors["id_parameter"]
            factors = extrapolation.extrapolate(factors, final_energy_saving_or_capacities.years)
            for index, values in factors._data_frame.to_dict(orient="index").items():
                data[index[2]] = data[index[2]] | values
    else:
        data = {
            1: {
                "id_parameter": 16,
                "id_final_energy_carrier": 1,
                "label": "Share of electricity among affected",
                "unit": "%",
                "importance": "recommended",
            },
            2: {
                "id_parameter": 16,
                "id_final_energy_carrier": 2,
                "label": "Share of oil among affected",
                "unit": "%",
                "importance": "recommended",
            },
            3: {
                "id_parameter": 16,
                "id_final_energy_carrier": 3,
                "label": "Share of coal among affected",
                "unit": "%",
                "importance": "recommended",
            },
            4: {
                "id_parameter": 16,
                "id_final_energy_carrier": 4,
                "label": "Share of gas among affected",
                "unit": "%",
                "importance": "recommended",
            },
            5: {
                "id_parameter": 16,
                "id_final_energy_carrier": 5,
                "label": "Share of biomass and waste among affected",
                "unit": "%",
                "importance": "recommended",
            },
            6: {
                "id_parameter": 16,
                "id_final_energy_carrier": 6,
                "label": "Share of heat among affected",
                "unit": "%",
                "importance": "recommended",
            },
            7: {
                "id_parameter": 16,
                "id_final_energy_carrier": 7,
                "label": "Share of H2 and e-fuels among affected",
                "unit": "%",
                "importance": "recommended",
            },
        }
        share_affected = fuel_split.fuel_split_by_action_type(
            final_energy_saving_or_capacities,
            data_source,
            id_region,
            subsector_ids,
            round=True,
        )

        for index, values in share_affected._data_frame.to_dict(orient="index").items():
            data[index[2]] = data[index[2]] | values

    return list(data.values())


def _get_fuel_switch_data(years, id_sector, data_source):
    table = data_source.table("measurement_specific_parameters_fuel_switch", {"id_sector": str(id_sector)})
    # Extract the columns with year numbers
    annual_df = table._data_frame.filter(regex="[1-3][0-9]{3}")
    annual_df.apply(pd.to_numeric)
    raw_annual_table = Table(annual_df)
    if raw_annual_table.contains_non_nan():
        annual_table = extrapolation.extrapolate(raw_annual_table, years)
    else:
        annual_table = _extrapolated_nan_table(raw_annual_table, years)
    # Remove annual from the original table
    table._data_frame = table._data_frame.drop(columns=annual_df.columns)
    # Add the interpolated annual data to the table
    table._data_frame = pd.concat([table._data_frame, annual_table._data_frame], axis=1)
    return table._data_frame.reset_index().to_dict(orient="records")


def _get_residential_data(
    context,
    final_energy_saving_or_capacities,
    wuppertal_parameters,
    data_source,
    is_renewable=None,
):
    data = {
        "number_of_affected_dwellings": {
            "id_parameter": 45,
            "label": "Number of affected dwellings",
            "unit": "absolute",
            "importance": "recommended",
        },
        "annual_renovation_rate": {
            "id_parameter": 43,
            "label": "Annual renovation rate",
            "unit": "%",
            "importance": "alternative to 1",
        },
        "energy_poverty_target": {
            "id_parameter": 42,
            "label": "Energy poverty target",
            "unit": "%",
            "importance": "optional",
        },
        "total_dwelling_stock": {
            "id_parameter": 32,
            "label": "Total dwelling stock",
            "unit": "absolute",
            "importance": "optional",
        },
    }
    id_region = context["id_region"]
    population_of_municipality = context["population_of_municipality"]

    number_of_affected_dwellings = dwelling.number_of_affected_dwellings(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        population_of_municipality,
    )
    data["number_of_affected_dwellings"] = (
        data["number_of_affected_dwellings"] | number_of_affected_dwellings._data_frame.to_dict(orient="records")[0]
    )

    # TODO: Annual renovation rate is not available yet
    data["annual_renovation_rate"] = data["annual_renovation_rate"] | {
        str(y): 0 for y in final_energy_saving_or_capacities.years
    }
    energy_poverty_target = wuppertal_parameters.reduce("id_parameter", 25)
    data["energy_poverty_target"] = data["energy_poverty_target"] | energy_poverty_target._series.to_dict()

    id_region = context["id_region"]
    population_of_municipality = context["population_of_municipality"]
    dwelling_stock = dwelling.dwelling_stock(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        population_of_municipality,
    )
    data["total_dwelling_stock"] = (
        data["total_dwelling_stock"] | dwelling_stock._data_frame.to_dict(orient="records")[0]
    )

    if not is_renewable:
        data["average_hh_per_building"] = {
            "id_parameter": 31,
            "label": "Average number of households per building",
            "unit": "absolute",
            "importance": "optional",
        }
        data["average_rent"] = {
            "id_parameter": 29,
            "label": "Average rent of energy poor households",
            "unit": "\u20ac/year",
            "importance": "optional",
        }
        data["rent_premium"] = {
            "id_parameter": 34,
            "label": "Average renovation rent premium",
            "unit": "% of rent",
            "importance": "optional",
        }

        average_hh_per_building = wuppertal_parameters.reduce("id_parameter", 31)
        data["average_hh_per_building"] = data["average_hh_per_building"] | average_hh_per_building._series.to_dict()

        average_rent = wuppertal_parameters.reduce("id_parameter", 29)
        data["average_rent"] = data["average_rent"] | average_rent._series.to_dict()

        rent_premium = wuppertal_parameters.reduce("id_parameter", 34)
        data["rent_premium"] = data["rent_premium"] | rent_premium._series.to_dict()

    return list(data.values())


def _annual_columns(sheet):
    annual_columns = []
    for column in sheet.columns:
        header_cell = column[0]
        value = header_cell.value
        if isinstance(value, int):
            annual_columns.append(column)
    return annual_columns


def _cell_style(cell):
    # noinspection PyProtectedMember
    style = copy(cell._style)  # pylint: disable = protected-access
    return style


def _cell_value(cell):
    value = cell.value
    if value == "=NA()":
        return float("NaN")
    else:
        return value


def _columns_to_table(columns):
    data = {}
    for column in columns:
        column_values = [_cell_value(cell) for cell in column]
        header = column_values.pop(0)
        data[header] = column_values
    table = Table(data)
    return table


def _extrapolated_nan_table(raw_annual_table, years):
    number_of_rows = len(raw_annual_table)
    data = {}
    for year in years:
        values = np.empty(number_of_rows)
        values.fill(np.nan)
        data[str(year)] = values
    annual_table = Table(data)
    return annual_table


def _fill_annual_data(
    sheet,
    annual_table,
    cell_styles,
):
    column_offset = sheet.max_column + 1

    _, column_names, _ = annual_table.column_names
    column_index = column_offset
    header_style = cell_styles[0]
    for column_name in column_names:
        cell = sheet.cell(row=1, column=column_index)
        cell.value = column_name
        cell._style = header_style  # pylint: disable=protected-access
        column_index += 1

    for row_index, row in annual_table.iterrows():
        column_index = column_offset
        cell_style = cell_styles[row_index + 1]
        for value in row:
            cell = sheet.cell(row=row_index + 2, column=column_index)
            cell.value = round(value, 2)
            cell._style = cell_style  # pylint: disable=protected-access
            column_index += 1

    return sheet


def _fill_annual_series(
    sheet,
    start_column_index,
    row_index,
    series_or_table,
):
    if isinstance(series_or_table, Table):
        values = series_or_table.values[0]
    else:
        values = series_or_table.values
    column_index = start_column_index
    for value in values:
        cell = sheet.cell(column=column_index, row=row_index)
        cell.value = round(value, 2)
        column_index += 1


def _fill_table(
    sheet,
    start_column_index,
    start_row_index,
    table,
):
    row_index = start_row_index
    for _index, row in table.iterrows():
        column_index = start_column_index
        for value in row.values:
            cell = sheet.cell(column=column_index, row=row_index)
            cell.value = round(value, 2)
            column_index += 1
        row_index += 1


def _lifetime(context, database):
    id_subsector = context["id_subsector"]
    id_action_type = context["id_action_type"]
    wuppertal_sector_parameters = database.table(
        "wuppertal_sector_parameters", {"id_subsector": str(id_subsector), "id_action_type": str(id_action_type)}
    )
    lifetime = wuppertal_sector_parameters.reduce("id_parameter", 36)
    return lifetime


def _fill_unit(sheet, context):
    unit_object = context["unit"]
    unit = unit_object["symbol"]
    sheet["D2"] = unit
    return sheet


def _interpolate_annual_data(sheet, years):
    sheet_without_annual_data, raw_annual_table, cell_styles = _split_sheet(sheet)
    if raw_annual_table.contains_non_nan():
        annual_table = extrapolation.extrapolate(raw_annual_table, years)
    else:
        annual_table = _extrapolated_nan_table(raw_annual_table, years)
    sheet = _fill_annual_data(sheet_without_annual_data, annual_table, cell_styles)

    return sheet


def _final_energy_saving_or_capacities(measure, context):
    annual_data = {key: value for key, value in measure.items() if key.isdigit()}
    annual_data["id_measure"] = measure["id"]
    annual_data["id_subsector"] = context["id_subsector"]
    annual_data["id_action_type"] = context["id_action_type"]

    savings = Table([annual_data])
    return savings


def _split_sheet(sheet):
    annual_columns = _annual_columns(sheet)
    annual_table = _columns_to_table(annual_columns)

    first_column = annual_columns[0]
    cell_styles = list(map(_cell_style, first_column))

    first_column_index = annual_columns[0][0].column
    number_of_columns = len(annual_columns)
    sheet.delete_cols(first_column_index, number_of_columns)

    return sheet, annual_table, cell_styles


def _template_args(request):
    query_dict = api.parse_request(request)
    measure = query_dict["json"]
    args = {
        "measure": measure,
        "id_region": query_dict["id_region"],
        "id_subsector": query_dict["id_subsector"],
        "parameter_table_names": [
            "eurostat_final_parameters",
            "eurostat_final_sector_parameters",
            "eurostat_primary_parameters",
            "iiasa_final_subsector_parameters",
            "mixed_final_constant_parameters",
            "primes_parameters",
            "primes_primary_parameters",
        ],
        "global_parameters": measure.get("global_parameters"),
    }
    return args
