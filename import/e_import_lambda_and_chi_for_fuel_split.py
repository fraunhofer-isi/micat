# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/24
# pylint: disable=duplicate-code
import warnings

import pandas as pd

from config import import_config
from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.table import Table

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database = Database(public_database_path)
    database_import = DatabaseImport(public_database_path)

    import_folder = raw_data_path + "/action_type_fuel_split_coefficient"

    print("Importing lambda...")
    lambda_ = determine_lambda(database)
    database_import.write_to_sqlite(lambda_, "eurostat_final_sector_parameters")

    print("Importing chi...")
    id_region_table = database.id_table("id_region")
    final_energy_carrier_ids = read_final_energy_carrier_ids(database)
    chi = determine_chi(import_folder, id_region_table, final_energy_carrier_ids)

    print("Determining missing entries for chi...")
    missing_entries = database_import.validate_table(
        chi, "mixed_final_constant_parameters"
    )
    file_path = import_folder + "/chi_missing_entries.xlsx"
    _write_missing_entries_as_excel_file(missing_entries, file_path)

    print("Merging missing entries...")
    chi_missing_entries = pd.read_excel(file_path)

    chi_missing_entries.set_index(
        [
            "id_region",
            "id_parameter",
            "id_subsector",
            "id_action_type",
            "id_final_energy_carrier",
        ],
        inplace=True,
    )

    chi = Table.concat([chi, chi_missing_entries])

    # mixed: from several sources: forecast, primes
    # final_constant_parameters: these values are assumed to be independent of the year
    print("# Writing  mixed_final_constant_parameters...")
    database_import.write_to_sqlite(chi, "mixed_final_constant_parameters")


def _write_missing_entries_as_excel_file(entries, file_path):
    rows = list(map(_create_chi_row, entries))
    df = pd.DataFrame(rows)
    df.to_excel(file_path, index=False)


def _create_chi_row(entry):
    row = {key: value[0] for key, value in entry.items()}
    row["value"] = -999
    return row


def determine_lambda(database):
    final_energy_consumption = database.table("eurostat_final_energy_consumption", {})
    lambda_ = final_energy_consumption.normalize(["id_region", "id_subsector"])
    lambda_ = lambda_.insert_index_column("id_parameter", 1, 11)
    return lambda_


def read_final_energy_carrier_ids(database):
    id_table = database.id_table("id_final_energy_carrier")
    id_values = list(id_table.index.values)
    return id_values


def determine_chi(
    import_folder,
    id_region_table,
    final_energy_carrier_ids,
):
    chi_industry = calculate_chi_industry(import_folder, final_energy_carrier_ids)
    chi_others = read_chi_others(import_folder, id_region_table)
    chi = pd.concat(
        [
            chi_industry,
            chi_others,
        ]
    )
    chi.name = "value"
    chi_table = Table(chi)
    chi_table = chi_table.insert_index_column("id_parameter", 1, 12)
    return chi_table


def calculate_chi_industry(import_folder, final_energy_carrier_ids):
    useless_columns = [
        "Unnamed: 0",
        "Project",
        "Revision ",
        "Scenario",
        "Country",
        "Energy carrier",
        "Sector",
        "Level_1",
        "Level_2",
        "Level_3",
        "Unit",
    ]

    file_path = import_folder + "/chi_industry.xlsx"
    final_energy_demand_dataframe = pd.read_excel(
        file_path, sheet_name="Result_FinalEnergyDemand_"
    )
    final_energy_demand_dataframe.drop(useless_columns, axis=1, inplace=True)

    index_columns = [
        "id_region",
        "id_subsector",
        "id_action_type",
        "id_final_energy_carrier",
    ]

    # There might be several rows that belong to the same combination of id_columns because
    # we do not map the difference in "Level_2".
    # Therefore, we sum up those rows.
    aggregated_final_energy_demand = final_energy_demand_dataframe.groupby(
        index_columns
    ).sum()

    final_energy_demand_in_twh = Table(aggregated_final_energy_demand)
    if final_energy_demand_in_twh.contains_nan():
        raise ValueError("Data must not contain NaN values")

    if final_energy_demand_in_twh.contains_negative_values():
        message = "Demand data should not contain negative values; we replace them with 0 for the time being..."
        warnings.warn(message)
        final_energy_demand_in_twh = (
            final_energy_demand_in_twh.replace_negative_values_with_zero()
        )

    chi = calculate_chi_from_final_energy_demand(final_energy_demand_in_twh)

    missing_final_energy_carrier_ids = final_energy_carrier_ids.copy()
    missing_final_energy_carrier_ids.remove(
        1
    )  # id_final_energy_carrier = 1 is already included in data
    chi = append_zeros_for_missing_energy_carriers_of_cross_cutting_technology(
        chi, missing_final_energy_carrier_ids
    )

    return chi


