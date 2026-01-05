# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/46
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/29
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/45
# pylint: disable=protected-access

import pandas as pd

import micat
from micat.calculation import air_pollution, extrapolation
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch, raises

mocked_fuel_split = Table(
    [
        {"id_final_energy_carrier": 2, "id_subsector": 2, "2018": 10},
    ]
)


@patch(
    air_pollution._factorial_reduction,
    "_factorial_reduction",
)
def test_reduction_of_air_pollution():
    mocked_iiasa_parameters = Mock()
    mocked_iiasa_parameters.reduce = Mock()
    mocked_iiasa_parameters_generation = Mock()
    mocked_iiasa_parameters_generation.reduce = Mock()
    result = air_pollution.reduction_of_air_pollution(
        mocked_iiasa_parameters,
        mocked_iiasa_parameters_generation,
        "mocked_energy_saving_by_final_energy_carrier",
        "mocked_heat_saving_final",
        "mocked_electricity_saving_final",
    )

    assert result == "_factorial_reduction_factorial_reduction_factorial_reduction"


mocked_reduction = Table(
    [
        {"id_measure": 1, "id_parameter": 4, "2020": 99},
    ]
)


@patch(
    air_pollution._factorial_reduction,
    mocked_reduction,
)
def test_reduction_of_green_house_gas_emission():
    mocked_iiasa_parameters = Mock()
    mocked_iiasa_parameters.reduce = Mock()
    mocked_iiasa_parameters_generation = Mock()
    mocked_iiasa_parameters_generation.reduce = Mock()
    result = air_pollution.reduction_of_green_house_gas_emission(
        mocked_iiasa_parameters,
        mocked_iiasa_parameters_generation,
        "mocked_energy_saving_by_final_energy_carrier",
        "mocked_heat_saving_final",
        "mocked_electricity_saving_final",
    )

    assert result["2020"][1] == 99 * 3


@patch(
    air_pollution._factorial_reduction,
    "_factorial_reduction",
)
def test_reduction_of_mortality_morbidity():
    mocked_iiasa_parameters = Mock()
    mocked_iiasa_parameters.reduce = Mock()
    mocked_iiasa_parameters_generation = Mock()
    mocked_iiasa_parameters_generation.reduce = Mock()
    result = air_pollution.reduction_of_mortality_morbidity(
        mocked_iiasa_parameters,
        mocked_iiasa_parameters_generation,
        "mocked_energy_saving_by_final_energy_carrier",
        "mocked_heat_saving_final",
        "mocked_electricity_saving_final",
    )

    assert result == "_factorial_reduction_factorial_reduction_factorial_reduction"


mocked_reduction = AnnualSeries({"2020": 1000, "2030": 2000})


@patch(
    extrapolation.extrapolate_series,
    mocked_reduction,
)
def test_reduction_of_mortality_morbidity_monetization():
    reduction_of_mortality_morbidity = Table(
        [
            {
                "id_measure": 1,
                "id_parameter": 8,
                "2020": 2000,
                "2030": 4000,
            },
            {
                "id_measure": 1,
                "id_parameter": 9,
                "2020": 2000,
                "2030": 4000,
            },
        ]
    )

    data_source = Mock()
    data_source.table = Mock(
        Table(
            [
                {"id_region": "mocked_id_region", "id_parameter": 37, "2020": 1000000, "2030": 2000000},
                {"id_region": "mocked_id_region", "id_parameter": 63, "2020": 500000, "2030": 1000000},
            ]
        )
    )

    result = air_pollution.reduction_of_mortality_morbidity_monetization(
        reduction_of_mortality_morbidity,
        data_source,
        "mocked_id_region",
    )

    assert result["2020"][1].iloc[0] == 2000000
    assert result["2030"][1].iloc[0] == 8000000


mocked_reduction = Table(
    [
        {"id_measure": 1, "id_parameter": 23, "2020": 33},
    ]
)


@patch(
    air_pollution._factorial_reduction,
    mocked_reduction,
)
def test_reduction_of_lost_work_days():
    mocked_iiasa_parameters = Mock()
    mocked_iiasa_parameters.reduce = Mock()
    mocked_iiasa_parameters_generation = Mock()
    mocked_iiasa_parameters_generation.reduce = Mock()
    result = air_pollution.reduction_of_lost_work_days(
        mocked_iiasa_parameters,
        mocked_iiasa_parameters_generation,
        "mocked_energy_saving_by_final_energy_carrier",
        "mocked_heat_saving_final",
        "mocked_electricity_saving_final",
    )

    assert result["2020"][1] == 33 * 3


@patch(micat.utils.list.string_to_integer, "mocked_columns")
@patch(Table.aggregate_to, "mocked_result")
class TestFactorialReduction:
    @staticmethod
    def mocked_factor():
        return Table([{"id_subsector": 2, "id_final_energy_carrier": 2, "2018": 2}])

    @patch(
        extrapolation.extrapolate,
        Mock(mocked_factor()),
    )
    def test_without_nan_values(self):
        result = air_pollution._factorial_reduction(
            "mocked_air_df",
            mocked_fuel_split,
        )
        assert result == "mocked_result"

    @staticmethod
    def mocked_factor_producing_nan():
        return Table([{"id_subsector": 1, "id_final_energy_carrier": 2, "2018": 2}])

    @patch(
        extrapolation.extrapolate,
        Mock(mocked_factor_producing_nan()),
    )
    def test_with_nan_values(self):
        with raises(KeyError):
            air_pollution._factorial_reduction(
                "mocked_air_df",
                mocked_fuel_split,
            )


def mocked_transpose():
    df = pd.DataFrame(
        [
            {"SO2": 10},
        ]
    )
    df.index = ["2020"]
    return Table(df)


def mocked_parameter_table():
    return Table(
        [
            {"id_parameter": 4, "id_final_energy_carrier": 2, "id_subsector": 2, "2018": 1},
        ]
    )
