# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import mode
from micat.calculation.economic import (
    eurostat,
    gross_available_energy,
    population,
    primes,
)
from micat.test_utils.isi_mock import patch


class TestGrossAvailableEnergy:
    @patch(mode.is_eurostat_mode, True)
    @patch(eurostat.primary_parameters)
    @patch(population.scale_by_population, "mocked_result")
    def test_for_eurostat_mode(self):
        result = gross_available_energy.gross_available_energy("mocked_data_source", "mocked_id_region", "mocked_years")
        assert result == "mocked_result"

    @patch(mode.is_eurostat_mode, False)
    @patch(primes.primary_parameters)
    @patch(population.scale_by_population, "mocked_result")
    def test_for_primes_mode(self):
        result = gross_available_energy.gross_available_energy("mocked_data_source", "mocked_id_region", "mocked_years")
        assert result == "mocked_result"
