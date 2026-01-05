# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.economic import population
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


class TestPopulationOfMunicipality:
    def test_with_population(self):
        properties = {'population': '1000'}
        result = population.population_of_municipality(properties)
        assert result == 1000

    def test_without_population(self):
        properties = {}
        result = population.population_of_municipality(properties)
        assert result is None


class TestScaleByPopulation:
    def test_without_population(self):
        result = population.scale_by_population(
            'mocked_table',
            None,
            'mocked_data_source',
            'mocked_id_region',
            'mocked_years',
        )
        assert result == 'mocked_table'

    @patch(population._population_for_region, 2)
    def test_with_population(self):
        table = Table(
            [
                {'id_foo': 1, '2000': 10},
            ]
        )
        population_of_municipality = 1

        result = population.scale_by_population(
            table,
            population_of_municipality,
            'mocked_data_source',
            'mocked_id_region',
            'mocked_years',
        )
        assert result['2000'][1] == 5

    class TestPopulationForRegion:
        @patch(extrapolation.extrapolate_series, 'mocked_result')
        def test_series(self):
            mocked_data_source = Mock()
            result = population._population_for_region(
                mocked_data_source,
                'mocked_id_region',
                ['mocked_year'],
            )
            assert result == 'mocked_result'

        def test_single_value(self):
            mocked_primes_parameters = Table([{'id_parameter': 24, '2000': 'mocked_result'}])
            mocked_data_source = Mock()
            mocked_data_source.table = Mock(mocked_primes_parameters)
            year = 2000
            result = population._population_for_region(
                mocked_data_source,
                'mocked_id_region',
                year,
            )
            assert result == 'mocked_result'
