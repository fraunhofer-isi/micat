# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/65

from data_import.conversion_energy import convert_energy_unit


def test_conversion():
    value = 1
    unit_from = 'PJ'
    unit_to = 'ktoe'  # be aware that this is 1000 * toe, not toe
    result = convert_energy_unit(value, unit_from, unit_to)
    assert result - 23.8845 < 1e-4
