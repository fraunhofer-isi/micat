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

    database_import = DatabaseImport(public_database_path)

    import_path = raw_data_path + '/irena'

    turnover_file_path = import_path + "/turnover_per_unit_of_energy_saved.xlsx"
    raw_turnover = pd.read_excel(turnover_file_path)
    turnover = Table(raw_turnover)
    id_parameter = 49  # Turnover per unit of energy saved
    turnover = turnover.insert_index_column('id_parameter', 0, id_parameter)

    database_import.write_to_sqlite(turnover, 'irena_parameters')

    investment_file_path = import_path + '/investment_costs_of_renewable_energy_system_technologies.xlsx'
    raw_investment = pd.read_excel(investment_file_path)
    investment = Table(raw_investment)
    id_parameter = 44  # Investment costs of renewable energy system technologies
    investment = investment.insert_index_column('id_parameter', 0, id_parameter)

    database_import.write_to_sqlite(investment, 'irena_technology_parameters')


if __name__ == "__main__":
    main()
