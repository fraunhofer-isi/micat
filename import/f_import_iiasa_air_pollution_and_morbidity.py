# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
import warnings

import pandas as pd
from config import import_config

from data_import import conversion_energy
from data_import.database_import import DatabaseImport
from input.database import Database
from table.table import Table


def main():  # pylint: disable=too-many-locals
    public_database_path, raw_data_path = import_config.get_paths()

    database = Database(public_database_path)
    database_import = DatabaseImport(public_database_path)

    import_folder = raw_data_path + '/iiasa'

    id_region_table = database.id_table('id_region')
    id_parameter_table = database.id_table('id_parameter')
    id_subsector_table = database.id_table('id_subsector')
    id_final_energy_carrier_table = database.id_table('id_final_energy_carrier')

    print('Reading input files...')

    # air pollution factors are specified in kt/PJ
    raw_air_pollution_factor = pd.read_excel(import_folder + '/air_pollutant.xlsx', engine='openpyxl')

    _warn_for_dummy_values(raw_air_pollution_factor, 'air_pollution')

    # morbidity factors are specified in 1/PJ
    raw_morbidity_factor = pd.read_excel(import_folder + '/morbidity.xlsx', engine='openpyxl')

    _warn_for_dummy_values(raw_morbidity_factor, 'morbidity')

    column_mapping = {
        'LABEL_REGION': 'id_region',
        'YEAR': 'year',
        'MICAT_SECTOR': 'id_subsector',
        'MICAT_FUEL': 'id_final_energy_carrier',
        'Parameter': 'id_parameter',
        'FACTOR': 'value',
    }

    pj_to_ktoe = conversion_energy.conversion_coefficient('PJ', 'ktoe')

    print('Translating iiasa air pollution data...')

    air_pollution_factor_in_kt_per_pj, missing_entries = _translate_iiasa_table(
        raw_air_pollution_factor,
        id_region_table,
        id_parameter_table,
        id_subsector_table,
        id_final_energy_carrier_table,
    )

    air_pollution_factor_in_kt_per_ktoe = air_pollution_factor_in_kt_per_pj * 1 / pj_to_ktoe

    print('Including air pollution data for europe...')
    air_pollution_factor_with_europe = _add_europe_data(air_pollution_factor_in_kt_per_ktoe)

    print('Validating data...')
    missing_entries = database_import.validate_table(air_pollution_factor_with_europe, missing_entries)
    years = _extract_years(raw_air_pollution_factor)
    exclusions = {'id_region': 0}  # we exclude european values because they are calculated
    dummy_value_for_missing_entries = -999

    if len(missing_entries) > 0:
        print('Writing missing entries...')
        database_import.write_missing_entries_as_excel_file(
            'missing_entries_air_pollution.xlsx',
            missing_entries,
            column_mapping,
            years,
            dummy_value_for_missing_entries,
            exclusions,
        )

    print('Translating iiasa morbidity data...')
    morbidity_factor, missing_entries = _translate_iiasa_table(
        raw_morbidity_factor,
        id_region_table,
        id_parameter_table,
        id_subsector_table,
        id_final_energy_carrier_table,
    )

    morbidity_factor_in_1_over_ktoe = morbidity_factor * 1 / pj_to_ktoe

    print('Including morbidity data for europe...')
    morbidity_factor_with_europe = _add_europe_data(morbidity_factor_in_1_over_ktoe)

    print('Validating data...')
    missing_entries = database_import.validate_table(morbidity_factor_with_europe, missing_entries)
    years = _extract_years(raw_morbidity_factor)

    if len(missing_entries) > 0:
        print('Writing missing entries...')
        database_import.write_missing_entries_as_excel_file(
            'missing_entries_morbidity.xlsx',
            missing_entries,
            column_mapping,
            years,
            dummy_value_for_missing_entries,
            exclusions,
        )

    factors = Table.concat([air_pollution_factor_with_europe, morbidity_factor_with_europe])

    print('Writing data to sqlite...')
    database_import.write_to_sqlite(factors, 'iiasa_final_subsector_parameters')

    print('Finished!')


