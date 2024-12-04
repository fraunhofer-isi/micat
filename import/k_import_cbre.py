# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=duplicate-code
import pandas as pd
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    import_path = raw_data_path + '/cbre'
    file_path = import_path + "/capitalisation_rate.xlsx"

    database_import = DatabaseImport(public_database_path)
    raw_parameters = pd.read_excel(file_path)

    table = Table(raw_parameters)
    table = table.insert_index_column('id_parameter', 1, 46)  # Capitalisation rate
    database_import.write_to_sqlite(table, '46_capitalisation_rate')


if __name__ == "__main__":
    main()
