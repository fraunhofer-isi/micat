# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import numpy as np
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

    import_path = raw_data_path + "/wuppertal"

    database_import.import_id_table("id_decile", import_path)

    file_path = import_path + "/energy_poverty.xlsx"
    raw_energy_poverty_parameters = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)

    decile_parameters, sector_parameters, constant_parameters, parameters = _read_energy_poverty_tables(
        raw_energy_poverty_parameters
    )
    extended_decile_parameters = PopulationUtils.extend_european_values(decile_parameters, database)

    extended_parameters = PopulationUtils.extend_european_values(parameters, database)
    # Filter out parameter, since they are handled in d_download_and_import_eurostat_data.py
    extended_parameters = extended_parameters[~extended_parameters.index.isin([25], level=1)]

    database_import.write_to_sqlite(extended_decile_parameters, "wuppertal_decile_parameters")
    database_import.write_to_sqlite(sector_parameters, "wuppertal_sector_parameters")
    database_import.write_to_sqlite(constant_parameters, "wuppertal_constant_parameters")
    # We enhance the table only, since it's are already in the database due to d_download_and_import_eurostat_data.py
    # We need to interpolate missing values though
    for year in [
        "2003",
        "2004",
        "2005",
        "2006",
        "2007",
        "2008",
        "2009",
        "2011",
        "2012",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "2021",
        "2022",
        "2023",
    ]:
        extended_parameters._data_frame.insert(1, year, np.nan)
    extended_parameters._data_frame = extended_parameters._data_frame.interpolate(axis=1)
    # Combine already existing entries
    extended_parameters._data_frame = pd.concat(
        [extended_parameters._data_frame, database.table("wuppertal_parameters", {})._data_frame],
        ignore_index=False,
        sort=False,
    )
    database_import.write_to_sqlite(extended_parameters, "wuppertal_parameters")

    file_path = import_path + "/health.xlsx"
    raw_health_parameters = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)
    health_parameters = _read_health_tables(raw_health_parameters)
    database_import.write_to_sqlite(health_parameters, "wuppertal_health_parameters")


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
        table = table.insert_index_column("id_parameter", 1, id_parameter)

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
        table = Table(data_frame.drop(columns=["id"], errors="ignore"))
        table = table.to_table_with_string_column_names()
        tables.append(table)
    health_tables = Table.concat(tables)
    return health_tables


if __name__ == "__main__":
    main()
