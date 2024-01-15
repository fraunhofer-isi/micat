# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=duplicate-code
import pandas as pd
from config import import_config

from data_import.database_import import DatabaseImport
from table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database = DatabaseImport(public_database_path)

    import_path = raw_data_path + '/who'

    file_path = import_path + '/health_monetization_factors.xlsx'
    raw_monetization_factors = pd.read_excel(file_path, sheet_name=None)

    who_monetization = _read_who_monetization_tables(raw_monetization_factors)

    database.write_to_sqlite(who_monetization, 'who_parameters')


def _to_table(raw_factors):
    factors = Table(raw_factors)
    factors = factors.to_table_with_string_column_names()
    return factors


def _import_value_of_statistical_life(raw_monetization_factors):
    raw_value_of_statistical_life = raw_monetization_factors['VSL']
    del raw_value_of_statistical_life['country']
    value_of_statistical_life = Table(raw_value_of_statistical_life)
    value_of_statistical_life = value_of_statistical_life.insert_index_column('id_parameter', 1, 37)
    return value_of_statistical_life


def _import_value_of_life_year(raw_monetization_factors):
    raw_value_of_life_year = raw_monetization_factors['VOLY']
    del raw_value_of_life_year['country']
    value_of_life_year = Table(raw_value_of_life_year)
    value_of_life_year = value_of_life_year.insert_index_column('id_parameter', 1, 56)
    return value_of_life_year


def _read_who_monetization_tables(raw_monetization_factors):
    value_of_statistical_life = _import_value_of_statistical_life(raw_monetization_factors)
    value_of_life_year = _import_value_of_life_year(raw_monetization_factors)
    who_tables = Table.concat([value_of_statistical_life, value_of_life_year])
    return who_tables


if __name__ == '__main__':
    main()
