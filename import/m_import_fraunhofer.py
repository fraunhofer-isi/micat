# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database_import = DatabaseImport(public_database_path)

    import_path = raw_data_path + "/fraunhofer"

    cost_of_res_statistical_transfer_file_path = import_path + "/statistical_transfers.xlsx"
    raw_cost_of_res_statistical_transfer = pd.read_excel(cost_of_res_statistical_transfer_file_path)
    cost_of_res_statistical_transfer = Table(raw_cost_of_res_statistical_transfer)
    id_parameter = 61
    fraunhofer_constant_parameters = cost_of_res_statistical_transfer.insert_index_column(
        "id_parameter",
        1,
        id_parameter,
    )

    capacity_factors_path = import_path + "/capacity_factors_res.xlsx"
    raw_capacity_factors = pd.read_excel(capacity_factors_path)
    capacity_factors = Table(raw_capacity_factors)
    id_parameter = 64
    fraunhofer_capacity_factors = capacity_factors.insert_index_column(
        "id_parameter",
        1,
        id_parameter,
    )

    database_import.write_to_sqlite(fraunhofer_constant_parameters, "fraunhofer_constant_parameters")

    database_import.write_to_sqlite(fraunhofer_capacity_factors, "fraunhofer_capacity_factors")
    # In case of issue with AnnualSeries, comment out "self._table_validator.validate(sorted_table, details)" in the
    # write_to_sqlite method of the DatabaseImport class


if __name__ == "__main__":
    main()
