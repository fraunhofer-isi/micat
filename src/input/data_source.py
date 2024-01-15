# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
import pandas as pd

from calculation import extrapolation
from series import annual_series as annual_series_
from table.table import Table
from table.value_table import ValueTable


class DataSource:
    def __init__(
        self,
        database,
        id_region,
        confidential_database,
        measure_specific_parameters=None,
        global_parameters=None,
    ):
        if global_parameters is None:
            global_parameters = {}

        if measure_specific_parameters is None:
            measure_specific_parameters = {}

        self._database = database

        self._id_region = id_region

        self._confidential_database = confidential_database

        self._user_input_measure_tables = DataSource._create_measure_specific_tables(
            measure_specific_parameters,
        )

        self._user_input_global_tables = self._create_global_tables(global_parameters)

    @staticmethod
    def row_table(id_measure, years, value):
        row_entry = {
            'id_measure': int(id_measure),
        }
        for year in years:
            row_entry[str(year)] = value

        row_table = Table([row_entry])
        return row_table

    @staticmethod
    def value_to_annual_series(value, years):
        years_as_str = [str(year) for year in years]
        values = np.full(len(years_as_str), value)
        series_ = pd.Series(values, index=years_as_str)
        _annual_series_ = annual_series_.AnnualSeries(series_)
        return _annual_series_

    @staticmethod
    def _calculated_table_for_measure(  # pylint: disable=too-many-locals
        multi_index,
        savings,
        measure_ids_for_which_extra_data_exists,
        measure_final_parameters,
        measure_parameters,
        measure_constants,
        determine_table_for_measure,
        provide_default_table,
        years,
    ):
        id_measure = multi_index[0]
        id_subsector = multi_index[1]
        id_action_type = multi_index[2]

        if id_measure in measure_ids_for_which_extra_data_exists:
            extrapolated_final_parameters = DataSource._extrapolated_final_parameters(
                measure_final_parameters,
                id_measure,
                years,
            )

            extrapolated_parameters = DataSource._extrapolated_parameters(
                measure_parameters,
                id_measure,
                years,
            )

            constants = DataSource._constants(measure_constants, id_measure)

            table = determine_table_for_measure(
                id_measure,
                id_subsector,
                id_action_type,
                savings,
                extrapolated_final_parameters,
                extrapolated_parameters,
                constants,
            )
            return table
        else:
            default_table = provide_default_table(
                id_measure,
                id_subsector,
                id_action_type,
                savings,
            )
            return default_table

    @staticmethod
    def _extrapolated_final_parameters(measure_final_parameters, id_measure, years):
        if measure_final_parameters is None:
            return None
        else:
            final_parameters = measure_final_parameters.query('id_measure==' + str(id_measure))
            if final_parameters is None:
                message = (
                    'Could not find measure specific final parameter data for id_measure='
                    + str(id_measure)
                    + '. Please check the format of the user data that has been send to the back-end.'
                    + 'If measures include parameter data, all of them need to be filled: '
                    + 'constants, parameters and parameters depending on id_final_energy_carrier.'
                )
                raise ValueError(message)
            extrapolated_final_parameters = extrapolation.extrapolate(final_parameters, years)
            return extrapolated_final_parameters

    @staticmethod
    def _extrapolated_parameters(measure_parameters, id_measure, years):
        if measure_parameters is None:
            return None
        else:
            parameters = measure_parameters.query('id_measure==' + str(id_measure))
            if parameters is None:
                message = (
                    'Could not find measure specific parameter data for id_measure='
                    + str(id_measure)
                    + '. Please check the format of the user data that has been send to the back-end.'
                    + 'If measures include parameter data, all of them need to be filled: '
                    + 'constants, parameters and parameters depending on id_final_energy_carrier.'
                )
                raise ValueError(message)
            extrapolated_parameters = extrapolation.extrapolate(parameters, years)
            return extrapolated_parameters

    @staticmethod
    def _constants(measure_constants, id_measure):
        if measure_constants is None:
            return None
        else:
            constants = measure_constants.query('id_measure==' + str(id_measure))
            return constants

    @staticmethod
    def _create_global_table(json_array, entry):
        raw_table = Table(json_array)

        data_column_names = ['value']
        years = raw_table.years
        if len(years) > 0:
            data_column_names = list(map(str, years))
        else:
            raw_table = ValueTable(json_array)
        table = raw_table[data_column_names]  # removes extra, optional value columns

        if 'normalization_column_names' in entry:
            normalization_column_names = entry['normalization_column_names']
            table = table.normalize(normalization_column_names)

        id_parameter = entry['id_parameter']
        table = table.insert_index_column(
            'id_parameter',
            0,
            id_parameter,
        )

        if 'id_technology' in entry:
            id_technology = entry['id_technology']
            table = table.insert_index_column(
                'id_technology',
                1,
                id_technology,
            )

        table = table[data_column_names]  # removes extra, optional column 'index'

        return table

    @staticmethod
    def _create_measure_specific_tables(measure_specific_parameters):
        tables = {}
        if measure_specific_parameters != {}:
            for id_measure, json_data in measure_specific_parameters.items():
                tables = DataSource._fill_measure_specific_tables(tables, id_measure, json_data)
        return tables

    @staticmethod
    def _fill_measure_specific_tables(tables, id_measure, json_data):
        for data_name, data_array in json_data.items():
            if len(data_array) > 0:
                entries = DataSource._map_measure_specific_parameter_tables(data_name)
                for entry in entries:
                    table_name = entry['table_name']
                    table_type = entry['table_type']
                    if table_type == 'ValueTable':
                        table = ValueTable(data_array)
                    else:
                        table = Table(data_array)

                    table = table.insert_index_column('id_measure', 0, int(id_measure))

                    if table_name in tables:
                        existing_table = tables[table_name]
                        if table_type == 'ValueTable':
                            table = ValueTable.concat([existing_table, table])
                        else:
                            table = Table.concat([existing_table, table])

                    tables[table_name] = table
        return tables

    @staticmethod
    def _extrapolated_parameter_table(
        parameter_table,
        id_measure,
        id_subsector,
        id_action_type,
        years=None,
    ):
        table = parameter_table.query('id_measure==' + str(id_measure))
        if years is not None:
            table = extrapolation.extrapolate(table, years)
        table = table.insert_index_column('id_subsector', 1, id_subsector)
        table = table.insert_index_column('id_action_type', 2, id_action_type)
        return table

    @staticmethod
    def _loop_over_measures_and_collect_parameters(
        final_energy_saving_by_action_type,
        measure_ids_for_which_extra_data_exists,
        parameter_table,
        provide_default_value,
        is_value_table=False,
    ):
        if is_value_table:
            years = None
        else:
            years = final_energy_saving_by_action_type.years

        measure_tables = []
        for measure_multi_index, savings in final_energy_saving_by_action_type.iterrows():
            measure_table = DataSource._table_for_measure(
                measure_multi_index,
                savings,
                measure_ids_for_which_extra_data_exists,
                parameter_table,
                provide_default_value,
                years,
            )
            measure_tables.append(measure_table)
        measure_specific_table = Table.concat(measure_tables)
        measure_specific_table = measure_specific_table.sort()

        _id_column_names, _year_column_names, value_column_names = measure_specific_table.column_names
        if 'value' in value_column_names:
            return ValueTable.from_table(measure_specific_table)
        else:
            return measure_specific_table

    # pylint: disable=too-many-locals
    @staticmethod
    def _loop_over_measures_and_collect_tables(
        final_energy_saving_by_action_type,
        measure_ids_for_which_extra_data_exists,
        measure_final_parameters,
        measure_parameters,
        measure_constants,
        determine_table_for_measure,
        provide_default_table,
    ):
        years = final_energy_saving_by_action_type.years
        measure_tables = []
        for measure_multi_index, savings in final_energy_saving_by_action_type.iterrows():
            measure_table = DataSource._calculated_table_for_measure(
                measure_multi_index,
                savings,
                measure_ids_for_which_extra_data_exists,
                measure_final_parameters,
                measure_parameters,
                measure_constants,
                determine_table_for_measure,
                provide_default_table,
                years,
            )
            measure_tables.append(measure_table)
        measure_specific_table = Table.concat(measure_tables)
        measure_specific_table = measure_specific_table.sort()

        _id_column_names, _year_column_names, value_column_names = measure_specific_table.column_names
        if 'value' in value_column_names:
            return ValueTable.from_table(measure_specific_table)
        else:
            return measure_specific_table

    @staticmethod
    def _map_measure_specific_parameter_tables(data_name):
        mapping = {
            'parameters': [{'table_name': 'measure_parameters', 'table_type': 'Table'}],
            'finalParameters': [{'table_name': 'measure_final_parameters', 'table_type': 'Table'}],
            'constants': [{'table_name': 'measure_constants', 'table_type': 'ValueTable'}],
        }
        if data_name not in mapping:
            message = 'Parameter data name "' + data_name + '" is not yet implemented!'
            raise KeyError(message)
        return mapping[data_name]

    @staticmethod
    def _map_global_parameter_tables(sheet_name):
        mapping = {  # sheet_name => (table_name, id_parameter)
            'FuelSplitCoefficient': [
                {
                    'table_name': 'eurostat_final_sector_parameters',
                    'id_parameter': 11,
                },
                {
                    'table_name': 'primes_final_sector_parameters',
                    'id_parameter': 11,
                },
            ],
            'EnergyPrice': [  # TO DO #233
                {
                    'table_name': 'error',
                    'id_parameter': -999,
                }
            ],
            'HeatGeneration': [
                {
                    'table_name': 'eurostat_primary_parameters',
                    'id_parameter': 20,
                    'normalization_column_names': [],
                }
            ],
            'ElectricityGeneration': [
                {
                    'table_name': 'eurostat_primary_parameters',
                    'id_parameter': 21,
                    'normalization_column_names': [],
                }
            ],
            'MonetisationFactors': [
                {
                    'mapping': {
                        'key_column_name': 'Monetisation factor',
                        'entries': {
                            'Value of statistical life [€]': [
                                {
                                    'table_name': 'who_parameters',
                                    'id_parameter': 37,
                                }
                            ],
                            'Value of a life year [€]': [
                                {
                                    'table_name': 'who_parameters',
                                    'id_parameter': 56,
                                }
                            ],
                            'Value of a lost work day [€]': [
                                {
                                    'table_name': 'iiasa_lost_working_days_monetization_factors',
                                    'id_parameter': 19,
                                }
                            ],
                            'Cost per ton of emitted CO2 [€/tCO2]': [
                                {
                                    'table_name': 'iiasa_greenhouse_gas_emission_monetization_factors',
                                    'id_parameter': 42,
                                }
                            ],
                            'Cost of statistical transfer of RES [€/ktoe]': [
                                {
                                    'table_name': 'fraunhofer_constant_parameters',
                                    'id_parameter': 61,
                                    'column_names': ['Value'],
                                }
                            ],
                            'Investment costs of PV [€/MWh]': [
                                {
                                    'table_name': 'irena_technology_parameters',
                                    'id_parameter': 4,
                                    'id_technology': 3,
                                    'column_names': ['Value'],
                                }
                            ],
                            'Investment costs of onshore wind [€/MWh]': [
                                {
                                    'table_name': 'irena_technology_parameters',
                                    'id_parameter': 44,
                                    'id_technology': 1,
                                    'column_names': ['Value'],
                                }
                            ],
                            'Investment costs of offshore wind [€/MWh]': [
                                {
                                    'table_name': 'irena_technology_parameters',
                                    'id_parameter': 37,
                                    'id_technology': 2,
                                    'column_names': ['Value'],
                                }
                            ],
                        },
                    }
                }
            ],
        }
        if sheet_name not in mapping:
            message = 'Parameter sheet "' + sheet_name + '" is not yet implemented!'
            raise KeyError(message)
        return mapping[sheet_name]

    @staticmethod
    def _parameter_query_from_where_clause(where_clause):
        constraints = []
        for key, value in where_clause.items():
            if key == 'id_region':
                continue

            if isinstance(value, str):
                constraint = key + ' == ' + value
            else:
                constraint = key + ' in ' + str(value)
            constraints.append(constraint)
        query = ' and '.join(constraints)
        return query

    @staticmethod
    def _provide_default_table(
        provide_default,
        id_measure,
        id_subsector,
        id_action_type,
        savings,
        years=None,
    ):
        entry = {
            'id_measure': id_measure,
            'id_subsector': id_subsector,
            'id_action_type': id_action_type,
        }
        if years is None:
            entry['value'] = provide_default(id_measure, id_subsector, id_action_type, savings)
            default_table = ValueTable([entry])
        else:
            for year in years:
                year_string = str(year)
                saving = savings[year_string]
                value = provide_default(id_measure, id_subsector, id_action_type, year, saving)
                entry[year_string] = value
            default_table = Table([entry])
        return default_table

    @staticmethod
    def _query_table(table_name, where_clause, tables):
        table = tables[table_name]
        if where_clause:
            query = DataSource._parameter_query_from_where_clause(where_clause)
            if query:
                filtered_table = table.query(query)
                return filtered_table
            else:
                return table
        else:
            return table

    @staticmethod
    def _row_to_json_array(row, key_column_name):
        data = row.copy()
        del data[key_column_name]
        if 'index' in data:
            del data['index']
        if 'Value' in data:
            data['value'] = data['Value']
            del data['Value']
        json_array = [data]
        return json_array

    @staticmethod
    def _table_for_measure(
        multi_index,
        savings,
        measure_ids_for_which_extra_data_exists,
        parameter_table,
        provide_default_value,
        years=None,
    ):
        id_measure = multi_index[0]
        id_subsector = multi_index[1]
        id_action_type = multi_index[2]

        if id_measure in measure_ids_for_which_extra_data_exists:
            table = DataSource._extrapolated_parameter_table(
                parameter_table,
                id_measure,
                id_subsector,
                id_action_type,
                years,
            )
            return table
        else:
            default_table = DataSource._provide_default_table(
                provide_default_value,
                id_measure,
                id_subsector,
                id_action_type,
                savings,
                years,
            )

            return default_table

    @staticmethod
    def _measure_ids_for_which_extra_data_exists(
        measure_final_parameters,
        measure_parameters,
        measure_constants,
    ):
        id_values = set()
        if measure_final_parameters is not None:
            id_values_final_parameters = measure_final_parameters.unique_index_values('id_measure')
            id_values.update(id_values_final_parameters)

        if measure_parameters is not None:
            id_values_parameters = measure_parameters.unique_index_values('id_measure')
            id_values.update(id_values_parameters)

        if measure_constants is not None:
            id_values_constants = measure_constants.unique_index_values('id_measure')
            id_values.update(id_values_constants)

        return list(id_values)

    def annual_parameters_per_measure(
        self,
        final_energy_saving_by_action_type,
        parameter_table_name,
        id_parameter,
        provide_default_parameter,
        id_region=None,
    ):
        years = final_energy_saving_by_action_type.years
        default_parameters_table = self._default_annual_parameters(parameter_table_name, id_parameter, years)

        def _provide_default_parameter(id_measure, id_subsector, id_action_type, year, saving):
            value = provide_default_parameter(
                id_region,
                id_parameter,
                id_measure,
                id_subsector,
                id_action_type,
                year,
                saving,
                default_parameters_table,
            )
            return value

        measure_specific_parameters = self.measure_specific_parameter(
            final_energy_saving_by_action_type,
            id_parameter,
            _provide_default_parameter,
        )

        return measure_specific_parameters

    def annual_series(self, table_name, where_clause=None):
        # used for cases where the query result contains only a single row and no id columns but
        # only annual values
        single_row_table = self.table(table_name, where_clause)
        annual_series = annual_series_.AnnualSeries(single_row_table)
        return annual_series

    def extrapolated_annual_series(self, table_name, years, where_clause=None):
        _annual_series_ = self.annual_series(table_name, where_clause)
        extrapolated_annual_series = extrapolation.extrapolate_series(_annual_series_, years)
        return extrapolated_annual_series

    def annual_series_from_value(self, value_table_name, years, where_clause):
        value_table = self.table(value_table_name, where_clause)
        if value_table.values.shape != (1, 1):
            raise ValueError('Too many values to create an annual series. Please check your where clause.')
        _annual_series_ = DataSource.value_to_annual_series(value_table.values[0][0], years)
        return _annual_series_

    def id_table(self, table_name):
        return self._database.id_table(table_name)

    def mapping_table(self, table_name):
        return self._database.mapping_table(table_name)

    def measure_specific_calculation(
        self,
        final_energy_saving_by_action_type,
        determine_table_for_measure,
        provide_default_table,  # has to use the same format (=id columns, years) as determine_table_for_measure
    ):
        # This function allows to calculate values that depend on multiple parameters and even
        # use different workflows depending on id_subsector and id_action_type.
        #
        # If you would like to query a single parameter, use the function
        # measure_specific_parameter
        # instead.

        measure_final_parameters = self.table('measure_final_parameters')
        measure_parameters = self.table('measure_parameters')
        measure_constants = self.table('measure_constants')
        has_no_measure_specific_parameters = (
            measure_final_parameters is None and measure_parameters is None and measure_constants is None
        )
        if has_no_measure_specific_parameters:
            # No measure specific data has been specified by users
            measure_specific_table = DataSource._loop_over_measures_and_collect_tables(
                final_energy_saving_by_action_type,
                [],
                None,
                None,
                None,
                determine_table_for_measure,
                provide_default_table,
            )
            return measure_specific_table
        else:
            # Some measure specific data has been specified by users
            measure_ids_for_which_extra_data_exists = self._measure_ids_for_which_extra_data_exists(
                measure_final_parameters,
                measure_parameters,
                measure_constants,
            )

            measure_specific_table = DataSource._loop_over_measures_and_collect_tables(
                final_energy_saving_by_action_type,
                measure_ids_for_which_extra_data_exists,
                measure_final_parameters,
                measure_parameters,
                measure_constants,
                determine_table_for_measure,
                provide_default_table,
            )
            return measure_specific_table

    def measure_specific_parameter(
        self,
        final_energy_saving_by_action_type,
        id_parameter,
        # the following argument is a function that returns a single column value for a given set of
        # id_measure, id_subsector, id_action_type, year, saving:
        provide_default_value,
        is_value_table=False,
    ):
        # Currently, this function uses parameters that do not depend on id_final_energy_carrier.
        # id_subsector etc. If that changes, we also need to read corresponding tables
        # 'measure_final_parameters' etc.

        annual_table = self.table('measure_parameters', {'id_parameter': str(id_parameter)})
        constant_table = self.table('measure_constants', {'id_parameter': str(id_parameter)})
        if annual_table is None and constant_table is None:
            # No measure specific data is available
            measure_specific_table = DataSource._loop_over_measures_and_collect_parameters(
                final_energy_saving_by_action_type,
                [],
                None,
                provide_default_value,
                is_value_table,
            )
            return measure_specific_table
        else:
            if constant_table is None:
                parameter_table = annual_table.reduce('id_parameter', [id_parameter])
            else:
                parameter_table = constant_table.reduce('id_parameter', [id_parameter])
            del parameter_table['id_parameter']

            if parameter_table.has_index_column('id_measure'):
                # Measure specific data has been specified by users
                measure_ids_for_which_extra_data_exists = parameter_table.unique_index_values('id_measure')
                measure_specific_table = DataSource._loop_over_measures_and_collect_parameters(
                    final_energy_saving_by_action_type,
                    measure_ids_for_which_extra_data_exists,
                    parameter_table,
                    provide_default_value,
                    is_value_table,
                )
                return measure_specific_table
            else:
                # Fallback data has been specified in one of the sqlite databases
                # A case where we provide fallback values for measure specific parameters (e.g. using
                # tables 'measure_parameters' and 'measure_final_parameters') from the sqlite database
                # has not been implemented, yet.
                # In that case it would not make sense to include id_measure in the database tables. The
                # fallback values might be the same for all measures or could be mapped using
                # id_subsector and id_action_type.
                raise ValueError('Not yet implemented')

    def measure_specific_parameter_using_default_table(
        self,
        final_energy_saving_by_action_type,
        id_parameter,
        parameter_default_values,
    ):
        years = final_energy_saving_by_action_type.years
        default_values = parameter_default_values.reduce('id_parameter', id_parameter)
        extrapolated_default_values = extrapolation.extrapolate_series(default_values, years)

        def provide_default_value(_id_measure, _id_subsector, _id_action_type, year, _saving):
            default_value = extrapolated_default_values[str(year)]
            return default_value

        measure_specific_parameter = self.measure_specific_parameter(
            final_energy_saving_by_action_type,
            id_parameter,
            provide_default_value,
        )
        return measure_specific_parameter

    def parameter(
        self,
        table_name,
        id_region,
        id_parameter,
        years=None,
    ):
        where_clause = {}
        if id_region is not None:
            where_clause['id_region'] = str(id_region)
        parameter_table = self.table(table_name, where_clause)
        raw_parameter = parameter_table.reduce('id_parameter', id_parameter)

        if isinstance(raw_parameter, ValueTable):
            return raw_parameter

        if years is None:
            message = 'Please specify the years if you want to query an annual parameter table.'
            raise AttributeError(message)

        parameter = extrapolation.extrapolate(raw_parameter, years)
        return parameter

    def table(self, table_name, where_clause=None):
        if where_clause is None:
            # Also see
            # https://stackoverflow.com/questions/26320899/why-is-the-empty-dictionary-a-dangerous-default-value-in-python
            where_clause = {}

        if table_name in self._user_input_measure_tables:
            table = self._query_table(table_name, where_clause, self._user_input_measure_tables)
            return table
        elif table_name in self._user_input_global_tables:
            table = self._query_table(table_name, where_clause, self._user_input_global_tables)
            return table
        else:
            table = self._table_from_database(table_name, where_clause)
            return table

    def _add_global_tables_from_mapping(
        self,
        tables,
        json_entry,
        entry,
    ):
        mapping = entry['mapping']
        key_column_name = mapping['key_column_name']
        entries = mapping['entries']
        for row in json_entry:
            key = row[key_column_name]
            mapping_entries = entries[key]
            json_array = DataSource._row_to_json_array(row, key_column_name)
            for mapping_entry in mapping_entries:
                tables = self._add_table_entry(tables, json_array, mapping_entry)
        return tables

    def _add_table_entry(
        self,
        tables,
        json_entry,
        entry,
    ):
        table_name = entry['table_name']
        if table_name == 'error':
            print("Not yet implemented")
            return tables

        if table_name not in tables:
            table = self._read_default_table(table_name, entry)
            tables[table_name] = table

        parameter_table = DataSource._create_global_table(json_entry, entry)

        table = tables[table_name]
        updated_table = table.update(parameter_table)
        tables[table_name] = updated_table

        return tables

    def _read_default_table(self, table_name, entry):
        table = self._table_from_database(table_name, {})
        if table is None:
            raise KeyError('Could not find table ' + table_name)
        id_column_names, _, _ = table.column_names

        if 'id_parameter' not in id_column_names:
            raise KeyError('Database table ' + table_name + ' does not include id_parameter.')

        if 'id_technology' in entry:
            if 'id_technology' not in id_column_names:
                raise KeyError('Database table ' + table_name + ' does not include id_technology.')

        if 'id_region' in id_column_names:
            table = table.reduce('id_region', [self._id_region])
            del table['id_region']

        return table

    def _create_global_tables(self, global_parameters):
        tables = {}
        for sheet_name, json_entry in global_parameters.items():
            if len(json_entry) > 0:
                entries = DataSource._map_global_parameter_tables(sheet_name)
                for entry in entries:
                    if 'mapping' in entry:
                        tables = self._add_global_tables_from_mapping(
                            tables,
                            json_entry,
                            entry,
                        )
                    else:
                        tables = self._add_table_entry(
                            tables,
                            json_entry,
                            entry,
                        )
        return tables

    def _table_from_database(self, table_name, where_clause):
        try:
            table = self._database.table(table_name, where_clause)
            return table
        except IOError:
            if self._confidential_database is None:
                return None
            else:
                try:
                    table = self._confidential_database.table(table_name, where_clause)
                    return table
                except IOError:
                    # This case is for example relevant, if a table for "measure specific parameters"
                    # (e.g. 'measure_parameters') is not present in self._user_input_tables because
                    # no measure specific parameters have been uploaded by the user for any measure.
                    return None

    def _default_annual_parameters(self, parameter_table_name, id_parameter, years):
        where_clause = {'id_parameter': str(id_parameter)}
        raw_default_parameters = self.table(parameter_table_name, where_clause)
        default_parameters = extrapolation.extrapolate(raw_default_parameters, years)
        return default_parameters
