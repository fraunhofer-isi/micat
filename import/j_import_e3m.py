# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import time

import pandas as pd
import xlwings  # pylint: disable=import-error
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    import_path = raw_data_path + '/e3m/'

    affected_dwellings_file_path = import_path + '/nia_per_ktoe.xlsx'
    investment_cost_file_path = import_path + 'investments_per_ktoe.xlsx'
    gdp_and_employment_file_path = import_path + '/gdp_employment.xlsx'
    output_file_path = import_path + '/gdp_employment_extracted.xlsx'

    database = Database(public_database_path)
    database_import = DatabaseImport(public_database_path)

    _import_e3m_global_parameters(
        affected_dwellings_file_path,
        investment_cost_file_path,
        database_import,
    )

    _import_e3m_parameters(
        gdp_and_employment_file_path,
        output_file_path,
        database,
        database_import,
    )


def _import_e3m_global_parameters(
    affected_dwellings_file_path,
    investment_cost_file_path,
    database_import,
):
    affected_dwellings = Table.read_excel(affected_dwellings_file_path)
    investment_cost = Table.read_excel(investment_cost_file_path)
    global_parameters = Table.concat([affected_dwellings, investment_cost])
    database_import.write_to_sqlite(global_parameters, 'e3m_global_parameters')


def _import_e3m_parameters(
    gdp_and_employment_file_path,
    output_file_path,
    database,
    database_import,
):
    id_region_table = database.id_table('id_region')
    id_action_type_table = database.id_table('id_action_type')
    parameter_entries, debugging_output_entries = _determine_data(
        gdp_and_employment_file_path,
        id_region_table,
        id_action_type_table,
    )
    # the purpose of the debugging output entries is to help
    # with finding missing data
    data_frame = pd.DataFrame(debugging_output_entries)
    data_frame.to_excel(output_file_path, index=False)
    table = Table(parameter_entries)
    database_import.write_to_sqlite(table, 'e3m_parameters')


# pylint: disable=too-many-locals
def _determine_data(
    gdp_and_employment_file_path,
    id_region_table,
    id_action_type_table,
):
    parameter_entries = []
    debugging_output_entries = []
    for id_region, region_row in id_region_table.iterrows():
        region_label = region_row['label']
        for id_action_type, action_type_row in id_action_type_table.iterrows():
            action_type_label = action_type_row['label']

            message = 'Extracting data for id_region ' + str(id_region) + ' and id_action_type ' + str(id_action_type)
            print(message)

            gdp_and_employment_workbook = xlwings.Book(gdp_and_employment_file_path)

            _set_excel_input(
                gdp_and_employment_workbook,
                region_label,
                action_type_label,
            )

            gdp_entry, employment_entry, debugging_entry = _extract_output(
                gdp_and_employment_workbook,
                id_region,
                region_label,
                id_action_type,
                action_type_label,
            )

            parameter_entries.append(gdp_entry)
            parameter_entries.append(employment_entry)

            debugging_output_entries.append(debugging_entry)

    gdp_and_employment_workbook.app.quit()  # should only be called once; otherwise process slows down.

    return parameter_entries, debugging_output_entries


def _extract_output(
    workbook,
    id_region,
    region_label,
    id_action_type,
    action_type_label,
):
    gdp = workbook.sheets['GDP']
    gdp_coefficient_in_euro_per_euro = gdp['B3'].value
    gdp_coefficient_in_euro_per_euro = _validate_and_set_fallback_value(
        gdp_coefficient_in_euro_per_euro,
    )
    print('gdp_coefficient: ' + str(gdp_coefficient_in_euro_per_euro))
    employment = workbook.sheets['Employment']
    employment_coefficient_in_number_per_million_euro = employment['A3'].value
    employment_coefficient_in_number_per_million_euro = _validate_and_set_fallback_value(
        employment_coefficient_in_number_per_million_euro,
    )
    print('employment_coefficient: ' + str(employment_coefficient_in_number_per_million_euro))
    employment_coefficient_in_number_per_euro = employment_coefficient_in_number_per_million_euro / 1e6
    gdp_entry = {
        'id_region': id_region,
        'id_parameter': 38,
        'id_action_type': id_action_type,
        'value': gdp_coefficient_in_euro_per_euro,
    }
    employment_entry = {
        'id_region': id_region,
        'id_parameter': 39,
        'id_action_type': id_action_type,
        'value': employment_coefficient_in_number_per_euro,
    }
    debugging_entry = {
        'id_region': id_region,
        'id_action_type': id_action_type,
        'gdp_coefficient': gdp_coefficient_in_euro_per_euro,
        'employment_coefficient': employment_coefficient_in_number_per_million_euro,
        'region': region_label,
        'action_type': action_type_label,
    }
    return gdp_entry, employment_entry, debugging_entry


def _validate_and_set_fallback_value(coefficient):
    if coefficient == 0:
        print('# !!! Warning: zero value !!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if coefficient is None:
        coefficient = -999
        print('# !!! Warning: missing value !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return coefficient


def _set_excel_input(
    workbook,
    region_label,
    action_type_label,
):
    investment = workbook.sheets['Investment_Input']
    investment['B3'].value = action_type_label
    investment['C3'].value = region_label
    workbook.app.calculate()
    while workbook.app.api.CalculationState != xlwings.constants.CalculationState.xlDone:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
