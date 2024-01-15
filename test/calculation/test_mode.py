# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from test_utils.mock import raises

from calculation import mode


class TestIsEurostatMode:
    def test_with_string(self):
        with raises(ValueError):
            mode.is_eurostat_mode('2')

    def test_with_eurostat_mode(self):
        result = mode.is_eurostat_mode(3)
        assert result

    def test_with_primes_mode(self):
        result = mode.is_eurostat_mode(1)
        assert not result
