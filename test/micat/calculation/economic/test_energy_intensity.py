# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.economic import energy_intensity
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/36
# pylint: disable=protected-access
from micat.test_utils.isi_mock import patch

mocked_gross_available_energy = Table(
    [
        {'id_primary_energy_carrier': 2, '2020': 4},
    ]
)

mocked_gross_domestic_product_baseline = Table(
    [
        {'id_parameter': 10, '2020': 10},  # inverted unit conversion
    ]
)

mocked_additional_gross_domestic_product = Table(
    [
        {'id_measure': 1, '2020': 2},
    ]
)

mocked_primary_non_energy_use = Table(
    [
        {'id_primary_energy_carrier': 2, '2020': 2},
    ]
)

mocked_additional_primary_energy_saving = Table(
    [
        {'id_measure': 1, 'id_subsector': 1, 'id_action_type': 1, 'id_primary_energy_carrier': 2, '2020': 1},
    ]
)

mocked_result_table = Table(
    [
        {'id_foo': 1, '2020': 1},
    ]
)


@patch(
    energy_intensity._intensity_table,
    mocked_result_table,
)
@patch(Table.concat, 'mocked_result')
def test_energy_intensity():
    result = energy_intensity.energy_intensity(
        mocked_gross_available_energy,
        mocked_gross_domestic_product_baseline,
        mocked_additional_gross_domestic_product,
        #mocked_primary_non_energy_use,
        mocked_additional_primary_energy_saving,
    )
    assert result == 'mocked_result'


@patch(Table.to_custom_json, 'mocked_result')
def test_intensity_table():
    sum_series = AnnualSeries({'2020': 10})

    gross_domestic_product = AnnualSeries({'2020': 200})

    label = 'foo'

    result = energy_intensity._intensity_table(
        sum_series,
        gross_domestic_product,
        label,
    )
    assert result['2020']['foo'] == 10 / 200
