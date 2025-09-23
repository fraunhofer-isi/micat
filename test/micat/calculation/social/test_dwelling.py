# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.calculation.economic import population
from micat.calculation.social import dwelling
from micat.input.data_source import DataSource
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch, raises


@patch(dwelling.dwelling_stock)
@patch(dwelling._improvement_actions_per_energy_unit)
@patch(dwelling._provide_default_number_of_affected_dwellings)
def test_number_of_affected_dwellings():
    data_source = Mock()

    def mocked_measure_specific_calculation(
        _final_energy_saving_or_capacities,
        _determine_table_for_measure,
        provide_default_table,
    ):
        provide_default_table(
            "mocked_id_measure",
            "mocked_id_subsector",
            "mocked_id_action_type",
            "mocked_savings",
        )
        return "mocked_result"

    data_source.measure_specific_calculation = mocked_measure_specific_calculation

    final_energy_savings_by_action_type = Mock()

    result = dwelling.number_of_affected_dwellings(
        final_energy_savings_by_action_type,
        data_source,
        "mocked_id_region",
        "mocked_population_of_municipality",
    )
    assert result == "mocked_result"


@patch(population.scale_by_population, "mocked_result")
def test_dwelling_stock():
    result = dwelling.dwelling_stock(
        Mock(),
        Mock(),
        "mocked_id_region",
        "mocked_population_of_municipality",
    )
    assert result == "mocked_result"


@patch(extrapolation.extrapolate, "mocked_result")
def test_improvement_actions_per_energy_unit():
    data_source = Mock()
    result = dwelling._improvement_actions_per_energy_unit(data_source, "mocked_years")
    assert result == "mocked_result"


class TestProvideDefaultNumberOfAffectedDwellings:
    def test_for_different_subsector(self):
        energy_savings = AnnualSeries({"2000": 1, "2010": 2})

        id_measure = 1
        id_subsector = 18

        result = dwelling._provide_default_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            "mocked__id_action_type",
            energy_savings,
            "mocked_improvement_actions_per_energy_unit",
        )
        assert result["2000"][id_measure] == 0
        assert result["2010"][id_measure] == 0

    def test_for_id_action_type_1(self):
        energy_savings = AnnualSeries({"2000": 1, "2010": 2})

        id_measure = 1
        id_subsector = 17
        id_action_type = 1
        improvement_actions_per_energy_unit = Mock()
        improvement_actions_per_energy_unit.reduce = Mock(2)

        result = dwelling._provide_default_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            id_action_type,
            energy_savings,
            improvement_actions_per_energy_unit,
        )
        assert result["2000"][id_measure] == 2
        assert result["2010"][id_measure] == 4

    def test_for_id_action_type_4(self):
        energy_savings = AnnualSeries({"2000": 1, "2010": 2})

        id_measure = 1
        id_subsector = 17
        id_action_type = 4

        result = dwelling._provide_default_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            id_action_type,
            energy_savings,
            "mocked_improvement_actions_per_energy_unit",
        )
        assert result["2000"][id_measure] == 0
        assert result["2010"][id_measure] == 0

    def test_for_id_action_type_5(self):
        energy_savings = AnnualSeries({"2000": 1, "2010": 2})

        id_measure = 1
        id_subsector = 17
        id_action_type = 5

        result = dwelling._provide_default_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            id_action_type,
            energy_savings,
            "mocked_improvement_actions_per_energy_unit",
        )
        assert result["2000"][id_measure] == 0
        assert result["2010"][id_measure] == 0

    def test_for_unknown_id_action_type(self):
        energy_savings = AnnualSeries({"2000": 1, "2010": 2})

        id_measure = 1
        id_subsector = 17
        id_action_type = 99

        with raises(KeyError):
            dwelling._provide_default_number_of_affected_dwellings(
                id_measure,
                id_subsector,
                id_action_type,
                energy_savings,
                "mocked_improvement_actions_per_energy_unit",
            )


class TestMeasureSpecificNumberOfAffectedDwellings:
    @patch(DataSource.row_table, "mocked_result")
    def test_non_residential(self):
        id_subsector = 1
        extrapolated_final_parameters = Mock()
        mocked_dwelling_stock = Mock()

        result = dwelling._measure_specific_number_of_affected_dwellings(
            "mocked_id_measure",
            id_subsector,
            "mocked_id_action_type",
            "mocked_energy_saving",
            extrapolated_final_parameters,
            "mocked_improvement_actions_per_energy_unit",
            mocked_dwelling_stock,
        )
        assert result == "mocked_result"

    class TestResidential:
        extrapolated_final_parameters = Mock()

        @patch(
            dwelling._measure_specific_number_of_affected_dwellings_others,
            "mocked_value",
        )
        @patch(DataSource.row_table, "mocked_result")
        def test_for_action_type_123(self):
            id_action_type = 1
            id_subsector = 17
            extrapolated_final_parameters = Mock()
            mocked_improvement_actions_per_energy_unit = Mock()
            mocked_dwelling_stock = Mock()

            result = dwelling._measure_specific_number_of_affected_dwellings(
                "mocked_id_measure",
                id_subsector,
                id_action_type,
                "mocked_energy_saving",
                extrapolated_final_parameters,
                mocked_improvement_actions_per_energy_unit,
                mocked_dwelling_stock,
            )
            assert result == "mocked_result"

        @patch(
            dwelling._measure_specific_number_of_affected_dwellings_others,
            "mocked_value",
        )
        @patch(DataSource.row_table)
        @patch(dwelling._result_to_table, "mocked_result")
        def test_action_type_4(self):
            id_action_type = 4
            id_subsector = 17
            mocked_dwelling_stock = Mock()

            result = dwelling._measure_specific_number_of_affected_dwellings(
                "mocked_id_measure",
                id_subsector,
                id_action_type,
                "mocked_energy_saving",
                self.extrapolated_final_parameters,
                "mocked_improvement_actions_per_energy_unit",
                mocked_dwelling_stock,
            )
            assert result == "mocked_result"

        @patch(DataSource.row_table, "mocked_result")
        def test_action_type_5_6(self):
            id_action_type = 5
            id_subsector = 17
            mocked_dwelling_stock = Mock()

            result = dwelling._measure_specific_number_of_affected_dwellings(
                "mocked_id_measure",
                id_subsector,
                id_action_type,
                "mocked_energy_saving",
                self.extrapolated_final_parameters,
                "mocked_improvement_actions_per_energy_unit",
                mocked_dwelling_stock,
            )
            assert result == "mocked_result"

        @patch(DataSource.row_table, "mocked_row_table")
        def test_action_type_other(self):
            id_action_type = 8
            id_subsector = 17
            mocked_dwelling_stock = Mock()

            with raises(KeyError):
                dwelling._measure_specific_number_of_affected_dwellings(
                    "mocked_id_measure",
                    id_subsector,
                    id_action_type,
                    "mocked_energy_saving",
                    self.extrapolated_final_parameters,
                    "mocked_improvement_actions_per_energy_unit",
                    mocked_dwelling_stock,
                )


