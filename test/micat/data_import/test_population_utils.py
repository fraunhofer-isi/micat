# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.data_import.population_utils import PopulationUtils
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch, raises


@patch(PopulationUtils._population)
@patch(
    PopulationUtils._european_table,
    Table([{'id_region': 0, 'id_foo': 1, '2000': 1.5}]),
)
def test_extend_european_values():
    table = Table(
        [
            {'id_region': 1, 'id_foo': 1, '2000': 1},
            {'id_region': 2, 'id_foo': 1, '2000': 2},
        ]
    )

    database = Mock()
    result = PopulationUtils.extend_european_values(table, database)
    assert result['2000'][0, 1] == 1.5
    assert result['2000'][1, 1] == 1
    assert result['2000'][2, 1] == 2


class TestEuropeanTable:
    def test_two_index_columns(self):
        table = Table(
            [
                {'id_region': 1, 'id_foo': 1, '2000': 10},
                {'id_region': 2, 'id_foo': 1, '2000': 100},
            ]
        )

        population = Table(
            [
                {'id_region': 1, '2000': 1},
                {'id_region': 2, '2000': 2},
            ]
        )
        european_population = AnnualSeries({'2000': 3})

        result = PopulationUtils._european_table(table, population, european_population)
        assert isinstance(result, Table)

        assert result['2000'][0, 1] == 1 / 3 * (10 * 1 + 2 * 100)

    def test_only_region_column(self):
        table = Table(
            [
                {'id_region': 1, '2000': 10},
                {'id_region': 2, '2000': 100},
            ]
        )

        population = Table(
            [
                {'id_region': 1, '2000': 1},
                {'id_region': 2, '2000': 2},
            ]
        )
        european_population = AnnualSeries({'2000': 3})

        with raises(NotImplementedError):
            PopulationUtils._european_table(table, population, european_population)


def test_european_population():
    population = Table(
        [
            {'id_region': 0, '2000': 1.5},
            {'id_region': 1, '2000': 1},
            {'id_region': 2, '2000': 2},
        ]
    )
    result = PopulationUtils._european_population(population)
    assert isinstance(result, AnnualSeries)
    assert result['2000'] == 1.5


class TestPopulation:
    @patch(extrapolation.extrapolate, 'mocked_result')
    @patch(Table.concat_years, 'mocked_concat_result')
    def test_with_years(self):
        database = Mock()
        result = PopulationUtils._population(database, 'mocked_years')
        assert result == 'mocked_result'

    @patch(Table.concat_years, 'mocked_concat_years_result')
    def test_without_years(self):
        database = Mock()
        result = PopulationUtils._population(database)
        assert result == 'mocked_concat_years_result'
