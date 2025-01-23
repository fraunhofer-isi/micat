# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=duplicate-code
import pandas as pd
from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.table import Table


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database = Database(public_database_path)
    database_import = DatabaseImport(public_database_path)

    import_folder = raw_data_path + "/iiasa/"

    # Import gas emission monetization factors
    file_path = import_folder + "/greenhouse_gas_emission_monetization_factors.xlsx"
    raw_monetization_factors = pd.read_excel(file_path)
    monetization_factors = _to_table(raw_monetization_factors)

    id_parameter = 42
    monetization_factors = monetization_factors.insert_index_column(
        "id_parameter",
        1,
        id_parameter,
    )

    database_import.write_to_sqlite(monetization_factors, "iiasa_greenhouse_gas_emission_monetization_factors")

    # Import lost working days and (?) monetization factors
    id_region_table = database.id_table("id_region")
    id_parameter_table = database.id_table("id_parameter")
    monetization_factors = pd.read_excel(import_folder + "/monetisation_factors_updated.xlsx", engine="openpyxl")
    monetization_factors.LABEL_REGION = monetization_factors.LABEL_REGION.replace(
        {
            "EU27": "European Union",
            "Slovak Republic": "Slovakia",
        },
    )
    monetization_factors.MORB_IND = monetization_factors.MORB_IND.replace(
        {
            "Hospital admissions": "Hospitalisation monetisation",
            "Labor force WLD": "Value of lost work days",
        }
    )
    monetization_factors["YEAR"] = monetization_factors["YEAR"].astype(str)
    monetization_factors = id_region_table.label_to_id(monetization_factors, "LABEL_REGION")
    monetization_factors = id_parameter_table.label_to_id(monetization_factors, "MORB_IND")
    result = monetization_factors.pivot_table(
        values="COEFF",
        index=["id_region", "id_parameter"],
        columns="YEAR",
    )
    table = Table(result)
    database_import.write_to_sqlite(table, "iiasa_lost_working_days_monetization_factors")


def _to_table(raw_factors):
    factors = Table(raw_factors)
    factors = factors.to_table_with_string_column_names()
    return factors


if __name__ == "__main__":
    main()
