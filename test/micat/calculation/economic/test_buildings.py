# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd

from micat.calculation.economic import buildings
from micat.table.mapping_table import MappingTable
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch

sectorial_cost_frame = pd.DataFrame(
    [
        {
            'id_measure': 1,
            'id_sector': 3,
            'id_action_type': 1,
            'id_final_energy_carrier': 2,
            '2020': 1,
            '2030': 2,
        },
    ]
)

sectorial_cost = Table(
    [
        {
            'id_measure': 1,
            'id_sector': 3,
            'id_action_type': 1,
            'id_final_energy_carrier': 2,
            '2020': 1,
            '2030': 2,
        },
    ]
)

capitalization_rate = ValueTable(
    [
        {'id_sector': 3, 'value': 0.5},
    ]
)


class TestAddedAssetValueOfBuildings:
    @patch(
        buildings._sectorial_cost_frame,
        sectorial_cost_frame,
    )
    @patch(
        buildings._include_default_entries,
        sectorial_cost,
    )
    @patch(
        buildings._includes_relevant_action_types,
        True,
    )
    @patch(
        buildings._capitalization_rate,
        capitalization_rate,
    )
    def test_with_relevant_action_types(self):
        reduction_of_energy_cost = Table(
            [
                {
                    'id_measure': 1,
                    'id_subsector': 1,
                    'id_action_type': 1,
                    'id_final_energy_carrier': 2,
                    '2020': 20,
                    '2030': 30,
                },
            ]
        )

        data_source = Mock()

        result = buildings.added_asset_value_of_buildings(
            reduction_of_energy_cost,
            data_source,
            'mocked_id_region',
            'mocked_years',
        )

        assert result['2020'][1, 3] == 2
        assert result['2030'][1, 3] == 4

    @patch(
        buildings._includes_relevant_action_types,
        Mock(False),
    )
    @patch(
        buildings._create_zero_result,
        'mocked_result',
    )
    def test_without_relevant_action_types(self):
        result = buildings.added_asset_value_of_buildings(
            'mocked_reduction_of_energy_cost',
            'mocked_data_source',
            'mocked_id_region',
            'mocked_years',
        )
        assert result == 'mocked_result'


def test_capitalization_rate():
    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_result')

    data_source = Mock()
    data_source.table = Mock(mocked_table)

    result = buildings._capitalization_rate(
        data_source,
        'mocked_id_region',
    )
    assert result == 'mocked_result'


def test_create_zero_result():
    table = Mock()
    table.unique_index_values = Mock([1])

    relevant_sector_ids = [3]
    years = [2020]
    result = buildings._create_zero_result(
        table,
        relevant_sector_ids,
        years,
    )
    assert result['2020'][1, 3] == 0


def test_include_default_entries():
    sectorial_cost_table = Table(
        [
            {
                'id_measure': 1,
                'id_sector': 4,
                'id_action_type': 1,
                'id_final_energy_carrier': 1,
                '2020': 20,
                '2030': 30,
            }
        ]
    )

    relevant_sector_ids = [3]
    years = [2020, 2030]

    result = buildings._include_default_entries(
        sectorial_cost_table,
        relevant_sector_ids,
        years,
    )
    assert result['2020'][1, 3, 1, 1] == 0


class TestIncludesRelevantActionTypes:
    def test_with_relevant_action_type(self):
        reduction_of_energy_cost = Table(
            [
                {
                    'id_measure': 1,
                    'id_subsector': 1,
                    'id_action_type': 2,
                    '2000': 33,
                }
            ]
        )
        relevant_action_type_ids = [2]
        result = buildings._includes_relevant_action_types(
            reduction_of_energy_cost,
            relevant_action_type_ids,
        )
        assert result

    def test_without_relevant_action_type(self):
        reduction_of_energy_cost = Table(
            [
                {
                    'id_measure': 1,
                    'id_subsector': 1,
                    'id_action_type': 2,
                    '2000': 33,
                }
            ]
        )
        relevant_action_type_ids = [3]
        result = buildings._includes_relevant_action_types(
            reduction_of_energy_cost,
            relevant_action_type_ids,
        )
        assert not result


def test_sectorial_cost_frame():
    relevant_cost = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 1,
                'id_action_type': 1,
                'id_final_energy_carrier': 1,
                '2000': 33,
            }
        ]
    )

    mapping = pd.DataFrame([{'id': 1, 'id_subsector': 1, 'id_sector': 88}])
    mapping.set_index(['id'], inplace=True)
    mapping_table = MappingTable(mapping)

    data_source = Mock()
    data_source.mapping_table = Mock(mapping_table)
    result = buildings._sectorial_cost_frame(
        relevant_cost,
        data_source,
    )
    assert result['2000'][1, 88, 1, 1] == 33
