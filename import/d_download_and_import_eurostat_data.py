# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import gzip
from warnings import warn

import pandas as pd
import requests
from config import import_config

from micat.data_import.conversion_coefficients import conversion_coefficients
from micat.data_import.database_import import DatabaseImport
from micat.input.database import Database
from micat.table.table import Table


# pylint: disable=too-many-locals
def main():
    public_database_path, raw_data_path = import_config.get_paths()

    database_import = DatabaseImport(public_database_path)
    database = Database(public_database_path)

    import_folder = raw_data_path + "/eurostat"

    siec_relation_url = (
        "https://ec.europa.eu/eurostat/documents/38154/4956218/Energy-Balance-Formulas.xlsx/cc2f9ade"
        "-5c0b-47b5-b83d-c05fe86eef6c "
    )
    siec_relation_file_path = import_folder + "/energy_balance_formulas.xlsx"

    utilization_file_path = import_folder + "/renewable_energy_system_utilization_eurostat.xlsx"

    # output_at_basic_price_file_path = import_folder + "/output_at_basic_price.xlsx"

    population_file_path = import_folder + "/population.xlsx"

    # risk_coefficient_file_path = import_folder + "/risk_coefficient_of_suppliers.xlsx"
    # imported_energy_file_path = import_folder + "/average_monthly_imported_energy.xlsx"

    is_skipping_download = False

    if not is_skipping_download:
        download_relations(siec_relation_url, siec_relation_file_path)
    try:
        siec_relations = read_siec_relations(siec_relation_file_path)
    except FileNotFoundError as exception:
        raise AttributeError("Could not find file. Please disable flag for skipping the download.") from exception

    for dataset in [
        {
            "code": "nrg_bal_c",
            "filter": {"unit": "KTOE", "siec": True},
        },
        {
            "code": "sdg_07_60",
            "filter": {"siec": False},
        },
    ]:
        url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{dataset['code']}/?format=TSV&compressed=true"
        zip_file_path = import_folder + f"/estat_{dataset['code']}.tsv.gz"
        file_path = import_folder + f"/estat_{dataset['code']}.tsv"

        if not is_skipping_download:
            print("Downloading eurostat data...")
            download_energy_balance_data(url, zip_file_path)

        print("Transforming eurostat data...")
        unzip_and_transform_energy_balance_data(zip_file_path, file_path)

        print("Reading eurostat data...")
        original_data_frame = pd.read_csv(file_path, sep="\t", decimal=".")
        original_data_frame.rename(columns={"geo\\TIME_PERIOD": "geo"}, inplace=True)
        year_column_names = original_data_frame.columns.to_list()[5:][::-1]  # Filter out non-year columns
        if dataset["code"] == "nrg_bal_c":
            import ipdb

            ipdb.set_trace()

            # Replace all non numeric values in year columns with NaN
            original_data_frame[year_column_names] = original_data_frame[year_column_names].apply(
                pd.to_numeric,
                errors="coerce",
            )

        cleaned_data_frame = clean_and_remove_redundant_rows(dataset, original_data_frame, siec_relations)

        regional_data_frame = join_region(cleaned_data_frame, database_import, import_folder)

        regional_data_frame = regional_data_frame[regional_data_frame["freq"] == "A"]
        del regional_data_frame["freq"]

        print("Creating and importing data...")
        if dataset["code"] == "nrg_bal_c":
            _create_data_for_final_energy_carrier(
                regional_data_frame,
                database_import,
                import_folder,
                year_column_names,
            )

            _create_data_for_primary_energy_carrier(
                regional_data_frame,
                database_import,
                import_folder,
                year_column_names,
            )

            _import_utilization(
                utilization_file_path,
                database_import,
            )

            # _import_output_source_at_basic_price_2015(
            #    output_at_basic_price_file_path,
            #    database,
            #    database_import,
            # )

            _import_population(
                import_folder,
                population_file_path,
                database_import,
            )

            # _import_supplier_diversity(
            #    risk_coefficient_file_path,
            #    imported_energy_file_path,
            #    database_import,
            # )
        elif dataset["code"] == "sdg_07_60":
            regional_data_frame = regional_data_frame[regional_data_frame["incgrp"] == "TOTAL"]
            del regional_data_frame["hhtyp"]
            del regional_data_frame["incgrp"]
            regional_data_frame = regional_data_frame.replace(r"[a-z]", "", regex=True)
            # Replace NaN values by copying values from previous or next years
            for column in regional_data_frame.columns:
                try:
                    prev = str(int(column) - 1)
                    next = str(int(column) + 1)
                except ValueError:
                    # Only consider columns with years
                    continue
                regional_data_frame[column] = regional_data_frame[column].fillna(
                    regional_data_frame[prev] if prev in regional_data_frame.columns else regional_data_frame[next]
                )
                if regional_data_frame[column].isnull().any():
                    # If there are still NaN values, search for the next year
                    regional_data_frame[column] = regional_data_frame[column].fillna(regional_data_frame[next])

            # Copy 2003 values to 2000
            regional_data_frame["2000"] = regional_data_frame["2003"]
            # Copy 2023 values to 2030
            regional_data_frame["2030"] = regional_data_frame["2023"]
            # Copy 2023 values to 2040
            regional_data_frame["2040"] = regional_data_frame["2023"]
            # Copy 2023 values to 2050
            regional_data_frame["2050"] = regional_data_frame["2023"]
            regional_data_frame = regional_data_frame[sorted(regional_data_frame)]
            table = Table(regional_data_frame)
            table = table.insert_index_column("id_parameter", 1, 25)
            # Remove column 2024 as it is not present in the wuppertal data
            table = table.drop("2024", axis=1)
            # IMPORTANT: This action clears the whole table, hence the Wuppertal import must be run after this one
            database_import.write_to_sqlite(table, "wuppertal_parameters")


