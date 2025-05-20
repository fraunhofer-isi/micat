# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from config import import_config
import pandas as pd

from micat.data_import.database_import import DatabaseImport
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()
    database_import = DatabaseImport(public_database_path)

    import_path = raw_data_path + "/e3m/"

    # Import e3m_parameters
    e3m_parameters_path = import_path + "/e3m_parameters_updated.xlsx"
    data = Table.read_excel(e3m_parameters_path)
    database_import.write_to_sqlite(data, "e3m_parameters")

    # Import e3m_global_parameters
    investments_per_ktoe_path = import_path + "/investments_per_ktoe_updated.xlsx"
    investments_per_ktoe = Table.read_excel(investments_per_ktoe_path)
    investments_in_mio_per_ktoe = investments_per_ktoe / 1000000  # convert to mio €
    nia_per_ktoe_path = import_path + "/nia_per_ktoe_updated.xlsx"
    nia_per_ktoe = Table.read_excel(nia_per_ktoe_path)
    data = Table.concat([investments_in_mio_per_ktoe, nia_per_ktoe])
    database_import.write_to_sqlite(data, "e3m_global_parameters")

    # Import e3m_energy_prices
    energy_prices_path = import_path + "/e3m_energy_prices.xlsx"
    energy_prices = Table.read_excel(energy_prices_path)
    #energy_prices = energy_prices.set_index(['id_parameter', 'id_region', 'id_sector', 'id_final_energy_carrier'])
    print(energy_prices)
    database_import.write_to_sqlite(energy_prices, "e3m_energy_prices")


if __name__ == "__main__":
    main()
