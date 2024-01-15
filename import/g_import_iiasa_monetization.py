# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
from config import import_config

from data_import.database_import import DatabaseImport
from table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database = DatabaseImport(public_database_path)

    import_folder = raw_data_path + '/iiasa/'

    file_path = import_folder + '/lost_working_days_monetization_factors.xlsx'
    raw_monetization_factors = pd.read_excel(file_path)
    monetization_factors = _to_table(raw_monetization_factors)

    id_parameter = 19
    monetization_factors = monetization_factors.insert_index_column(
        'id_parameter',
        1,
        id_parameter,
    )

    database.write_to_sqlite(monetization_factors, 'iiasa_lost_working_days_monetization_factors')

    file_path = import_folder + '/greenhouse_gas_emission_monetization_factors.xlsx'
    raw_monetization_factors = pd.read_excel(file_path)
    monetization_factors = _to_table(raw_monetization_factors)

    id_parameter = 42
    monetization_factors = monetization_factors.insert_index_column(
        'id_parameter',
        1,
        id_parameter,
    )

    database.write_to_sqlite(monetization_factors, 'iiasa_greenhouse_gas_emission_monetization_factors')


def _to_table(raw_factors):
    factors = Table(raw_factors)
    factors = factors.to_table_with_string_column_names()
    return factors


if __name__ == '__main__':
    main()
