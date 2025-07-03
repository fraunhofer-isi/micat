# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import air_pollution
from micat.calculation.ecologic import (
    calculation_ecologic,
    energy_saving,
    reduction_of_green_house_gas_emission_monetization,
    targets,
)
from micat.calculation.economic import grid
from micat.test_utils.isi_mock import Mock, patch


@patch(energy_saving.energy_saving)
@patch(air_pollution.reduction_of_air_pollution)
@patch(air_pollution.reduction_of_green_house_gas_emission)
@patch(air_pollution.reduction_of_mortality_morbidity)
@patch(air_pollution.reduction_of_mortality_morbidity_monetization)
@patch(reduction_of_green_house_gas_emission_monetization.monetize)
@patch(targets.impact_on_res_targets)
@patch(targets.impact_on_res_targets_monetization)
@patch(grid.reduction_of_additional_capacities_in_grid)
class TestEcologicIndicators:
    def test_indicators(self):
        mocked_interim_data = Mock()

        id_region = 0

        mocked_data_source = Mock()

        result = calculation_ecologic.ecologic_indicators(
            mocked_interim_data,
            mocked_data_source,
            id_region,
        )
        assert len(result) == 9
