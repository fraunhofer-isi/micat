# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.template import xlsx_utils


MIN_YEAR = 2000
MAX_YEAR = 2050


def exact_string_validator(string_name, first_row, first_col, last_row, last_col):
    cells = xlsx_utils.slice_to_cell_string(first_row, first_col, last_row, last_col)
    return {
        "validate": "custom",
        "value": f'=EXACT({cells}, "{string_name}")',
    }


def year_header_validator():
    return {
        "validate": "integer",
        "criteria": "between",
        "minimum": MIN_YEAR,
        "maximum": MAX_YEAR,
        "input_title": "Enter a year",
        "input_message": f"between {MIN_YEAR} and {MAX_YEAR}",
    }


def parameter_cell_validator():
    return {
        "validate": "decimal",
        "criteria": "between",
        "minimum": 0,
        "maximum": 10**9,
        "input_title": "Enter a parameter",
        "input_message": "between 0 and 10^9",
    }


def subsector_list_dropdown_validator(options_sheet_name, id_subsector_table):
    subsector_validation_formula = _subsector_validation_formula(options_sheet_name, id_subsector_table)
    return {
        "validate": "list",
        "source": subsector_validation_formula,
    }


def _subsector_validation_formula(options_sheet_name, id_subsector_table):
    return f"={options_sheet_name}!A$1:A${len(id_subsector_table)}"


def final_energy_carrier_list_dropdown_validator(options_sheet_name, id_final_energy_carrier_table):
    final_energy_carrier_validation_formula = _final_energy_carrier_validation_formula(
        options_sheet_name,
        id_final_energy_carrier_table,
    )
    return {
        "validate": "list",
        "source": final_energy_carrier_validation_formula,
    }


def _final_energy_carrier_validation_formula(options_sheet_name, id_final_energy_carrier_table):
    return f"={options_sheet_name}!B$1:B${len(id_final_energy_carrier_table)}"


def primary_energy_carrier_list_dropdown_validator(options_sheet_name, id_primary_energy_carrier_table):
    primary_energy_carrier_validation_formula = _primary_energy_carrier_validation_formula(
        options_sheet_name,
        id_primary_energy_carrier_table,
    )
    return {
        "validate": "list",
        "source": primary_energy_carrier_validation_formula,
    }


def _primary_energy_carrier_validation_formula(options_sheet_name, id_primary_energy_carrier_table):
    return f"={options_sheet_name}!A$1:A${len(id_primary_energy_carrier_table)}"
