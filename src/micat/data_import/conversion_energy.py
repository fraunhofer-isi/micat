# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/65
import pandas as pd


def convert_energy_unit(value_or_table, unit_from, unit_to):
    coefficient = conversion_coefficient(unit_from, unit_to)
    return value_or_table * coefficient


def conversion_coefficient(unit_from, unit_to):
    matrix = pd.DataFrame(
        [
            # pylint: disable=line-too-long
            {
                'ktoe': 1,
                'GWh': 1 / 11.63,
                'kWh': 1 / 11630000,
                'TJ': 1 / 41.868,
                'Mtoe': 1000,
                'PJ': 1 / 0.041868,
                'TWh': 1 / 0.011630,
            },
            {
                'ktoe': 1 / 0.08598,
                'GWh': 1,
                'kWh': 1 / 1000000,
                'TJ': 1 / 3.6,
                'Mtoe': 1 / 0.00008598,
                'PJ': 1 / 0.0036,
                'TWh': 1000,
            },
            {
                'ktoe': 1 / 0.00000008598,
                'GWh': 1000000,
                'kWh': 1,
                'TJ': 1 / 0.0000036,
                'Mtoe': 1 / 0.00000000008598,
                'PJ': 1 / 0.0000000036,
                'TWh': 1000000000,
            },
            {
                'ktoe': 1 / 0.02388,
                'GWh': 1 / 0.28,
                'kWh': 1 / 277778,
                'TJ': 1,
                'Mtoe': 1 / 0.00002388,
                'PJ': 1000,
                'TWh': 1 / 0.00028,
            },
            {
                'ktoe': 1 / 1000,
                'GWh': 1 / 11630,
                'kWh': 1 / 11630000000,
                'TJ': 1 / 41868,
                'Mtoe': 1,
                'PJ': 1 / 41.868,
                'TWh': 1 / 11.63,
            },
            {
                'ktoe': 1 / 23.88,
                'GWh': 1 / 277.8,
                'kWh': 1 / 277777778,
                'TJ': 1 / 1000,
                'Mtoe': 1 / 0.02388,
                'PJ': 1,
                'TWh': 1 / 0.28,
            },
            {
                'ktoe': 1 / 85.98,
                'GWh': 1 / 1000,
                'kWh': 1 / 1000000000,
                'TJ': 1 / 3600,
                'Mtoe': 1 / 0.08598,
                'PJ': 1 / 3.6,
                'TWh': 1,
            },
        ],
        index=[
            'ktoe',
            'GWh',
            'kWh',
            'TJ',
            'Mtoe',
            'PJ',
            'TWh',
        ],
    )

    return matrix[unit_from][unit_to]
