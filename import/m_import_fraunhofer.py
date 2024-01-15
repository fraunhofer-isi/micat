# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
from config import import_config

from data_import.database_import import DatabaseImport
from table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database_import = DatabaseImport(public_database_path)

    import_path = raw_data_path + '/fraunhofer'

    cost_of_res_statistical_transfer_file_path = import_path + "/statistical_transfers.xlsx"
    raw_cost_of_res_statistical_transfer = pd.read_excel(cost_of_res_statistical_transfer_file_path)
    cost_of_res_statistical_transfer = Table(raw_cost_of_res_statistical_transfer)
    id_parameter = 61
    fraunhofer_constant_parameters = cost_of_res_statistical_transfer.insert_index_column(
        'id_parameter',
        1,
        id_parameter,
    )

    database_import.write_to_sqlite(fraunhofer_constant_parameters, 'fraunhofer_constant_parameters')


if __name__ == "__main__":
    main()
