# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import extrapolation
from micat.calculation.social import lost_working_days_monetization
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


@patch(
    lost_working_days_monetization._monetization_factors,
    2,
)
def test_monetize():
    reduction_of_lost_work_days = Table(
        [
            {
                'id_foo': 1,
                '2000': 3,
            }
        ]
    )

    result = lost_working_days_monetization.monetization_of_lost_working_days_due_to_air_pollution(
        reduction_of_lost_work_days,
        'mocked_database',
        'mocked_id_region',
    )
    assert result['2000'][1] == 3 * 2


@patch(extrapolation.extrapolate_series, 'mocked_result')
def test_monetization_factors():
    data_source = Mock()
    data_source.annual_series = Mock('mocked_annual_series')

    result = lost_working_days_monetization._monetization_factors(
        data_source,
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'
