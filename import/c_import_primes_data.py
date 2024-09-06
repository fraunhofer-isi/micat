# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/148
import sqlite3

import pandas as pd
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.table import Table

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database = Database(public_database_path)
    database_import = DatabaseImport(public_database_path)

    import_folder = raw_data_path + '/primes'
    utilization_file_path = import_folder + '/renewable_energy_system_utilization_primes.xlsx'

    raw_sheets = pd.read_excel(import_folder + '/reference_scenario.xlsx', sheet_name=None)
    sheets = _clean_sheets(raw_sheets)

    id_region_table = database.id_table('id_region')
    id_parameter_table = database.id_table('id_parameter')

    print('# importing primes_parameters...')
    macroeconomic_data = _extract_macroeconomic_data(
        sheets,
        id_region_table,
        id_parameter_table,
    )
    # includes following values of id_parameter:
    # 10: GDP, Gross domestic product
    # 24: Population
    database_import.write_to_sqlite(macroeconomic_data, 'primes_parameters')

    print('# importing primes_primary_parameters...')
    primary_parameters = _determine_primary_parameters(
        sheets,
        id_region_table,
        database_import,
        import_folder,
    )
    # includes following values of id_parameter:
    # 1: PP, Primary production
    # 2: GAE, Gross available energy
    database_import.write_to_sqlite(primary_parameters, 'primes_primary_parameters')

    print('# importing primes_technology_parameters')
    _import_utilization(utilization_file_path, database_import)


def _import_utilization(file_path, database_import):
    utilization_frame = pd.read_excel(file_path)
    utilization = Table(utilization_frame)
    utilization = utilization.insert_index_column('id_parameter', 0, 47)

    database_import.write_to_sqlite(utilization, 'primes_technology_parameters')


def _clean_sheets(raw_sheets):
    raw_sheets.pop("Cover")
    sheets_a = {}
    for sheet_name, sheet in raw_sheets.items():
        region_code = _extract_region_code(sheet_name)
        if '_A' in sheet_name:
            sheets_a[region_code] = clean_type_a_sheet(sheet)
        elif '_B' in sheet_name:
            # currently we do not use the .._B sheets
            continue
        else:
            raise ValueError('Invalid sheet name ' + sheet_name)
    return sheets_a


def _extract_region_code(sheet_name):
    region_code = sheet_name.split('_')[0]
    region_code = region_code.replace('EU', 'EU27_2020')
    return region_code


def clean_type_a_sheet(sheet):
    column_start_index = 11
    useless_columns = sheet.columns[column_start_index:]
    cleaned_sheet = sheet.drop(useless_columns, axis=1)
    cleaned_sheet.rename(columns={'Unnamed: 0': 'primes'}, inplace=True)
    return cleaned_sheet


def _extract_macroeconomic_data(sheets, id_region_table, id_parameter):
    label_header = 'primes'

    useful_labels = ['Population (in million)', 'GDP (in 000 M€15)']
    label_map = {
        'Population (in million)': 'Population',
        'GDP (in 000 M€15)': 'GDP',
    }
    region_tables = []
    for region_code, sheet in sheets.items():
        id_region = id_region_table.id_by_description(region_code)
        years = _extract_years(sheet)
        df = sheet[sheet[label_header].isin(useful_labels)]
        df.replace(label_map, inplace=True)
        df = id_parameter.label_to_id(df, label_header)
        df['id_region'] = id_region
        df.set_index(['id_region', 'id_parameter'], inplace=True)
        df.columns = years
        df.loc[df.index.get_level_values('id_parameter') == 'GDP'] *= 1e9  # convert from B€ (1000 M€) to €
        df.loc[df.index.get_level_values('id_parameter') == 'Population'] *= 1e6  # convert from M to 1
        region_table = Table(df)
        region_tables.append(region_table)

    return Table.concat(region_tables)


def _extract_years(sheet):
    year_numbers = list(map(int, sheet.loc[0][1:].values))
    years = list(map(str, year_numbers))
    return years


def _determine_primary_parameters(
    sheets,
    id_region_table,
    database_import,
    import_folder,
):
    mapping__primes__primary_energy_carrier = database_import.read_mapping_table(
        'mapping__primes__primary_energy_carrier',
        'primes',
        'id_primary_energy_carrier',
        import_folder,
    )
    primary_production = _extract_primary_production(
        sheets,
        id_region_table,
        mapping__primes__primary_energy_carrier,
    )
    gross_available_energy = _extract_gross_available_energy(
        sheets,
        id_region_table,
        mapping__primes__primary_energy_carrier,
    )
    primary_parameters = Table.concat(
        [
            primary_production,
            gross_available_energy,
        ]
    )
    return primary_parameters


def _extract_primary_production(
    sheets,
    id_region_table,
    mapping__primes__primary_energy_carrier,
):
    useful_row_ids = [94, 95, 96]
    label_map = {
        'Biomass & Waste (6)': 'Biomass & Waste',
    }
    id_columns = ['id_region', 'id_parameter', 'id_primary_energy_carrier']
    region_tables = []
    for region_code, sheet in sheets.items():
        id_region = id_region_table.id_by_description(region_code)
        years = _extract_years(sheet)

        df = sheet.loc[useful_row_ids]
        df.replace(label_map, inplace=True)
        df['id_region'] = id_region
        df['id_parameter'] = 1  # primary production
        df = mapping__primes__primary_energy_carrier.apply_for(df)
        # several primes entries might be mapped to one energy carrier => sum up corresponding rows
        df = df.groupby(id_columns).sum()
        df.columns = years
        region_table = Table(df)
        region_tables.append(region_table)

    return Table.concat(region_tables)


def _extract_gross_available_energy(
    sheets,
    id_region_table,
    mapping__primes__primary_energy_carrier,
):
    useful_row_ids = [21, 22, 23, 24, 25, 26, 27, 28, 29]
    label_map = {
        'Biomass & Waste (6)': 'Biomass & Waste',
    }
    id_columns = ['id_region', 'id_parameter', 'id_primary_energy_carrier']
    region_tables = []
    for region_code, sheet in sheets.items():
        id_region = id_region_table.id_by_description(region_code)
        years = _extract_years(sheet)

        df = sheet.loc[useful_row_ids]
        df.replace(label_map, inplace=True)
        df['id_region'] = id_region
        df['id_parameter'] = 2  # gross available energy
        df = mapping__primes__primary_energy_carrier.apply_for(df)
        # several primes entries might be mapped to one energy carrier => sum up corresponding rows
        df = df.groupby(id_columns).sum()
        df.columns = years
        region_table = Table(df)
        region_tables.append(region_table)

    return Table.concat(region_tables)


def _eurostat_primary_parameters_data(database_path):
    con = sqlite3.connect(database_path)
    df = pd.read_sql_query("SELECT * FROM eurostat_primary_parameter_data", con)
    del df['id']
    return df


if __name__ == '__main__':
    main()
