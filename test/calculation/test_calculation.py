# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import os

from test_utils.mock import Mock, patch, patch_property, raises

from calculation import calculation
from calculation.ecologic import calculation_ecologic, energy_saving
from calculation.economic import calculation_economic, eurostat, population
from calculation.social import calculation_social
from series.annual_series import AnnualSeries
from table.id_table import IdTable
from table.table import Table


def determine_database_path():
    file_path = os.path.abspath(__file__)
    calculation_path = os.path.dirname(file_path)
    test_path = os.path.dirname(calculation_path)
    back_end_path = os.path.dirname(test_path)
    sqlite_path = back_end_path + '/data/public.sqlite'
    return sqlite_path


database_path = determine_database_path()


def mocked_savings():
    savings = Table(
        [
            {'id_measure': 1, 'id_subsector': 3, 'id_action_type': 8, '2020': 5000, '2025': 4000, '2030': 3000},
            {'id_measure': 2, 'id_subsector': 3, 'id_action_type': 11, '2020': 10000, '2025': 9000, '2030': 8000},
        ]
    )
    return savings


def mocked_primary_energy_savings():
    savings = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 3,
                'id_action_type': 8,
                'id_primary_energy_carrier': 1,
                '2020': 5000,
                '2025': 4000,
                '2030': 3000,
            },
        ]
    )
    return savings


def mocked_parameters():
    parameters = {}
    return parameters


def mocked_table():
    mock = Mock()
    mock.reduce = Mock('mocked_table')
    mock.join_id_column = Mock(Mock())
    mock.transpose = Mock('mocked_transposed_table')
    return mock


def mocked_front_end_arguments():
    return {
        'id_mode': 1,
        'id_region': 1,
        'final_energy_saving_by_action_type': mocked_savings(),
        'measure_specific_parameters': mocked_parameters(),
        'parameters': mocked_parameters(),
        'population_of_municipality': 'mocked_population',
    }


class TestPublicApi:
    # <editor-fold desc="Fold @patch">
    @patch(print)
    @patch(
        calculation._front_end_arguments,
        mocked_front_end_arguments(),
    )
    @patch_property(
        Table.years,
        [2020, 2025, 2030],
    )
    @patch(
        calculation._interim_data,
        'mocked_interim_data',
    )
    @patch(
        calculation_social.social_indicators,
        {'mocked_social_indicator': 'foo'},
    )
    @patch(
        calculation_economic.economic_indicators,
        {'mocked_economic_indicator': 'baa'},
    )
    @patch(
        calculation_ecologic.ecologic_indicators,
        {'mocked_ecologic_indicator': 'qux'},
    )
    @patch(
        calculation.cost_benefit_analysis.parameters,
        {'mocked_lifetime': 'qux'},
    )
    @patch(
        calculation._translate_result_tables,
        'mocked_translated_result_table',
    )
    @patch(
        calculation._convert_result_tables_to_json,
        'mocked_result',
    )
    @patch(calculation._validate_data)
    # </editor-fold>
    def test_calculate_indicator_data(self, _mocked_year_property):
        http_request_mock = 'request_mock'
        result = calculation.calculate_indicator_data(
            http_request_mock,
            'mocked_database',
            'mocked_confidential_database',
        )

        assert result == 'mocked_result'


