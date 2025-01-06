# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=unused-variable
# pylint: disable=duplicate-code
import io

import pandas as pd

from micat.calculation import mode
from micat.table import table
from micat.template import constants, database_utils, validators, xlsx_utils
from micat.utils import api


def parameters_template(request, database, confidential_database=None):
    template_args = _template_args(request)
    template_bytes = _parameters_template(template_args, database, confidential_database)
    return template_bytes


def _template_args(request):
    query = api.parse_request(request)
    id_mode = int(query["id_mode"])
    id_region = int(query["id_region"])
    args = {
        "coefficient_sheets": [
            "FuelSplitCoefficient",
            "EnergyPrice",
            "ElectricityGeneration",
            "HeatGeneration",
            "MonetisationFactors",
        ],
        "id_mode": id_mode,
        "id_region": id_region,
        "sheet_password": "micat",
        "options_sheet_name": "Options",
    }
    if request.args.getlist("years"):
        args["years"] = request.args.getlist("years")
    return args


def _parameters_template(template_args, database, confidential_database=None):
    id_subsector_table = database.id_table("id_subsector")
    id_final_energy_carrier_table = database.id_table("id_final_energy_carrier")
    id_primary_energy_carrier_table = database.id_table("id_primary_energy_carrier")

    # If there is no year below or equal to 2020, add a dummy value; otherwise a table cannot be created
    if not any([y for y in template_args["years"] if int(y) <= 2020]):
        template_args["years"].append("2020")
        template_args["ignore_years"] = ["2020"]

    template_bytes = io.BytesIO()
    workbook = xlsx_utils.empty_workbook(template_bytes)

    for sheet_name in template_args["coefficient_sheets"]:
        if sheet_name in ("FuelSplitCoefficient", "EnergyPrice"):
            _subsector_final_create_parameter_sheet(
                workbook,
                sheet_name,
                template_args,
                database if mode.is_eurostat_mode(template_args["id_mode"]) else confidential_database,
                id_subsector_table,
                id_final_energy_carrier_table,
            )

        elif sheet_name in ("ElectricityGeneration", "HeatGeneration"):
            _primary_create_parameter_sheet(
                workbook,
                sheet_name,
                template_args,
                database if mode.is_eurostat_mode(template_args["id_mode"]) else confidential_database,
                id_primary_energy_carrier_table,
            )
        elif sheet_name in ["MonetisationFactors"]:
            _monetization_create_parameter_sheet(
                workbook,
                sheet_name,
                template_args,
                database,
            )

    _create_options_sheet(
        workbook,
        template_args,
        id_subsector_table,
        id_final_energy_carrier_table,
        id_primary_energy_carrier_table,
    )
    workbook.close()
    return template_bytes


def _monetization_create_parameter_sheet(
    workbook,
    sheet_name,
    template_args,
    database,
):
    id_mode = template_args["id_mode"]
    id_region = template_args["id_region"]

    sheet = workbook.add_worksheet(sheet_name)
    sheet = _add_parameters_header(sheet, workbook, ["id_parameter", "Parameter", "Value"])
    sheet = _monetization_add_parameters_data_validation(
        sheet,
        id_mode,
    )

    monetization_parameter_table = _monetization_parameters_table(database, id_mode, id_region)

    data_table = table.Table(monetization_parameter_table)
    sheet = _write_data_to_sheet(sheet, data_table)

    sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=40)