def _create_data_for_final_energy_carrier(
    regional_data_frame,
    database_import,
    import_folder,
    year_column_names,
):
    # note: join does not sum rows with same target ids => ids might not be unique
    final_energy_carrier_data_frame = join_final_energy_carrier(
        regional_data_frame,
        database_import,
        import_folder,
    )

    # siec can either be mapped to parameter or subsector

    # a) map siec to subsector
    # note: join does not sum rows with same target ids => ids might not be unique
    sector_data_frame = join_subsector(
        final_energy_carrier_data_frame,
        database_import,
        import_folder,
    )

    # We sum up the rows having same ids => afterwards row ids are unique
    # During summation existing NaN values (might come for example from :z not applicable values) become
    # zero values.
    sector_id_columns = ["id_region", "id_subsector", "id_final_energy_carrier"]

    aggregated_sector_data_frame = sector_data_frame.groupby(sector_id_columns)[year_column_names].sum().reset_index()
    sector_table = Table(aggregated_sector_data_frame)

    sector_table = _fill_missing_values_for_final_energy_consumption(sector_table)

    print("# Writing eurostat_final_energy_consumption...")
    database_import.write_to_sqlite(sector_table, "eurostat_final_energy_consumption")

    # b) map siec to parameter
    # note: join does not sum rows with same target ids => ids might not be unique
    parameter_data_frame = join_parameter(final_energy_carrier_data_frame, database_import, import_folder)

    # We sum up the rows having same ids => afterward row ids are unique
    # During summation existing NaN values (might come for example from :z not applicable values) become
    # zero values.
    parameter_id_columns = ["id_region", "id_parameter", "id_final_energy_carrier"]
    parameter_data_frame = parameter_data_frame.groupby(parameter_id_columns)[year_column_names].sum().reset_index()

    parameter_table = Table(parameter_data_frame)

    parameter_table = _fill_missing_values_for_final_parameters(parameter_table)

    print("# Writing eurostat_final_parameters...")
    database_import.write_to_sqlite(parameter_table, "eurostat_final_parameters")


def _create_data_for_primary_energy_carrier(
    regional_data_frame,
    database_import,
    import_folder,
    year_column_names,
):
    # note: join does not sum rows with same target ids => ids might not be unique
    primary_energy_carrier_data_frame = join_primary_energy_carrier(regional_data_frame, database_import, import_folder)

    # note: join does not sum rows with same target ids => ids might not be unique
    parameter_data_frame = join_parameter(primary_energy_carrier_data_frame, database_import, import_folder)

    # we sum up the rows having same ids => afterwards row ids are unique
    parameter_id_columns = ["id_region", "id_parameter", "id_primary_energy_carrier"]
    parameter_data_frame = parameter_data_frame.groupby(parameter_id_columns)[year_column_names].sum().reset_index()
    parameter_table = Table(parameter_data_frame)

    extra_primary_parameters_table = calculate_extra_primary_parameters(
        regional_data_frame,
        database_import,
        import_folder,
        year_column_names,
    )

    parameter_table = Table.concat([parameter_table, extra_primary_parameters_table])

    parameter_table = _fill_missing_values_for_primary_parameters(parameter_table)

    print("# Writing eurostat_primary_parameters")
    database_import.write_to_sqlite(parameter_table, "eurostat_primary_parameters")


