# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.social import (
    energy_poverty,
    energy_poverty_eu,
    energy_poverty_national,
)
from micat.test_utils.isi_mock import Mock, patch


@patch(
    energy_poverty_eu.alleviation_of_energy_poverty_on_eu_level,
    ("mocked_m2_eu_result", "mocked_2m_eu_result"),
)
@patch(
    energy_poverty_national.alleviation_of_energy_poverty_on_national_level,
    Mock(side_effect=["mocked_m2_national_result", "mocked_2m_national_result"]),
)
class TestAlleviationOfEnergyPoverty:
    def test_on_eu_level(self):
        result = energy_poverty.alleviation_of_energy_poverty(
            "mocked_final_energy_saving_or_capacities",
            "mocked_population_of_municipality",
            "mocked_reduction_of_energy_cost",
            "mocked_data_source",
            0,
        )
        assert result[0] == "mocked_m2_eu_result"
        assert result[1] == "mocked_2m_eu_result"

    def test_on_national_level(self):
        result = energy_poverty.alleviation_of_energy_poverty(
            "mocked_final_energy_saving_or_capacities",
            "mocked_population_of_municipality",
            "mocked_reduction_of_energy_cost",
            "mocked_data_source",
            1,
        )
        assert result[0] == "mocked_m2_national_result"
        assert result[1] == "mocked_2m_national_result"