def _monetization_parameters_table(database, id_mode, id_region):
    value_of_statistical_life = database_utils.parameter_table(
        database, id_mode, "who_parameters", {"id_region": str(id_region), "id_parameter": str(37)}
    )
    value_of_a_life_year = database_utils.parameter_table(
        database, id_mode, "who_parameters", {"id_region": str(id_region), "id_parameter": str(56)}
    )
    value_of_a_lost_workday = database_utils.parameter_table(
        database,
        id_mode,
        "iiasa_lost_working_days_monetization_factors",
        {"id_parameter": str(19), "id_region": str(id_region)},
    )
    hospitalisation_monetisation = database_utils.parameter_table(
        database,
        id_mode,
        "iiasa_lost_working_days_monetization_factors",
        {"id_parameter": str(63), "id_region": str(id_region)},
    )
    cost_per_ton_of_emitted_co2 = database_utils.parameter_table(
        database, id_mode, "iiasa_greenhouse_gas_emission_monetization_factors", {"id_region": str(id_region)}
    )
    cost_of_statistical_transfer_of_res = database_utils.parameter_table(
        database, id_mode, "fraunhofer_constant_parameters", {"id_region": str(id_region), "id_parameter": str(61)}
    )
    investment_costs_of_pv = database_utils.parameter_table(
        database, id_mode, "irena_technology_parameters", {"id_parameter": str(44), "id_technology": str(3)}
    )
    investment_costs_of_onshore_wind = database_utils.parameter_table(
        database, id_mode, "irena_technology_parameters", {"id_parameter": str(44), "id_technology": str(1)}
    )
    investment_costs_of_offshore_wind = database_utils.parameter_table(
        database, id_mode, "irena_technology_parameters", {"id_parameter": str(44), "id_technology": str(2)}
    )

    parameter_tables = {
        "Value of statistical life [€]": value_of_statistical_life,
        "Value of a life year [€]": value_of_a_life_year,
        "Value of a lost work day [€]": value_of_a_lost_workday,
        "Hospitalisation monetisation [€]": hospitalisation_monetisation,
        "Cost per ton of emitted CO2 [€/tCO2]": cost_per_ton_of_emitted_co2,
        "Cost of statistical transfer of RES [€/ktoe]": cost_of_statistical_transfer_of_res,
        "Investment costs of PV [€/MW]": investment_costs_of_pv,
        "Investment costs of onshore wind [€/MW]": investment_costs_of_onshore_wind,
        "Investment costs of offshore wind [€/MW]": investment_costs_of_offshore_wind,
    }

    monetization_parameter_table = _construct_monetization_parameter_table(parameter_tables)
    monetization_parameter_table = monetization_parameter_table.fillna("")

    return monetization_parameter_table


def _construct_monetization_parameter_table(parameter_tables):
    rows = []
    for parameter_table_name in parameter_tables.keys():
        parameter_table = parameter_tables[parameter_table_name]
        data = parameter_table.to_data_frame().to_dict(orient="records")
        for row in data:
            row["Monetisation factor"] = parameter_table_name
            rows.append(row)
    monetization_parameter_table = pd.DataFrame(rows)
    monetization_parameter_table = monetization_parameter_table.rename(columns=str.capitalize)
    first_columns = ["Monetisation factor", "Value"]
    ordered_columns = first_columns + monetization_parameter_table.columns.drop(first_columns).to_list()
    # pylint: disable=unsubscriptable-object
    monetization_parameter_table = monetization_parameter_table[ordered_columns]
    return monetization_parameter_table


# pylint: disable=too-many-arguments
def _subsector_final_create_parameter_sheet(
    workbook,
    sheet_name,
    template_args,
    database,
    id_subsector_table,
    id_final_energy_carrier_table,
):
    id_mode = template_args["id_mode"]
    id_region = template_args["id_region"]
    years = template_args.get("years")
    ignore_years = template_args.get("ignore_years", [])

    sheet = workbook.add_worksheet(sheet_name)
    sheet = _add_parameters_header(
        sheet, workbook, ["id_subsector", "id_final_energy_carrier", "Subsector", "Final energy carrier"]
    )
    sheet = _subsector_final_add_parameters_data_validation(
        sheet,
        template_args["options_sheet_name"],
        id_mode,
        id_subsector_table,
        id_final_energy_carrier_table,
    )

    id_parameter = 11

    sheet = _subsector_final_add_parameter_data(
        sheet,
        database,
        "eurostat_final_sector_parameters" if mode.is_eurostat_mode(id_mode) else "primes_final_sector_parameters",
        id_mode,
        id_region,
        id_parameter,
        id_subsector_table,
        id_final_energy_carrier_table,
        years,
        ignore_years,
    )

    sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=30)


def _primary_create_parameter_sheet(
    workbook,
    sheet_name,
    template_args,
    database,
    id_primary_energy_carrier_table,
):
    id_mode = template_args["id_mode"]
    id_region = template_args["id_region"]
    years = template_args.get("years")
    years = template_args.get("years")
    ignore_years = template_args.get("ignore_years", [])

    sheet = workbook.add_worksheet(sheet_name)
    sheet = _add_parameters_header(
        sheet, workbook, ["id_subsector", "id_final_energy_carrier", "Subsector", "Final energy carrier"]
    )
    sheet = _primary_add_parameters_data_validation(
        sheet,
        template_args["options_sheet_name"],
        id_mode,
        id_primary_energy_carrier_table,
    )

    if sheet_name == "ElectricityGeneration":
        id_parameter = 21
        sheet = _primary_add_parameter_data(
            sheet,
            database,
            "eurostat_primary_parameters"
            if mode.is_eurostat_mode(id_mode)
            else "primes_primary_parameters_confidential",
            id_mode,
            id_region,
            id_parameter,
            id_primary_energy_carrier_table,
            years,
            ignore_years,
        )

    elif sheet_name == "HeatGeneration":
        id_parameter = 20
        sheet = _primary_add_parameter_data(
            sheet,
            database,
            "eurostat_primary_parameters"
            if mode.is_eurostat_mode(id_mode)
            else "primes_primary_parameters_confidential",
            id_mode,
            id_region,
            id_parameter,
            id_primary_energy_carrier_table,
            years,
            ignore_years,
        )

    sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=30)