def _import_population(
    import_folder,
    file_path,
    database_import,
):
    population_sheet = pd.read_excel(file_path, sheet_name="Sheet 1")
    population_frame = _clean_population_sheet(population_sheet)
    population_frame = join_region(population_frame, database_import, import_folder)

    population = Table(population_frame)
    population = population.insert_index_column("id_parameter", 1, 24)

    print("# Writing eurostat_parameters")
    database_import.write_to_sqlite(population, "eurostat_parameters")


def _import_supplier_diversity(
    risk_coefficient_file_path,
    imported_energy_file_path,
    database_import,
):
    risk_coefficient_sheet = pd.read_excel(risk_coefficient_file_path)
    risk_coefficient = Table(risk_coefficient_sheet)
    risk_coefficient = risk_coefficient.insert_index_column("id_parameter", 1, 52)

    print("# Writing eurostat_partner_parameters")
    database_import.write_to_sqlite(risk_coefficient, "eurostat_partner_parameters")

    imported_energy_sheet = pd.read_excel(imported_energy_file_path)
    imported_energy = Table(imported_energy_sheet)
    imported_energy = imported_energy.insert_index_column("id_parameter", 1, 51)
    # business logic should only use id_final_energy_carrier values 2, 3, 4
    # we fill some dummy values to silence validation and to easier identify possible issues
    imported_energy.fill_missing_values("id_final_energy_carrier", [1, 5, 6, 7], -999)

    print("# Writing eurostat_partner_relation_parameters")
    database_import.write_to_sqlite(imported_energy, "eurostat_partner_relation_parameters")


def _clean_population_sheet(population_sheet):
    population_frame = population_sheet.iloc[10:38]
    population_frame.columns = _population_column_names(population_sheet)
    return population_frame


def _population_column_names(population_sheet):
    column_names = population_sheet.iloc[8]
    years = column_names[1:]
    int_years = list(map(int, years))
    year_column_names = list(map(str, int_years))
    column_names = ["geo"] + year_column_names
    return column_names


def _import_utilization(file_path, database_import):
    utilization_frame = pd.read_excel(file_path)
    utilization = Table(utilization_frame)
    utilization = utilization.insert_index_column("id_parameter", 0, 47)

    print("# Writing eurostat_technology_parameters")
    database_import.write_to_sqlite(utilization, "eurostat_technology_parameters")


# def _import_output_source_at_basic_price_2015(
#    file_path,
#    database,
#    database_import,
# ):
#    source_at_basic_price_frame = pd.read_excel(file_path)
#    source_at_basic_price = Table(source_at_basic_price_frame)
#
#    source_at_basic_price_europe = source_at_basic_price.reduce("id_region", 0)["value"]
#
#    gross_domestic_product_2015 = _gross_domestic_product_2015(database)
#
#    missing_id_regions = [6, 9, 17, 18, 19, 26, 27]
#    tables = []
#    for id_region in missing_id_regions:
#        source = _scaled_output_source_at_basic_price_2015(
#            source_at_basic_price_europe,
#            gross_domestic_product_2015,
#            id_region,
#        )
#        tables.append(source)
#
#    source_at_basic_price = Table.concat([source_at_basic_price] + tables)
#
#    source_at_basic_price = source_at_basic_price.insert_index_column("id_parameter", 1, 50)
#
#    print("# Writing eurostat_sector_parameters")
#    database_import.write_to_sqlite(source_at_basic_price, "eurostat_sector_parameters")


def _gross_domestic_product_2015(database):
    primes_parameters = database.table("primes_parameters", {})
    gross_domestic_product_in_euro = primes_parameters.reduce("id_parameter", 10)
    gross_domestic_product_2015 = gross_domestic_product_in_euro["2015"]
    return gross_domestic_product_2015