def _warn_for_dummy_values(data_frame, label):
    dummy_value = -0.00001
    number_of_dummy_values = data_frame['FACTOR'].value_counts()[dummy_value]
    if number_of_dummy_values > 0:
        message = label + ' includes ' + str(number_of_dummy_values) + ' dummy values (' + str(dummy_value) + ')!'
        warnings.warn(message)


def _extract_years(df):
    years = list(set(df['YEAR']))
    years.sort()
    return years


def _add_europe_data(factors):
    id_columns = ['id_parameter', 'id_subsector', 'id_final_energy_carrier']
    europe_data = factors.aggregate_by_mean_to(id_columns)
    # note: if you want to change the default value of 0, be aware of the different units
    europe_data = europe_data.insert_index_column('id_region', 0, 0)
    extended_factors = Table.concat([factors, europe_data])
    return extended_factors


def _translate_iiasa_table(
    df,
    id_region_table,
    id_parameter_table,
    id_subsector_table,
    id_final_energy_carrier_table,
):
    df['YEAR'] = df['YEAR'].astype(str)

    translated_df = id_region_table.label_to_id(df, 'LABEL_REGION')
    translated_df = id_parameter_table.label_to_id(translated_df, 'Parameter')
    translated_df = id_subsector_table.label_to_id(translated_df, 'MICAT_SECTOR')
    translated_df = id_final_energy_carrier_table.label_to_id(translated_df, 'MICAT_FUEL')

    contains_nan_values = translated_df.isna().any().any()
    if contains_nan_values:
        raise ValueError('Data contains rows with missing values')

    result = translated_df.pivot_table(
        values='FACTOR',
        index=['id_region', 'id_parameter', 'id_subsector', 'id_final_energy_carrier'],
        columns='YEAR',
    )

    missing_entries = []
    contains_nan_values = result.isna().any().any()
    if contains_nan_values:
        message = "Missing data: transposed table would contain nan values:"
        warnings.warn(message)

        rows_including_na = result[result.isna().any(axis=1)]
        print(rows_including_na)
        missing_entries = _missing_entries_from_ids(
            rows_including_na,
            id_region_table,
            id_parameter_table,
            id_subsector_table,
            id_final_energy_carrier_table,
        )

        result = result[~result.isna().any(axis=1)]

    table = Table(result)

    return table, missing_entries


def _missing_entries_from_ids(
    df,
    id_region_table,
    id_parameter_table,
    id_subsector_table,
    id_final_energy_carrier_table,
):
    missing_entries = []
    years = list(df.columns)
    unindexed_df = df.reset_index()
    for _, df_row in unindexed_df.iterrows():
        for year in years:
            if math.isnan(df_row[year]):
                missing_entry = _create_missing_entry(
                    df_row,
                    year,
                    id_region_table,
                    id_parameter_table,
                    id_subsector_table,
                    id_final_energy_carrier_table,
                )
                missing_entries.append(missing_entry)

    return missing_entries


def _create_missing_entry(  # pylint: disable=too-many-arguments
    df_row,
    year,
    id_region_table,
    id_parameter_table,
    id_subsector_table,
    id_final_energy_carrier_table,
):
    entry = {'year': year}

    id_region = int(df_row['id_region'])
    region_label = id_region_table.label(id_region)
    entry['id_region'] = (id_region, region_label)

    id_parameter = int(df_row['id_parameter'])
    parameter_label = id_parameter_table.label(id_parameter)
    entry['id_parameter'] = (id_parameter, parameter_label)

    id_subsector = int(df_row['id_subsector'])
    subsector_label = id_subsector_table.label(id_subsector)
    entry['id_subsector'] = (id_subsector, subsector_label)

    id_final_energy_carrier = int(df_row['id_final_energy_carrier'])
    final_energy_carrier_label = id_final_energy_carrier_table.label(id_final_energy_carrier)
    entry['id_final_energy_carrier'] = (id_final_energy_carrier, final_energy_carrier_label)

    return entry


if __name__ == '__main__':
    main()