def _create_options_sheet(
    workbook,
    template_args,
    id_subsector_table,
    id_final_energy_carrier_table,
    id_primary_energy_carrier_table,
):
    options_sheet_name = template_args["options_sheet_name"]
    options_sheet = workbook.add_worksheet(options_sheet_name)

    subsectors = id_subsector_table["label"].values
    options_sheet.write_column(row=0, col=0, data=subsectors)

    final_energy_carriers = id_final_energy_carrier_table["label"].values
    options_sheet.write_column(row=0, col=1, data=final_energy_carriers)

    primary_energy_carriers = id_primary_energy_carrier_table["label"].values
    options_sheet.write_column(row=0, col=0, data=primary_energy_carriers)

    options_sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=30)
    password = template_args["sheet_password"]
    xlsx_utils.protect_sheet(options_sheet, password, True)

    return options_sheet


def _add_parameters_header(sheet, workbook, header_columns):
    header_format = workbook.add_format(_header_format())
    sheet.set_row(row=0, height=None, cell_format=header_format)
    sheet.write_row(row=0, col=0, data=header_columns)
    return sheet


def _subsector_final_add_parameters_data_validation(
    sheet,
    options_sheet_name,
    id_mode,
    id_subsector_table,
    id_final_energy_carrier_table,
):
    sheet.data_validation(
        first_row=0,
        first_col=0,
        last_row=0,
        last_col=0,
        options=validators.exact_string_validator("Subsector", 0, 0, 0, 0),
    )
    sheet.data_validation(
        first_row=0,
        first_col=1,
        last_row=0,
        last_col=1,
        options=validators.exact_string_validator("Final energy carrier", 0, 1, 0, 1),
    )
    sheet.data_validation(
        first_row=0,
        first_col=2,
        last_row=0,
        last_col=constants.MAX_COLS,
        options=validators.year_header_validator(id_mode),
    )
    sheet.data_validation(
        first_row=1,
        first_col=2,
        last_row=constants.MAX_ROWS,
        last_col=constants.MAX_COLS,
        options=validators.parameter_cell_validator(),
    )
    sheet.data_validation(
        first_row=1,
        first_col=0,
        last_row=constants.MAX_ROWS,
        last_col=0,
        options=validators.subsector_list_dropdown_validator(options_sheet_name, id_subsector_table),
    )
    sheet.data_validation(
        first_row=1,
        first_col=1,
        last_row=constants.MAX_ROWS,
        last_col=1,
        options=validators.final_energy_carrier_list_dropdown_validator(
            options_sheet_name, id_final_energy_carrier_table
        ),
    )
    return sheet


def _primary_add_parameters_data_validation(
    sheet,
    options_sheet_name,
    id_mode,
    id_primary_energy_carrier_table,
):
    sheet.data_validation(
        first_row=0,
        first_col=0,
        last_row=0,
        last_col=0,
        options=validators.exact_string_validator("Primary energy carrier", 0, 0, 0, 0),
    )
    sheet.data_validation(
        first_row=0,
        first_col=1,
        last_row=0,
        last_col=constants.MAX_COLS,
        options=validators.year_header_validator(id_mode),
    )
    sheet.data_validation(
        first_row=1,
        first_col=2,
        last_row=constants.MAX_ROWS,
        last_col=constants.MAX_COLS,
        options=validators.parameter_cell_validator(),
    )
    sheet.data_validation(
        first_row=1,
        first_col=0,
        last_row=constants.MAX_ROWS,
        last_col=0,
        options=validators.primary_energy_carrier_list_dropdown_validator(
            options_sheet_name, id_primary_energy_carrier_table
        ),
    )
    return sheet


