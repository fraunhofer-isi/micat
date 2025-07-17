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
    directory = micat_path + "/src/micat/data/"
    return directory


database_directory = determine_database_directory()
database_path = database_directory + "public.sqlite"
confidential_database_path = database_directory + "confidential.sqlite"

mocked_measure_specific_parameters = {  # maps from id_measure to dictionary:
    1: {
        "constants": [
            {
                "id_parameter": 36,
                "value": 27,
            },
        ],
        "finalParameters": [
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 1,
                "2010": 42,
                "2015": 32,
                "2020": 34,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 2,
                "2010": 24,
                "2015": 22,
                "2020": 0,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 3,
                "2010": 0,
                "2015": 0,
                "2020": 37,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 4,
                "2010": 0,
                "2015": 0,
                "2020": 0,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 5,
                "2010": 0,
                "2015": 0,
                "2020": 0,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 6,
                "2010": 0,
                "2015": 0,
                "2020": 0,
            },
            {
                "id_parameter": 16,
                "id_final_energy_carrier": 7,
                "2010": 0,
                "2015": 0,
                "2020": 0,
            },
        ],
        "parameters": [
            {
                "id_parameter": 40,
                "2010": 42000000,
                "2015": 21000000,
                "2020": 10540000.0,
            },
            {
                "id_parameter": 35,
                "2010": 14,
                "2015": 0,
                "2020": 0,
            },
        ],
    }
}


def mocked_savings():
    savings = Table(
        [
            {
                "id_measure": 1,
                "id_subsector": 3,
                "id_action_type": 8,
                "2020": 5000,
                "2025": 4000,
                "2030": 3000,
            },
            {
                "id_measure": 2,
                "id_subsector": 3,
                "id_action_type": 11,
                "2020": 10000,
                "2025": 9000,
                "2030": 8000,
            },
        ]
    )
    return savings


def mocked_nuclear():
    nuclear = Table(
        [
            {
                "id_subsector": 3,
                "id_action_type": 8,
                "id_primary_energy_carrier": 1,
                "2020": 4,
            },
        ]
    )
    return nuclear


def mocked_table():
    mock = Mock()
    mock.reduce = Mock("mocked_table")
    mock.join_id_column = Mock(Mock())
    mock.transpose = Mock("mocked_transposed_table")
    return mock


class TestPublicApi:
    @staticmethod
    def mocked_id_region():
        return "1"

    @patch(
        calculation._front_end_arguments,
        {
            "id_region": mocked_id_region(),
            "final_energy_saving_by_action_type": mocked_savings(),
            "parameters": {},
            "measure_specific_parameters": mocked_measure_specific_parameters,
            "population_of_municipality": 1,
        },
    )
    def test_for_debugging_calculate_indicator_data(self):
        http_request_mock = "request_mock"
        database = Database(database_path)
        confidential_database = Database(confidential_database_path)
        result = calculation.calculate_indicator_data(http_request_mock, database, confidential_database)
        import_dependency = result["reductionOfImportDependency"]
        rows = import_dependency["rows"]
        oil_2020 = rows[0][2]
        assert oil_2020 > 0.001

        assertion.allow_strings_but_no_nan_or_inf_values(rows)