# def _scaled_output_source_at_basic_price_2015(
#    source_at_basic_price_europe,
#    gross_domestic_product_2015,
#    id_region,
# ):
#    id_region_europe = 0
#    gross_domestic_product_2015_europe = gross_domestic_product_2015[id_region_europe]
#    gross_domestic_product_2015_region = gross_domestic_product_2015[id_region]
#    source_series = (
#        source_at_basic_price_europe * gross_domestic_product_2015_region / gross_domestic_product_2015_europe
#    )
#    source = Table(source_series)
#    source = source.insert_index_column("id_region", 0, id_region)
#    return source


def _fill_missing_values_for_final_energy_consumption(table):
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/249

    table.fill_missing_values("id_final_energy_carrier", [7], 0)  # 7: H2 and e-fuels

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 18,  # Average transport
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 19,  # Rail
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 20,  # Road
            "id_final_energy_carrier": 3,  # Coal
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 20,  # Road
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 21,  # Aviation
            "id_final_energy_carrier": 1,  # Electricity
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 21,  # Aviation
            "id_final_energy_carrier": 3,  # Coal
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 21,  # Aviation
            "id_final_energy_carrier": 4,  # Gas
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 21,  # Aviation
            "id_final_energy_carrier": 5,  # Biomass and Waste
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 21,  # Aviation
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 22,  # Navigation
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_subsector": 24,  # Not elsewhere specified in transport
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    return table


def _fill_missing_values_for_final_parameters(table):
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/249

    table.fill_missing_values("id_final_energy_carrier", [7], 0)  # 7: H2 and e-fuels

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_final_energy_carrier": 1,  # Electricity
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_final_energy_carrier": 5,  # Biomass and Waste
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_final_energy_carrier": 6,  # Heat
        },
        0,
    )

    return table


def _fill_missing_values_for_primary_parameters(table):
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/249

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_primary_energy_carrier": 4,  # Biomass and Waste
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_primary_energy_carrier": 5,  # Renewables
        },
        0,
    )

    table.fill_missing_value(
        {
            "id_region": 0,  # European Union
            "id_parameter": 3,  # Non-energy
            "id_primary_energy_carrier": 6,  # Nuclear
        },
        0,
    )

    return table


def join_region(data_frame, database_import, import_folder):
    mapping_geo_region = database_import.read_mapping_table(
        "mapping__geo__region",
        "geo",
        "id_region",
        import_folder,
    )
    data_frame = mapping_geo_region.apply_for(data_frame)
    return data_frame


def join_subsector(data_frame, database_import, micat_folder):
    mapping_nrg_bal_subsector = database_import.read_mapping_table(
        "mapping__nrg_bal__subsector",
        "nrg_bal",
        "id_subsector",
        micat_folder,
    )
    subsector_data_frame = mapping_nrg_bal_subsector.apply_for(data_frame)
    return subsector_data_frame


def calculate_extra_primary_parameters(data_frame, database_import, micat_folder, year_column_names):
    primary_energy_carrier_mapping = database_import.read_mapping_table(
        "mapping__siec__energy_carrier",
        "siec",
        "id_primary_energy_carrier",
        micat_folder,
    )
    merged_nrg_bal = merge_nrg_bal(data_frame, primary_energy_carrier_mapping, year_column_names)
    coefficients = conversion_coefficients(merged_nrg_bal)
    return coefficients


def merge_nrg_bal(data_frame, primary_energy_carrier_mapping, year_column_names):
    # Also see # https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/47
    heat_in = merge_nrg_bal_entries(
        data_frame,
        ["TI_EHG_MAPH_E", "TI_EHG_APH_E"],
        primary_energy_carrier_mapping,
        year_column_names,
    )

    heat_out = merge_nrg_bal_output_entries(
        data_frame,
        ["TO_EHG_MAPH", "TO_EHG_APH"],
        "H8000",  # Heat
    )

    electricity_in = merge_nrg_bal_entries(
        data_frame,
        ["TI_EHG_MAPE_E", "TI_EHG_APE_E"],
        primary_energy_carrier_mapping,
        year_column_names,
    )

    electricity_out = merge_nrg_bal_output_entries(
        data_frame,
        ["TO_EHG_MAPE", "TO_EHG_APE"],
        "E7000",  # Electricity
    )

    chp_in = merge_nrg_bal_entries(
        data_frame,
        ["TI_EHG_MAPCHP_E", "TI_EHG_APCHP_E"],
        primary_energy_carrier_mapping,
        year_column_names,
    )

    chp_heat_out = merge_nrg_bal_output_entries(
        data_frame,
        ["TO_EHG_MAPCHP", "TO_EHG_APCHP"],
        "H8000",  # Heat
    )

    chp_electricity_out = merge_nrg_bal_output_entries(
        data_frame,
        ["TO_EHG_MAPCHP", "TO_EHG_APCHP"],
        "E7000",  # Electricity
    )

    merged_nrg_bal = {
        "heat_in": Table(heat_in),
        "heat_out": Table(heat_out),
        "electricity_in": Table(electricity_in),
        "electricity_out": Table(electricity_out),
        "chp_in": Table(chp_in),
        "chp_heat_out": Table(chp_heat_out),
        "chp_electricity_out": Table(chp_electricity_out),
    }
    return merged_nrg_bal