def _monetization_add_parameters_data_validation(
    sheet,
    id_mode,
):
    sheet.data_validation(
        first_row=0,
        first_col=0,
        last_row=0,
        last_col=0,
        options=validators.exact_string_validator("Monetisation factor", 0, 1, 0, 1),
    )
    sheet.data_validation(
        first_row=0,
        first_col=1,
        last_row=0,
        last_col=1,
        options=validators.exact_string_validator("Value", 0, 1, 0, 1),
    )
    sheet.data_validation(
        first_row=0,
        first_col=2,
        last_row=0,
        last_col=constants.MAX_COLS,
        options=validators.year_header_validator(id_mode),
    )
    sheet.data_validation(
        first_row=1,
        first_col=1,
        last_row=constants.MAX_ROWS,
        last_col=constants.MAX_COLS,
        options=validators.parameter_cell_validator(),
    )
    return sheet


# pylint: disable=too-many-arguments
def _subsector_final_add_parameter_data(
    sheet,
    database,
    table_name,
    id_mode,
    id_region,
    id_parameter,
    id_subsector_table,
    id_final_energy_carrier_table,
    years=None,
    ignore_years=[],
):
    column_names = database_utils.column_names(database, table_name)
    filtered_column_names = database_utils.filter_column_names_by_id_mode(column_names, id_mode, years)
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": str(id_parameter),
    }

    data_table = database_utils.table(database, table_name, filtered_column_names, where_clause)
    data_table = data_table.reduce("id_parameter", id_parameter)

    data_table = data_table.join_id_column(
        id_subsector_table,
        "subsector",
        is_keeping_id_column=True,
    )

    data_table = data_table.join_id_column(
        id_final_energy_carrier_table,
        "final_energy_carrier",
        is_keeping_id_column=True,
    )

    data_table = _subsector_final_reorder_and_rename_columns(data_table)

    if len(ignore_years) > 0:
        data_table = data_table.drop(columns=ignore_years)

    # Add empty columns for years that are not present in the database
    if years is not None:
        for year in years:
            if year not in ignore_years and year not in data_table.columns:
                data_table[year] = ""

    sheet = _write_data_to_sheet(sheet, data_table)
    return sheet


def _primary_add_parameter_data(
    sheet,
    database,
    table_name,
    id_mode,
    id_region,
    id_parameter,
    id_primary_energy_carrier_table,
    years=None,
    ignore_years=[],
):
    column_names = database_utils.column_names(database, table_name)
    filtered_column_names = database_utils.filter_column_names_by_id_mode(column_names, id_mode, years)
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": str(id_parameter),
    }

    data_table = database_utils.table(database, table_name, filtered_column_names, where_clause)
    data_table = data_table.reduce("id_parameter", id_parameter)

    data_table = data_table.join_id_column(
        id_primary_energy_carrier_table,
        "primary_energy_carrier",
        is_keeping_id_column=True,
    )

    data_table = _primary_reorder_and_rename_columns(data_table)

    if len(ignore_years) > 0:
        data_table = data_table.drop(columns=ignore_years)

    # Add empty columns for years that are not present in the database
    if years is not None:
        for year in years:
            if year not in ignore_years and year not in data_table.columns:
                data_table[year] = ""

    sheet = _write_data_to_sheet(sheet, data_table)
    return sheet


def _subsector_final_reorder_and_rename_columns(data_table):
    columns = data_table.columns
    columns.insert(0, columns.pop(columns.index("subsector")))
    columns.insert(1, columns.pop(columns.index("final_energy_carrier")))
    data_table = data_table[columns]
    columns_mapping = {
        "subsector": "Subsector",
        "final_energy_carrier": "Final energy carrier",
    }
    data_table.rename(columns=columns_mapping, inplace=True)
    return data_table


def _primary_reorder_and_rename_columns(data_table):
    columns = data_table.columns
    columns.insert(0, columns.pop(columns.index("primary_energy_carrier")))
    data_table = data_table[columns]
    columns_mapping = {
        "primary_energy_carrier": "Primary energy carrier",
    }
    data_table.rename(columns=columns_mapping, inplace=True)
    return data_table


def _write_data_to_sheet(sheet, data_table):
    numpy_table = data_table.to_numpy_with_headers()
    for row_num, row_data in enumerate(numpy_table):
        for col_num, col_data in enumerate(row_data):
            sheet.write(row_num, col_num, col_data)
    return sheet


def _header_format():
    return {
        "bg_color": "#C0C0C0",
        "bold": True,
        "locked": False,
    }
