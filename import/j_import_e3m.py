# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()
    database_import = DatabaseImport(public_database_path)

    import_path = raw_data_path + "/e3m/"
    data_path = import_path + "/e3m_parameters_updated.xlsx"

    data = Table.read_excel(data_path)
    database_import.write_to_sqlite(data, "e3m_parameters")