def merge_nrg_bal_entries(data_frame, nrg_bal_codes, primary_energy_carrier_mapping, year_column_names):
    left_frame = extract_nrg_bal(data_frame, nrg_bal_codes[0])
    right_frame = extract_nrg_bal(data_frame, nrg_bal_codes[1])
    frame = left_frame + right_frame
    frame = join_and_merge_primary_energy_carriers(frame, primary_energy_carrier_mapping, year_column_names)

    includes_nan = frame.isna().any().any()
    if includes_nan:
        warn("merged nrg_bal entries contain NaN values")
    return frame


def merge_nrg_bal_output_entries(data_frame, nrg_bal_codes, siec_code):
    left_frame = extract_nrg_bal_and_siec(data_frame, nrg_bal_codes[0], siec_code)
    right_frame = extract_nrg_bal_and_siec(data_frame, nrg_bal_codes[1], siec_code)
    frame = left_frame + right_frame
    return frame


def extract_nrg_bal(data, nrg_bal):
    data_frame = data[data["nrg_bal"] == nrg_bal].copy()
    data_frame.drop("nrg_bal", axis=1, inplace=True)
    data_frame.set_index(["id_region", "siec"], inplace=True)
    return data_frame


def extract_nrg_bal_and_siec(data, nrg_bal, siec):
    data_frame = data[data["nrg_bal"] == nrg_bal]
    data_frame = data_frame[data_frame["siec"] == siec].copy()
    data_frame.drop("nrg_bal", axis=1, inplace=True)
    data_frame.drop("siec", axis=1, inplace=True)
    data_frame.set_index(["id_region"], inplace=True)

    includes_nan = data_frame.isna().any().any()
    if includes_nan:
        regions, years = find_nan(data_frame)
        warning = (
            "extraction for nrg_bal ("
            + nrg_bal
            + ") & siec ("
            + siec
            + ") found NaN value(s) at "
            + " years "
            + years
            + " and  regions "
            + regions
        )
        warn(warning)
    return data_frame


def find_nan(data_frame):
    is_region_na = data_frame.isna().any(axis=1)
    regions = str(is_region_na[is_region_na].index.values)

    is_year_na = data_frame.isna().any()
    years = str(is_year_na[is_year_na].index.values)

    return regions, years


def join_parameter(data_frame, database_import, micat_folder):
    mapping_nrg_bal_parameter = database_import.read_mapping_table(
        "mapping__nrg_bal__parameter",
        "nrg_bal",
        "id_parameter",
        micat_folder,
    )

    parameter_data_frame = mapping_nrg_bal_parameter.apply_for(data_frame)
    parameter_data_frame["id_parameter"] = parameter_data_frame["id_parameter"].astype(int)
    return parameter_data_frame


def join_final_energy_carrier(data_frame, database_import, micat_folder):
    mapping_siec_energy_carrier = database_import.read_mapping_table(
        "mapping__siec__energy_carrier",
        "siec",
        "id_final_energy_carrier",
        micat_folder,
    )
    data_frame = mapping_siec_energy_carrier.apply_for(data_frame)
    return data_frame


def join_primary_energy_carrier(data_frame, database_import, micat_folder):
    mapping_siec_energy_carrier = database_import.read_mapping_table(
        "mapping__siec__energy_carrier",
        "siec",
        "id_primary_energy_carrier",
        micat_folder,
    )
    data_frame = mapping_siec_energy_carrier.apply_for(data_frame)
    return data_frame


