# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.economic import eurostat
from micat.test_utils.isi_mock import Mock, patch


@patch(eurostat._primary_parameters_raw, 'mocked_parameters')
@patch(extrapolation.extrapolate, 'mocked_result')
def test_primary_parameters():
    result = eurostat.primary_parameters(
        'mocked_data_source',
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


@patch(eurostat._technology_parameters_raw, 'mocked_parameters')
@patch(extrapolation.extrapolate, 'mocked_result')
def test_technology_parameters():
    result = eurostat.technology_parameters(
        'mocked_data_source',
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


# pylint: disable=duplicate-code
def test_primary_parameters_raw():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = eurostat._primary_parameters_raw(
        data_source_mock,
        'mocked_id_region',
    )
    assert table == 'mocked_table'


def test_technology_parameters_raw():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = eurostat._technology_parameters_raw(
        data_source_mock,
        'mocked_id_region',
    )
    assert table == 'mocked_table'
