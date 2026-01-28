# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def test_annual_years():
    result = extrapolation._annual_years([2000, 2005])
    assert result == [2000, 2001, 2002, 2003, 2004, 2005]