def join_and_merge_primary_energy_carriers(data_frame, primary_energy_carrier_mapping, year_column_names):
    data_frame.reset_index(inplace=True)
    data_frame = primary_energy_carrier_mapping.apply_for(data_frame)

    data_frame = data_frame[
        (data_frame["id_primary_energy_carrier"] != -99)
        & (data_frame["id_primary_energy_carrier"] != -999)  # -99: redundant entries  # -999: unmapped entries
    ]

    data_frame = data_frame.groupby(["id_region", "id_primary_energy_carrier"])[year_column_names].sum().reset_index()
    return data_frame


def download_relations(relation_url, relation_file_path):
    relation_ref = requests.get(relation_url, allow_redirects=True, timeout=None)
    with open(relation_file_path, "wb") as file:
        file.write(relation_ref.content)


def read_siec_relations(relation_file_path):
    siec_groups_df = pd.read_excel(
        relation_file_path,
        sheet_name="PRODUCTS_TEXT",
        header=None,
        names=["label", "siec_group", "equal", "operator", "siec", "label"],
    )

    siec_relations = {}
    last_group = None
    for _, row in siec_groups_df.iterrows():
        group = row["siec_group"]
        siec = row["siec"].strip()
        if isinstance(group, str):
            last_group = group.strip()
            siec_relations[last_group] = []

        if last_group is None:
            raise NotImplementedError("Entry does not belong to group")

        siec_relations[last_group].append(siec)

    return siec_relations


def download_energy_balance_data(url, zip_file_path):
    zip_file_ref = requests.get(url, allow_redirects=True, timeout=None)
    with open(zip_file_path, "wb") as file:
        file.write(zip_file_ref.content)


def unzip_and_transform_energy_balance_data(zip_file_path, file_path):
    # The format of the tsv files is special because it does not only use tabs
    # as separators but also commas and spaces. Each data column entry can be a pair
    # of a value and a flag, separated by a space. If no flag is present, the entry
    # ends with a space. Also see documentation of the data format at
    # https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=BulkDownload_Guidelines.pdf
    # https://ec.europa.eu/eurostat/data/database/information
    # https://ec.europa.eu/eurostat/statistics-explained/index.php/Tutorial:Symbols_and_abbreviations

    with gzip.open(zip_file_path, "rt", encoding="utf8") as f_in:
        with open(file_path, "wt", encoding="utf8") as f_out:
            for line in f_in:
                new_line = (
                    line.replace(",", "\t")
                    .replace(" \t", "\t")
                    .replace(" ", "")
                    .replace(":z", "NaN")
                    .replace(":", "NaN")
                )
                f_out.write(new_line)


def clean_and_remove_redundant_rows(dataset, df, siec_relations):
    if dataset["filter"].get("unit"):
        df = filter_by_unit(df, dataset["filter"]["unit"])
    df = remove_useless_columns(df)
    df = adapt_order_of_columns(df)
    if dataset["filter"].get("siec"):
        df = remove_redundant_siec_groups(df, siec_relations)
    return df


def filter_by_unit(df, unit):
    df = df[df["unit"] == unit]
    return df


def remove_useless_columns(df):
    del df["unit"]
    return df


def adapt_order_of_columns(df):
    ordered_column_names = list(df.columns[:3]) + list(df.columns[:2:-1])
    df = df[ordered_column_names]
    return df


def remove_redundant_siec_groups(df, siec_relations):
    # removes entries for some siec (="energy carrier") groups and TOTAL
    redundant_siec_groups = determine_redundant_siec_groups(df, siec_relations)
    df = df[~df["siec"].isin(redundant_siec_groups)]
    return df


def determine_redundant_siec_groups(df, siec_relations):
    siecs = list(set(df["siec"].apply(lambda x: x.strip())))
    redundant_groups = set()
    # unfortunately, the entry "FE" is missing in the Excel sheet - documentation
    # but its present in the data
    redundant_groups.add("FE")

    for group in siec_relations.keys():
        if is_redundant_group(group, siecs, siec_relations):
            redundant_groups.add(group)

    return redundant_groups


def is_redundant_group(group, used_siecs, siec_relations):
    siec_entries = siec_relations[group]
    for siec in siec_entries:
        if siec in siec_relations:
            sub_group = siec
            return is_redundant_group(sub_group, used_siecs, siec_relations)
        else:
            is_redundant = siec in used_siecs
            return is_redundant


if __name__ == "__main__":
    main()
