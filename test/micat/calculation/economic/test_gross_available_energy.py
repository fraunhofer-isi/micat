# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from micat.calculation.economic import (
    eurostat,
    gross_available_energy,
    population,
)
from micat.template import mocks
from micat.test_utils.isi_mock import patch


class TestGrossAvailableEnergy:
    @patch(eurostat.primary_parameters)
    @patch(population.scale_by_population, "mocked_result")
    def test_gross_available_energy(self):
        result = gross_available_energy.gross_available_energy(
            mocks.mocked_database(), "mocked_id_region", [2020, 2021, 2022]
        )
        assert result == "mocked_result"
