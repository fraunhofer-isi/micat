# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.data_import import conversion_coefficients
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch, raises


def mock_table():
    table_mock = Mock()
    table_mock.unique_index_values = Mock([1, 2])
    table_mock.insert_index_column = Mock(table_mock)
    table_mock.reduce = Mock()
    return table_mock


@patch(conversion_coefficients._input_output_ratio)
@patch(conversion_coefficients._chp_usage_share)
@patch(conversion_coefficients._coefficient, mock_table())
@patch(Table.concat, mock_table())
def test_conversion_coefficients():
    inout = {
        'heat_in': mock_table(),
        'heat_out': 'mocked_heat_out',
        'electricity_in': mock_table(),
        'electricity_out': 'mocked_electricity_out',
        'chp_in': mock_table(),
        'chp_heat_out': 'mocked_chp_heat_out',
        'chp_electricity_out': 'mocked_chp_electricity_out',
    }

    result = conversion_coefficients.conversion_coefficients(
        inout,
    )

    assert result is not None


class TestCoefficient:
    def test_normal_usage(self):
        energy_input = Table(
            [
                {'id_region': 0, '2000': 7000},
                {'id_region': 1, '2000': 7000},
            ]
        )

        chp_share = Table(
            [
                {'id_region': 0, '2000': 0.5},
                {'id_region': 1, '2000': 0.5},
            ]
        )

        chp_input = Table(
            [
                {'id_region': 0, '2000': 20000},
                {'id_region': 1, '2000': 0},
            ]
        )

        energy_output = Table(
            [
                {'id_region': 0, '2000': 200},
                {'id_region': 1, '2000': 200},
            ]
        )

        chp_output = Table(
            [
                {'id_region': 0, '2000': 400},
                {'id_region': 1, '2000': 0},
            ]
        )

        result = conversion_coefficients._coefficient(
            energy_input,
            chp_share,
            chp_input,
            energy_output,
            chp_output,
        )
        values = result['2000']

        assert values[0] == (7000 + 0.5 * 20000) / (200 + 400)
        assert values[1] == 7000 / 200

    def test_with_nan_in_input(self):
        energy_input = Table(
            [
                {'id_region': 0, '2000': float('NaN')},
            ]
        )

        chp_share = Table(
            [
                {'id_region': 0, '2000': 0.5},
            ]
        )

        chp_input = Table(
            [
                {'id_region': 0, '2000': 20000},
            ]
        )

        energy_output = Table(
            [
                {'id_region': 0, '2000': 200},
            ]
        )

        chp_output = Table(
            [
                {'id_region': 0, '2000': 400},
            ]
        )

        with raises(ValueError):
            conversion_coefficients._coefficient(
                energy_input,
                chp_share,
                chp_input,
                energy_output,
                chp_output,
            )


def test_chp_usage_share():
    input_output_ratio_left = Table(
        [
            {'id_region': 0, '2000': 1.3},
        ]
    )

    chp_output_left = Table(
        [
            {'id_region': 0, '2000': 400},
        ]
    )

    input_output_ratio_right = Table(
        [
            {'id_region': 0, '2000': 2.5},
        ]
    )

    chp_output_right = Table(
        [
            {'id_region': 0, '2000': 700},
        ]
    )

    result = conversion_coefficients._chp_usage_share(
        input_output_ratio_left,
        chp_output_left,
        input_output_ratio_right,
        chp_output_right,
    )

    values = result['2000']
    left = 1.3 * 400
    right = 2.5 * 700
    assert values[0] == left / (left + right)


total_energy_input = Table(
    [
        {'id_region': 0, '2000': 4},
        {'id_region': 1, '2000': 4},
    ]
)


@patch(Table.aggregate_to, total_energy_input)
def test_input_output_ratio():
    energy_input_table = Table(
        [
            {'id_region': 0, 'id_primary_energy_carrier': 1, '2000': 2},
            {'id_region': 0, 'id_primary_energy_carrier': 2, '2000': 2},
            {'id_region': 1, 'id_primary_energy_carrier': 1, '2000': 2},
            {'id_region': 1, 'id_primary_energy_carrier': 2, '2000': 2},
        ]
    )

    energy_output_table = Table(
        [
            {'id_region': 0, '2000': 40},
            {'id_region': 1, '2000': 0},
        ]
    )

    result = conversion_coefficients._input_output_ratio(
        energy_input_table,
        energy_output_table,
    )

    assert result['2000'][0] == 0.1
    assert result['2000'][1] == 0.1
