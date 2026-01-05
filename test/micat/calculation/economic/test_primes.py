# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.economic import primes
from micat.test_utils.isi_mock import Mock, patch


@patch(primes._parameters_raw, 'mocked_parameters')
@patch(extrapolation.extrapolate, 'mocked_result')
def test_parameters():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = primes.parameters(
        data_source_mock,
        'mocked_id_region',
        'mocked_years',
    )
    assert table == 'mocked_result'


@patch(primes._primary_parameters_raw, 'mocked_parameters')
@patch(extrapolation.extrapolate, 'mocked_result')
def test_primary_parameters():
    result = primes.primary_parameters(
        'mocked_database',
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


@patch(primes._technology_parameters_raw, 'mocked_parameters')
@patch(extrapolation.extrapolate, 'mocked_result')
def test_technology_parameters():
    result = primes.technology_parameters(
        'mocked_database',
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


def test_parameters_raw():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = primes._parameters_raw(
        data_source_mock,
        'mocked_id_region',
    )
    assert table == 'mocked_table'


def test_primary_parameters_raw():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = primes._primary_parameters_raw(
        data_source_mock,
        'mocked_id_region',
    )
    assert table == 'mocked_table'


def test_technology_parameters_raw():
    data_source_mock = Mock()
    data_source_mock.table = Mock('mocked_table')

    table = primes._technology_parameters_raw(
        data_source_mock,
        'mocked_id_region',
    )
    assert table == 'mocked_table'