def calculate_chi_from_final_energy_demand(final_energy_demand_in_twh):
    annual_chi = final_energy_demand_in_twh.normalize(
        ["id_region", "id_final_energy_carrier", "id_subsector"]
    )
    chi = annual_chi.annual_mean()
    chi.name = "chi"
    return chi


def read_chi_others(import_folder, id_region_table):
    raw_data_frames = pd.read_excel(
        import_folder + "/chi_all_but_industry.xlsx", sheet_name=None
    )
    regional_tables = translate_regional_sheets(raw_data_frames, id_region_table)
    table = Table.concat(regional_tables)
    chi_series = table["chi"]
    return chi_series


def translate_regional_sheets(sheets, id_region_table):
    columns = ["id_subsector", "id_action_type", "id_final_energy_carrier", "chi"]

    tables = []
    for sheet_name, raw_sheet in sheets.items():
        sheet = raw_sheet[columns]
        id_region = id_region_table.id_by_description(sheet_name)
        sheet["id_region"] = id_region

        # define order of columns:
        sheet = sheet[
            [
                "id_region",
                "id_subsector",
                "id_action_type",
                "id_final_energy_carrier",
                "chi",
            ]
        ]

        table = Table(sheet)
        tables.append(table)
    return tables


def append_zeros_for_missing_energy_carriers_of_cross_cutting_technology(
    series, missing_final_energy_carrier_ids
):
    # TO DO: why doing this at all?
    # TO DO: already add zeros in raw data or remove the zeros?
    # do not add zeros for all combinations but only the unique already existing ones
    id_action_type = 8  # cross-cutting technology
    index_entries = index_entries_for_action_type(series, id_action_type)

    for entry in index_entries:
        id_region = entry[0]
        id_subsector = entry[1]
        for id_final_energy_carrier in missing_final_energy_carrier_ids:
            extra_row = _create_series_with_single_row(
                id_region,
                id_subsector,
                id_action_type,
                id_final_energy_carrier,
            )
            series = pd.concat([series, extra_row])

    sorted_series = series.sort_index()
    return sorted_series


def index_entries_for_action_type(series, id_action_type):
    existing_entries = series.to_frame().query(
        "id_action_type == " + str(id_action_type)
    )["chi"]
    index = existing_entries.index
    #  we assume that id_final_energy_carrier is 1 for all entries and can be dropped
    base_index = index.droplevel(level=["id_final_energy_carrier", "id_action_type"])
    return base_index


def _create_series_with_single_row(
    id_region,
    id_subsector,
    id_action_type,
    id_final_energy_carrier,
):
    extra_series_index = pd.MultiIndex.from_tuples(
        [(id_region, id_subsector, id_action_type, id_final_energy_carrier)],
        names=[
            "id_region",
            "id_subsector",
            "id_action_type",
            "id_final_energy_carrier",
        ],
    )
    extra_series = pd.Series([0], index=extra_series_index)
    return extra_series


if __name__ == "__main__":
    main()
