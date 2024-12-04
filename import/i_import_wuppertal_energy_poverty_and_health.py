# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.data_import.population_utils import PopulationUtils
from micat.input.database import Database
from micat.table.table import Table
from micat.table.value_table import ValueTable


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database_import = DatabaseImport(public_database_path)
    database = Database(public_database_path)

    import_path = raw_data_path + '/wuppertal'

    database_import.import_id_table('id_decile', import_path)

    file_path = import_path + '/energy_poverty.xlsx'
    raw_energy_poverty_parameters = pd.read_excel(file_path, engine='openpyxl', sheet_name=None)

    decile_parameters, sector_parameters, constant_parameters, parameters = _read_energy_poverty_tables(
        raw_energy_poverty_parameters
    )
    extended_decile_parameters = PopulationUtils.extend_european_values(decile_parameters, database)

    extended_parameters = PopulationUtils.extend_european_values(parameters, database)

    database_import.write_to_sqlite(extended_decile_parameters, '27_28_57_58_energy_poverty_gaps')
    database_import.write_to_sqlite(sector_parameters, '36_action_lifetime')
    database_import.write_to_sqlite(constant_parameters, '59_60_M2_2M_equivalence_coefficients')
    database_import.write_to_sqlite(extended_parameters, '25_29_30_31_32_33_34_35_energy_poverty_coefficients')

    file_path = import_path + '/health.xlsx'
    raw_health_parameters = pd.read_excel(file_path, engine='openpyxl', sheet_name=None)
    health_parameters = _read_health_tables(raw_health_parameters)
    database_import.write_to_sqlite(health_parameters, '26_53_54_55_excess_cold_weather_mortality_coefficients')


def _read_energy_poverty_tables(raw_energy_poverty_parameters):  # pylint: disable=too-many-locals
    parameter_tables = []
    decile_parameter_tables = []
    sector_parameter_tables = []
    constant_parameter_tables = []

    sectorial_parameter_ids = [36]
    decile_parameter_ids = [27, 28, 57, 58]
    constant_ids = [59, 60]
    for sheet_name, data_frame in raw_energy_poverty_parameters.items():
        id_parameter = int(sheet_name)

        if id_parameter in sectorial_parameter_ids:
            table = ValueTable(data_frame)
        elif id_parameter in constant_ids:
            table = ValueTable(data_frame)
        else:
            table = Table(data_frame)
            table = table.to_table_with_string_column_names()
        table = table.insert_index_column('id_parameter', 1, id_parameter)

        if id_parameter in decile_parameter_ids:
            decile_parameter_tables.append(table)
        elif id_parameter in sectorial_parameter_ids:
            sector_parameter_tables.append(table)
        elif id_parameter in constant_ids:
            constant_parameter_tables.append(table)
        else:
            parameter_tables.append(table)
    decile_parameters = Table.concat(decile_parameter_tables)
    sector_parameters = ValueTable.concat(sector_parameter_tables)
    constant_parameters = ValueTable.concat(constant_parameter_tables)
    parameters = Table.concat(parameter_tables)

    return decile_parameters, sector_parameters, constant_parameters, parameters


def _read_health_tables(raw_health_parameters):
    tables = []
    for _, data_frame in raw_health_parameters.items():
        table = Table(data_frame.drop(columns=['id'], errors='ignore'))
        table = table.to_table_with_string_column_names()
        tables.append(table)
    health_tables = Table.concat(tables)
    return health_tables


if __name__ == '__main__':
    main()
