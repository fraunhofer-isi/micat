# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access, duplicate-code

from micat.calculation import extrapolation
from micat.calculation.social import hospitalization_monetization
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


@patch(
    hospitalization_monetization._monetization_factors,
    2,
)
def test_monetize():
    reduction_hospitalization = Table(
        [
            {
                'id_foo': 1,
                '2000': 3,
            }
        ]
    )

    result = hospitalization_monetization.monetization_of_hospitalizations_due_to_air_pollution(
        reduction_hospitalization,
        'mocked_database',
        'mocked_id_region',
    )
    assert result['2000'][1] == 3 * 2


@patch(extrapolation.extrapolate_series, 'mocked_result')
def test_monetization_factors():
    data_source = Mock()
    data_source.annual_series = Mock('mocked_annual_series')

    result = hospitalization_monetization._monetization_factors(
        data_source,
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'