class TestPrivateApi:
    @patch(
        Table.unique_multi_index_tuples,
        Mock([(1, 3, 8)]),
    )
    def test_add_renewables_and_other(self):
        primary_savings = mocked_primary_energy_savings()
        result = calculation._add_renewables_and_other(primary_savings)
        assert result['2020'][1, 3, 8, 5] == 0
        assert result['2020'][1, 3, 8, 6] == 0

    @patch(
        calculation._mapping_from_final_to_primary_energy_carrier,
        Mock(),
    )
    @patch(
        calculation._add_renewables_and_other,
        Mock('mocked_result'),
    )
    def test_additional_primary_energy_saving(self):
        mocked_energy_saving_by_final_energy_carrier = Mock()
        mocked_energy_saving_by_final_energy_carrier.map_id_column = Mock()

        result = calculation._additional_primary_energy_saving(
            mocked_energy_saving_by_final_energy_carrier,
            'mocked_data_source',
        )
        assert result == 'mocked_result'

    class TestCheckRequestParameters:
        def test_without_id_mode(self):
            mocked_query_parameters = {
                'id_region': '1',
                'id_wrong_id': '1',
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_id_mode_as_none(self):
            mocked_query_parameters = {
                'id_mode': None,
                'id_region': '1',
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_id_mode_as_undefined(self):
            mocked_query_parameters = {
                'id_mode': 'undefined',
                'id_region': '1',
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_without_id_region(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_wrong_id': '1',
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_id_region_as_none(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': None,
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_id_region_as_undefined(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': 'undefined',
                'savings': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_without_savings(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': '1',
                'wrong_parameter': 'mocked_savings',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_savings_as_none(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': '1',
                'savings': None,
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_savings_as_undefined(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': '1',
                'savings': 'undefined',
            }
            with raises(AttributeError):
                calculation._check_request_parameters(mocked_query_parameters)

        def test_with_all_parameters(self):
            mocked_query_parameters = {
                'id_mode': '1',
                'id_region': '1',
                'savings': 'mocked_savings',
            }
            calculation._check_request_parameters(mocked_query_parameters)

    @patch(
        calculation._add_renewables_and_other,
        Mock('mocked_result'),
    )
    def test_convert_result_tables_to_json(self):
        mocked_result_table = Mock()
        mocked_result_table.to_custom_json = Mock('mocked_json')
        mocked_tables = {'mocked_table_name': mocked_result_table}
        result = calculation._convert_result_tables_to_json(mocked_tables)
        assert result['mocked_table_name'] == 'mocked_json'

    def test_extract_details_from_measures(self):
        measures = [
            {
                'id_measure': 1,
                'id_subsector': 2,
                'details': {'foo': 'baa'},
            },
        ]
        details, measures_without_detail = calculation._extract_details_from_measures(measures)
        first_detail = details[1]
        assert first_detail['foo'] == 'baa'

        first_measure = measures_without_detail[0]
        assert first_measure['id_measure'] == 1
        assert first_measure['id_subsector'] == 2
        assert 'details' not in first_measure

    @patch(
        calculation._check_request_parameters,
        Mock(None),
    )
    @patch(
        calculation._extract_details_from_measures,
        Mock(
            (
                'mocked_measure_specific_parameters',
                [{'id_measure': 1, 'id_subsector': 3, 'id_action_type': 8, '2020': 1, '2025': 0, '2030': 0}],
            ),
        ),
    )
    @patch(population.population_of_municipality)
    class TestFrontEndArguments:
        @staticmethod
        def mocked_query_parameters():
            return {
                'id_mode': '1',
                'id_region': '1',
                'savings': '[{"2020":0,"2025":0,"2030":0,"id_measure":1,"id_subsector":3,"id_action_type":8}]',
                'json': {'parameters': 'undefined'},
            }

        @staticmethod
        def mocked_query_parameters_including_parameters():
            return {
                'id_mode': '1',
                'id_region': '1',
                'savings': '[{"2020":0,"2025":0,"2030":0,"id_measure":1,"id_subsector":3,"id_action_type":8}]',
                'json': {'parameters': 'mocked_parameters'},
            }

        @patch(
            calculation._parse_request,
            Mock(mocked_query_parameters()),
        )
        def test_without_parameters(self):
            arguments = calculation._front_end_arguments(
                'mocked_http_request',
            )

            assert arguments['id_mode'] == 1
            assert arguments['id_region'] == 1

            final_energy_savings = arguments['final_energy_saving_by_action_type']
            first_value = final_energy_savings['2020'][1, 3, 8]
            assert first_value == 1
            assert arguments['parameters'] == 'undefined'

        @patch(
            calculation._parse_request,
            Mock(mocked_query_parameters_including_parameters()),
        )
        def test_with_parameters(self):
            arguments = calculation._front_end_arguments(
                {'json': {}},
            )
            assert arguments['parameters'] == 'mocked_parameters'

    @patch(
        eurostat.primary_parameters,
        Mock(),
    )
    @patch(
        energy_saving.energy_saving_by_final_energy_carrier,
        Mock(),
    )
    @patch(
        calculation._mocked_h2,
        Mock(),
    )
    @patch(
        calculation.conversion.primary_energy_saving,
        Mock(),
    )
    @patch(
        calculation._additional_primary_energy_saving,
        Mock(),
    )
    @patch(
        calculation.conversion.total_primary_energy_saving,
        Mock(),
    )
    @patch(
        calculation.air_pollution.subsector_parameters,
        Mock(),
    )
    @patch(
        calculation.energy_cost.reduction_of_energy_cost,
        Mock(),
    )
    def test_interim_data(self):
        mocked_final_energy_saving_by_action_type = Mock()

        result = calculation._interim_data(
            mocked_final_energy_saving_by_action_type,
            'mocked_data_source',
            'mocked_id_mode',
            'mocked_id_region',
            'mocked_years',
        )
        assert len(result) == 6

    def test_mapping_from_final_to_primary_energy_carrier(self):
        database = Mock()
        database.mapping_table = Mock('mocked_result')
        result = calculation._mapping_from_final_to_primary_energy_carrier(database)
        assert result == 'mocked_result'

    def test_mocked_h2(self):
        result = calculation._mocked_h2()
        assert result is not None

    class TestParseRequest:
        def test_parse_request_with_json(self):
            http_request_mock = Mock()
            http_request_mock.query_string = Mock()
            http_request_mock.query_string.decode = Mock('a=1&b=[10,20]')
            http_request_mock.content_type = 'application/json'
            http_request_mock.json = {
                'measures': [
                    {'savings': []},
                ],
            }
            result = calculation._parse_request(http_request_mock)
            assert result['a'] == '1'
            assert result['b'] == '[10,20]'

        def test_parse_request_without_measure(self):
            http_request_mock = Mock()
            http_request_mock.query_string = Mock()
            http_request_mock.query_string.decode = Mock('a=1&b=[10,20]')
            http_request_mock.content_type = 'application/json'
            http_request_mock.json = {}
            with raises(AttributeError):
                calculation._parse_request(http_request_mock)

        def test_parse_request_with_different_content_type(self):
            http_request_mock = Mock()
            http_request_mock.query_string = Mock()
            http_request_mock.query_string.decode = Mock('a=1&b=[10,20]')
            http_request_mock.content_type = 'unknown'
            http_request_mock.json = {
                'measures': [
                    {'savings': []},
                ],
            }
            with raises(AttributeError):
                calculation._parse_request(http_request_mock)

        def test_parse_request_without_json(self):
            http_request_mock = Mock()
            http_request_mock.query_string = Mock()
            http_request_mock.query_string.decode = Mock('a=1&b=[10,20]')
            with raises(AttributeError) as exception_info:
                calculation._parse_request(http_request_mock)
                assert exception_info.value

    class TestTranslateIdIfExists:
        def test_without_existing_id(self):
            table = Table(
                [
                    {'id_measure': 1, 'id_parameter': 2, '2000': 1},
                ]
            )
            result = calculation._translate_id_if_exists(
                table,
                'id_foo',
                'mocked_data_source',
            )
            assert result['2000'][1, 2] == 1

        def test_with_existing_id(self):
            table = Table(
                [
                    {'id_measure': 1, 'id_parameter': 2, '2000': 33},
                ]
            )

            id_table = IdTable(
                [
                    {'id': 2, 'label': 'foo', 'description': 'baa'},
                ]
            )

            mocked_data_source = Mock()
            mocked_data_source.id_table = Mock(id_table)

            result = calculation._translate_id_if_exists(
                table,
                'id_parameter',
                mocked_data_source,
            )
            assert result['2000'][1, 'foo'] == 33

    class TestTranslateResult:
        def test_with_wrong_argument(self):
            annual_series = AnnualSeries({'2010': 10})
            with raises(ValueError):
                calculation._translate_result(
                    'mocked_key',
                    annual_series,
                    'mocked_data_source',
                )

        @patch(
            calculation._translate_id_if_exists,
            Mock('mocked_result'),
        )
        @patch(
            calculation._validate_remaining_index_column_names,
            Mock(),
        )
        def test_normal_usage(self):
            result = calculation._translate_result(
                'mocked_key',
                'mocked_table',
                'mocked_data_source',
            )
            assert result == 'mocked_result'

    @patch(
        calculation._translate_result,
        Mock('mocked_result'),
    )
    def test_translate_result_tables(self):
        tables = {
            'mocked_table_name': 'mocked_table',
        }
        result = calculation._translate_result_tables(
            tables,
            'mocked_data_source',
        )
        assert result['mocked_table_name'] == 'mocked_result'

    class TestValidateData:
        def test_with_nan(self):
            tables = {
                'foo': Table(
                    [
                        {
                            'id_measure': 1,
                            '2000': float('NaN'),
                        }
                    ]
                ),
            }
            with raises(ValueError):
                calculation._validate_data(tables)

        def test_with_infinity(self):
            tables = {
                'foo': Table(
                    [
                        {
                            'id_measure': 1,
                            '2000': float('infinity'),
                        }
                    ]
                ),
            }
            with raises(ValueError):
                calculation._validate_data(tables)

        def test_with_minus_infinity(self):
            tables = {
                'foo': Table(
                    [
                        {
                            'id_measure': 1,
                            '2000': float('-infinity'),
                        }
                    ]
                ),
            }
            with raises(ValueError):
                calculation._validate_data(tables)

    class TestValidateRemainingIndexColumnNames:
        def test_with_non_id_column(self):
            table = Table(
                [
                    {
                        'id_measure': 1,
                        '2020': 33,
                    }
                ]
            )
            table = table.insert_index_column('foo', 1, 1)
            calculation._validate_remaining_index_column_names(table)

        def test_with_id_column(self):
            table = Table(
                [
                    {
                        'id_measure': 1,
                        '2020': 33,
                    }
                ]
            )
            table = table.insert_index_column('id_foo', 1, 1)
            with raises(KeyError):
                calculation._validate_remaining_index_column_names(table)
