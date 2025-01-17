# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import os

from micat.calculation import calculation
from micat.input.database import Database
from micat.table.table import Table
from micat.test_utils import assertion
from micat.test_utils.isi_mock import Mock, patch


def determine_database_directory():
    file_path = os.path.abspath(__file__)
    calculation_path = os.path.dirname(file_path)
    test_path = os.path.dirname(calculation_path)
    micat_path = os.path.dirname(test_path)
    directory = micat_path + '/src/micat/data/'
    return directory


database_directory = determine_database_directory()
database_path = database_directory + 'public.sqlite'
confidential_database_path = database_directory + 'confidential.sqlite'


def mocked_savings():
    savings = Table(
        [
            {'id_measure': 1, 'id_subsector': 3, 'id_action_type': 8, '2020': 5000, '2025': 4000, '2030': 3000},
            {'id_measure': 2, 'id_subsector': 3, 'id_action_type': 11, '2020': 10000, '2025': 9000, '2030': 8000},
        ]
    )
    return savings


def mocked_nuclear():
    nuclear = Table(
        [
            {'id_subsector': 3, 'id_action_type': 8, 'id_primary_energy_carrier': 1, '2020': 4},
        ]
    )
    return nuclear


def mocked_table():
    mock = Mock()
    mock.reduce = Mock('mocked_table')
    mock.join_id_column = Mock(Mock())
    mock.transpose = Mock('mocked_transposed_table')
    return mock


class TestPublicApi:
    @staticmethod
    def mocked_id_mode():
        return '1'

    @staticmethod
    def mocked_id_region():
        return '1'

    @patch(
        calculation._front_end_arguments,
        {
            'id_mode': mocked_id_mode(),
            'id_region': mocked_id_region(),
            'final_energy_saving_by_action_type': mocked_savings(),
            'parameters': {},
            'measure_specific_parameters': {},
            'population_of_municipality': 1,
        },
    )
    def test_for_debugging_calculate_indicator_data(self):
        http_request_mock = 'request_mock'
        database = Database(database_path)
        confidential_database = Database(confidential_database_path)
        result = calculation.calculate_indicator_data(http_request_mock, database, confidential_database)
        import_dependency = result['reductionOfImportDependency']
        rows = import_dependency['rows']
        oil_2020 = rows[0][2]
        assert oil_2020 > 0.001

        assertion.allow_strings_but_no_nan_or_inf_values(rows)
