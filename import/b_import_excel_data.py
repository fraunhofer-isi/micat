# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from config import import_config

from micat.data_import.database_import import DatabaseImport
from micat.utils.file import delete_file_if_exists


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database_import = DatabaseImport(public_database_path)

    delete_file_if_exists(public_database_path)

    database_import.import_id_table("id_region", raw_data_path)

    database_import.import_id_table("id_partner_region", raw_data_path)

    database_import.import_id_table("id_parameter", raw_data_path)

    database_import.import_id_table("id_sector", raw_data_path)

    database_import.import_id_table("id_subsector", raw_data_path)

    database_import.import_mapping_table(
        "mapping__subsector__sector",
        "id_subsector",
        "id_sector",
        raw_data_path,
    )

    database_import.import_id_table("id_indicator", raw_data_path)

    database_import.import_id_table("id_indicator_chart", raw_data_path)

    database_import.import_mapping_table(
        "mapping__indicator_chart__indicator",
        "id_indicator_chart",
        "id_indicator",
        raw_data_path,
    )

    database_import.import_id_table("id_indicator_group", raw_data_path)

    database_import.import_mapping_table(
        "mapping__indicator__indicator_group",
        "id_indicator",
        "id_indicator_group",
        raw_data_path,
    )

    database_import.import_id_table("id_action_type", raw_data_path, ["description"])

    database_import.import_mapping_table(
        "mapping__subsector__action_type",
        "id_subsector",
        "id_action_type",
        raw_data_path,
    )

    database_import.import_id_table("id_primary_energy_carrier", raw_data_path)

    database_import.import_id_table("id_final_energy_carrier", raw_data_path)

    database_import.import_id_table("id_technology", raw_data_path)

    # database_import.import_id_table('id_unit', raw_data_path)

    database_import.import_mapping_table(
        "mapping__final_energy_carrier__primary_energy_carrier",
        "id_final_energy_carrier",
        "id_primary_energy_carrier",
        raw_data_path,
    )

    database_import.import_id_table("id_start_year_usage", raw_data_path)

    database_import.import_mapping_table(
        "mapping__parameter__start_year_usage",
        "id_parameter",
        "id_start_year_usage",
        raw_data_path,
    )


if __name__ == "__main__":
    main()