class TestMeasureSpecificNumberOfAffectedDwellingsElectric:
    class TestWithoutNumberOfAffectedDwellings:
        def test_without_annual_renovation_rate(self):
            extrapolated_final_parameters = Mock()
            extrapolated_final_parameters.reduce = Mock(None)

            result = dwelling._measure_specific_number_of_affected_dwellings_electric(
                extrapolated_final_parameters,
                "mocked_dwelling_stock",
            )
            assert result == 0

        def test_with_annual_renovation_rate(self):
            def mocked_reduce(_id_name, value):
                if value == 45:
                    return None  # for number_of_affected_dwellings_from_user
                else:
                    return 2  # for annual_renovation_rate_from_user

            extrapolated_final_parameters = Mock()
            extrapolated_final_parameters.reduce = mocked_reduce

            dwelling_stock = 2

            result = dwelling._measure_specific_number_of_affected_dwellings_electric(
                extrapolated_final_parameters,
                dwelling_stock,
            )
            assert result == 0.04

    def test_with_number_of_affected_dwellings(self):
        extrapolated_final_parameters = Mock()
        extrapolated_final_parameters.reduce = Mock("mocked_result")

        result = dwelling._measure_specific_number_of_affected_dwellings_electric(
            extrapolated_final_parameters,
            "mocked_dwelling_stock",
        )
        assert result == "mocked_result"


class TestResultToTable:
    def test_with_table(self):
        table = Table([{"id_foo": 1, "2000": 10}])
        result = dwelling._result_to_table(
            table,
            "mocked_id_measure",
            "mocked_years",
        )
        assert result["2000"][1] == 10

    def test_with_annual_series(self):
        series = AnnualSeries({"2000": 10})
        result = dwelling._result_to_table(
            series,
            1,
            "mocked_years",
        )
        assert result["2000"][1] == 10

    @patch(DataSource.row_table, "mocked_result")
    def test_with_value(self):
        result = dwelling._result_to_table(
            "mocked_value",
            "mocked_id_measure",
            "mocked_years",
        )
        assert result == "mocked_result"


class TestMeasureSpecificNumberOfAffectedDwellingsOthers:
    class TestWithoutNumberOfAffectedDwellings:
        def test_without_annual_renovation_rate(self):
            def mocked_reduce(_id_name, value):
                if value == 45:  # number of affected dwellings
                    return None
                elif value == 43:  # annual renovation rate
                    return None
                else:
                    raise ValueError("unknown")

            extrapolated_final_parameters = Mock()
            extrapolated_final_parameters.reduce = mocked_reduce

            improvement_actions_per_energy_unit = 1

            mocked_table = Table([{"id_measure": 1, "2000": 2}])
            energy_saving = mocked_table
            dwelling_stock = mocked_table

            result = dwelling._measure_specific_number_of_affected_dwellings_others(
                energy_saving,
                extrapolated_final_parameters,
                improvement_actions_per_energy_unit,
                dwelling_stock,
            )
            assert result["2000"][1] == 2

        def test_with_annual_renovation_rate(self):
            def mocked_reduce(_id_name, value):
                if value == 45:  # number of affected dwellings
                    return None
                elif value == 43:  # annual renovation rate
                    return 3
                elif value == 48:  # improvement actions per energy unit
                    return 2
                else:
                    raise ValueError("unknown")

            extrapolated_final_parameters = Mock()
            extrapolated_final_parameters.reduce = mocked_reduce

            mocked_table = Table([{"id_measure": 1, "2000": 2}])
            energy_saving = mocked_table
            dwelling_stock = mocked_table

            result = dwelling._measure_specific_number_of_affected_dwellings_others(
                energy_saving,
                extrapolated_final_parameters,
                "mocked_improvement_actions_per_energy_unit",
                dwelling_stock,
            )
            assert result["2000"][1] == 3 / 100 * 2

        def test_with_number_of_affected_dwellings(self):
            mocked_table = Table([{"id_measure": 1, "2000": 2}])

            extrapolated_final_parameters = Mock()
            extrapolated_final_parameters.reduce = Mock(mocked_table)

            energy_saving = mocked_table
            dwelling_stock = mocked_table

            result = dwelling._measure_specific_number_of_affected_dwellings_others(
                energy_saving,
                extrapolated_final_parameters,
                "mocked_improvement_actions_per_energy_unit",
                dwelling_stock,
            )
            assert result["2000"][1] == 2
