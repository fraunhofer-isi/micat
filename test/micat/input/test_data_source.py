# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable = protected-access, too-many-lines
import pandas as pd

from micat.calculation import extrapolation
from micat.input.data_source import DataSource
from micat.series import annual_series
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, fixture, patch, raises


# noinspection PyProtectedMember
@fixture(name="sut")
def fixture_sut():
    with patch(DataSource._create_measure_specific_tables, {}):
        with patch(DataSource._create_global_tables, {}):
            return DataSource(
                "mocked_database",
                "mocked_id_region",
                "mocked_confidential_database",
                "mocked_measure_specific_parameters",
                "mocked_global_parameters",
            )


mocked_years = [2020, 2025, 2030]


def _mocked_final_energy_savings_by_action_type():
    mocked_final_energy_savings_by_action_type = Table(
        [
            {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 10, "2025": 20, "2030": 30},
            {"id_measure": 2, "id_subsector": 2, "id_action_type": 2, "2020": 100, "2025": 200, "2030": 300},
        ]
    )
    return mocked_final_energy_savings_by_action_type


def _mocked_annual_series():
    mocked_annual_series = annual_series.AnnualSeries({"2020": 1, "2025": 1, "2030": 1})
    return mocked_annual_series


def _mocked_measure_specific_parameter(_energy_saving, _id_parameter, provide_default, _is_value_table=False):
    mocked_parameter_table = Table([{"id_measure": 1, "id_subsector": 2, "id_action_type": 3, "2000": 100}])
    mocked_value = provide_default(1, 2, 3, "mocked_year", "mocked_saving")
    assert mocked_value
    return mocked_parameter_table


class TestPublicApi:
    def test_construction(self, sut):
        assert sut._database == "mocked_database"

    mocked_series = pd.Series([1, 2], index=["2000", "2020"])
    mocked_table = Table([{"id_foo": 1, "2000": 1}])

    @patch(DataSource.table, mocked_table)
    def test_annual_series(self, sut):
        result = sut.annual_series("mocked_table_name", "mocked_where_clause")
        assert result["2000"] == 1

    @patch(DataSource.annual_series, Mock())
    @patch(extrapolation.extrapolate_series, Mock(return_value=_mocked_annual_series()))
    def test_extrapolated_annual_series(self, sut):
        result = sut.extrapolated_annual_series("mocked_table_name", "mocked_years", "mocked_where_clause")
        assert result["2020"] == 1

    class TestAnnualSeriesFromValue:
        mocked_oversized_value_table = Mock()
        mocked_oversized_value_table.values = Mock()
        mocked_oversized_value_table.values.shape = Mock(return_value=(1, 2))

        mocked_value_table = ValueTable([{"id_parameter": 1, "value": 2}])

        @patch(DataSource.value_to_annual_series, Mock(return_value=_mocked_annual_series()))
        @patch(DataSource.table, Mock(return_value=mocked_value_table))
        def test_without_error(self, sut):
            result = sut.annual_series_from_value("mocked_value_table_name", mocked_years, "mocked_where_clause")
            assert result["2020"] == 1

        @patch(DataSource.table, Mock(return_value=mocked_oversized_value_table))
        def test_with_value_error(self, sut):
            with raises(Exception) as e_info:
                sut.annual_series_from_value("mocked_value_table_name", mocked_years, "mocked_where_clause")
                assert "Too many values to create" in e_info

    @patch(annual_series.AnnualSeries, Mock(return_value="mocked_annual_series"))
    def test_to_annual_series(self):
        result = DataSource.value_to_annual_series("mocked_value", mocked_years)
        assert result == "mocked_annual_series"

    def test_id_table(self, sut):
        sut._database = Mock()
        sut._database.id_table = Mock("mocked_result")

        result = sut.id_table("mocked_table_name")
        assert result == "mocked_result"

    class TestMeasureSpecificCalculation:
        @patch(
            DataSource._loop_over_measures_and_collect_tables,
            "mocked_result",
        )
        def test_without_measure_specific_parameters(self, sut):
            sut.table = Mock(None)

            result = sut.measure_specific_calculation(
                "mocked_final_energy_saving_by_action_type",
                "mocked_determine_table_for_measure",
                "mocked_provide_default_table",
            )
            assert result == "mocked_result"

        @patch(
            DataSource._loop_over_measures_and_collect_tables,
            "mocked_result",
        )
        @patch(
            DataSource._measure_ids_for_which_extra_data_exists,
            "mocked_id_values",
        )
        def test_with_measure_specific_parameters(self, sut):
            mocked_table = Mock()
            sut.table = Mock(mocked_table)

            result = sut.measure_specific_calculation(
                "mocked_final_energy_saving_by_action_type",
                "mocked_determine_table_for_measure",
                "mocked_provide_default_table",
            )
            assert result == "mocked_result"

    class TestMeasureSpecificParameter:
        @patch(
            DataSource._loop_over_measures_and_collect_parameters,
            "mocked_result",
        )
        def test_without_measure_specific_parameters(self, sut):
            sut.table = Mock(None)

            result = sut.measure_specific_parameter(
                "mocked_final_energy_saving_by_action_type",
                "mocked_id_parameter",
                "mocked_provide_default_table",
                "mocked_years",
            )
            assert result == "mocked_result"

        @patch(
            DataSource._loop_over_measures_and_collect_parameters,
            "mocked_result",
        )
        def test_with_id_measure(self, sut):
            mocked_table = Mock()
            mocked_table.has_index_column = Mock(True)

            mocked_parameter_table = Mock()
            mocked_parameter_table.reduce = Mock(mocked_table)

            sut.table = Mock(mocked_parameter_table)

            result = sut.measure_specific_parameter(
                "mocked_final_energy_saving_by_action_type",
                "mocked_id_parameter",
                "mocked_provide_default_table",
                "mocked_years",
            )
            assert result == "mocked_result"

        def test_without_id_measure(self, sut):
            mocked_table = Mock()
            mocked_table.has_index_column = Mock(False)

            mocked_parameter_table = Mock()
            mocked_parameter_table.reduce = Mock(mocked_table)

            sut.table = Mock(mocked_parameter_table)

            with raises(ValueError):
                sut.measure_specific_parameter(
                    "mocked_final_energy_saving_by_action_type",
                    "mocked_id_parameter",
                    "mocked_provide_default_table",
                    "mocked_years",
                )

        @patch(
            DataSource._loop_over_measures_and_collect_parameters,
            "mocked_result",
        )
        def test_without_constants_table(self, sut):
            mocked_table = Mock()
            mocked_table.has_index_column = Mock(True)

            mocked_parameter_table = Mock()
            mocked_parameter_table.reduce = Mock(mocked_table)

            def mocked_table_without_constants(table_name, _query):
                if table_name == "measure_constants":
                    return None
                else:
                    return mocked_parameter_table

            sut.table = mocked_table_without_constants

            result = sut.measure_specific_parameter(
                "mocked_final_energy_saving_by_action_type",
                "mocked_id_parameter",
                "mocked_provide_default_table",
                "mocked_years",
            )
            assert result == "mocked_result"

    @patch(extrapolation.extrapolate_series)
    def test_measure_specific_parameter_using_default_table(self, sut):
        parameter_default_values = Mock()
        parameter_default_values.reduce = Mock()

        def mocked_measure_specific_parameter(
            _final_energy_saving_by_action_type,
            _id_parameter,
            provide_default_value,
        ):
            provide_default_value(
                "mocked_id_measure", "mocked_id_subsector", "mocked_id_action_type", "mocked_year", "mocked_saving"
            )
            return "mocked_result"

        sut.measure_specific_parameter = mocked_measure_specific_parameter

        final_energy_saving_by_action_type = Mock()

        result = sut.measure_specific_parameter_using_default_table(
            final_energy_saving_by_action_type,
            "mocked_id_parameter",
            parameter_default_values,
        )
        assert result == "mocked_result"

    def test_mapping_table(self, sut):
        sut._database = Mock()
        sut._database.mapping_table = Mock("mocked_result")

        result = sut.mapping_table("mocked_table_name")
        assert result == "mocked_result"

    class TestParameter:
        @patch(DataSource.table)
        @patch(extrapolation.extrapolate, "mocked_result")
        def test_without_id_region(self, sut):
            result = sut.parameter(
                "mocked_table_name",
                None,
                "mocked_id_parameter",
                "mocked_years",
            )
            assert result == "mocked_result"

        class TestWithIdRegion:
            mocked_table = Mock()
            mocked_table.reduce = Mock(ValueTable([{"id_foo": 1, "value": 10}]))

            @patch(
                DataSource.table,
                Mock(mocked_table),
            )
            def test_with_value_table(self, sut):
                result = sut.parameter(
                    "mocked_table_name",
                    "mocked_id_region",
                    "mocked_id_parameter",
                    "mocked_years",
                )
                assert result["value"][1] == 10

            class TestWithTable:
                mocked_table = Mock()
                mocked_table.reduce = Mock(Table([{"id_foo": 1, "2000": 10}]))

                @patch(
                    DataSource.table,
                    Mock(mocked_table),
                )
                @patch(
                    extrapolation.extrapolate,
                    Mock("mocked_result"),
                )
                def test_with_years(self, sut):
                    result = sut.parameter(
                        "mocked_table_name",
                        "mocked_id_region",
                        "mocked_id_parameter",
                        "mocked_years",
                    )
                    assert result == "mocked_result"

                @patch(
                    DataSource.table,
                    Mock(mocked_table),
                )
                def test_without_years(self, sut):
                    with raises(AttributeError):
                        sut.parameter(
                            "mocked_table_name",
                            "mocked_id_region",
                            "mocked_id_parameter",
                            None,
                        )

    class TestTable:
        @patch(DataSource._query_table, "mocked_result")
        def test_with_measure_table(self, sut):
            sut._user_input_measure_tables = {
                "mocked_table_name": "foo",
            }

            result = sut.table("mocked_table_name")
            assert result == "mocked_result"

        @patch(DataSource._query_table, "mocked_result")
        def test_with_global_table(self, sut):
            sut._user_input_global_tables = {
                "mocked_table_name": "foo",
            }

            result = sut.table("mocked_table_name", "mocked_where_clause")
            assert result == "mocked_result"

        @patch(DataSource._table_from_database, "mocked_table_from_database_result")
        def test_with_table_from_database(self, sut):
            result = sut.table("mocked_table_name", "mocked_where_clause")
            assert result == "mocked_table_from_database_result"

    class TestTableFromDatabase:
        def test_with_database(self, sut):
            sut._database = Mock()
            sut._database.table = Mock("mocked_result")
            result = sut._table_from_database("mocked_table_name", "mocked_where_clause")
            assert result == "mocked_result"

        def test_without_confidential_database(self, sut):
            sut._database = Mock()
            sut._database.table = Mock(side_effect=OSError("foo"))

            sut._confidential_database = None

            result = sut.table("mocked_table_name", "mocked_where_clause")
            assert result is None

        class TestWithConfidentialDatabase:
            def test_with_table(self, sut):
                sut._database = Mock()
                sut._database.table = Mock(side_effect=IOError("foo"))

                sut._confidential_database = Mock()
                sut._confidential_database.table = Mock("mocked_result")

                result = sut._table_from_database("mocked_table_name", "mocked_where_clause")
                assert result == "mocked_result"

            def test_without_table(self, sut):
                sut._database = Mock()
                sut._database.table = Mock(side_effect=IOError("foo"))

                sut._confidential_database = Mock()
                sut._confidential_database.table = Mock(side_effect=IOError("foo"))

                result = sut._table_from_database("mocked_table_name", "mocked_where_clause")
                assert result is None

    @patch(DataSource._default_annual_parameters)
    def test_annual_parameters_per_measure(self, sut):
        sut.measure_specific_parameter = _mocked_measure_specific_parameter
        mocked_provide_default_prameter = Mock()
        result = sut.annual_parameters_per_measure(
            _mocked_final_energy_savings_by_action_type(),
            "mocked_parameter_table_name",
            1,
            mocked_provide_default_prameter,
            0,
        )
        mocked_provide_default_prameter.assert_called()
        assert result["2000"][1, 2, 3] == 100


class TestPrivateApi:
    class TestCalculatedTableForMeasure:
        @patch(extrapolation.extrapolate)
        @patch(DataSource._extrapolated_final_parameters)
        @patch(DataSource._extrapolated_parameters)
        @patch(DataSource._constants)
        def test_measure_with_details(self):
            multi_index = (1, 2, 3)
            measure_ids_for_which_extra_data_exists = [1]
            measure_final_parameters = Mock()
            measure_parameters = Mock()
            measure_constants = Mock()
            determine_table_for_measure = Mock("mocked_result")

            result = DataSource._calculated_table_for_measure(
                multi_index,
                "mocked_savings",
                measure_ids_for_which_extra_data_exists,
                measure_final_parameters,
                measure_parameters,
                measure_constants,
                determine_table_for_measure,
                "mocked_provide_default_table",
                "mocked_years",
            )
            assert result == "mocked_result"

        @patch(extrapolation.extrapolate)
        def test_measure_without_details(self):
            multi_index = (1, 2, 3)
            measure_ids_for_which_extra_data_exists = [99]
            measure_final_parameters = Mock()
            measure_parameters = Mock()
            measure_constants = Mock()
            provide_default_table = Mock("mocked_result")

            result = DataSource._calculated_table_for_measure(
                multi_index,
                "mocked_savings",
                measure_ids_for_which_extra_data_exists,
                measure_final_parameters,
                measure_parameters,
                measure_constants,
                "mocked_determine_table_for_measure",
                provide_default_table,
                "mocked_years",
            )
            assert result == "mocked_result"

    class TestExtrapolatedFinalParameters:
        def test_without_parameters(self):
            result = DataSource._extrapolated_final_parameters(
                None,
                "mocked_id_measure",
                "mocked_years",
            )
            assert result is None

        @patch(extrapolation.extrapolate, "mocked_result")
        def test_without_parameters_for_measure(self):
            measure_final_parameters = Mock()
            measure_final_parameters.query = Mock(None)
            with raises(ValueError):
                DataSource._extrapolated_final_parameters(
                    measure_final_parameters,
                    "mocked_id_measure",
                    "mocked_years",
                )

        @patch(extrapolation.extrapolate, "mocked_result")
        def test_with_parameters(self):
            measure_final_parameters = Mock()
            result = DataSource._extrapolated_final_parameters(
                measure_final_parameters,
                "mocked_id_measure",
                "mocked_years",
            )
            assert result == "mocked_result"

    class TestExtrapolatedParameters:
        def test_without_parameters(self):
            result = DataSource._extrapolated_parameters(
                None,
                "mocked_id_measure",
                "mocked_years",
            )
            assert result is None

        @patch(extrapolation.extrapolate, "mocked_result")
        def test_without_parameters_for_measure(self):
            measure_parameters = Mock()
            measure_parameters.query = Mock(None)
            with raises(ValueError):
                DataSource._extrapolated_parameters(
                    measure_parameters,
                    "mocked_id_measure",
                    "mocked_years",
                )

        @patch(extrapolation.extrapolate, "mocked_result")
        def test_with_parameters(self):
            measure_parameters = Mock()
            result = DataSource._extrapolated_parameters(
                measure_parameters,
                "mocked_id_measure",
                "mocked_years",
            )
            assert result == "mocked_result"

    class TestConstants:
        def test_without_parameters(self):
            result = DataSource._constants(None, "mocked_id_measure")
            assert result is None

        def test_with_parameters(self):
            measure_constants = Mock()
            measure_constants.query = Mock("mocked_result")
            result = DataSource._constants(measure_constants, "mocked_id_measure")
            assert result == "mocked_result"

    class TestMeasureIdsForWhichExtraDataExists:
        def test_without_final_parameters(self):
            measure_parameters = Mock()
            measure_parameters.unique_index_values = Mock([2])

            measure_constants = Mock()
            measure_constants.unique_index_values = Mock([3])

            result = DataSource._measure_ids_for_which_extra_data_exists(
                None,
                measure_parameters,
                measure_constants,
            )
            assert result == [2, 3]

        def test_without_parameters(self):
            measure_final_parameters = Mock()
            measure_final_parameters.unique_index_values = Mock([1])

            measure_constants = Mock()
            measure_constants.unique_index_values = Mock([3])

            result = DataSource._measure_ids_for_which_extra_data_exists(
                measure_final_parameters,
                None,
                measure_constants,
            )
            assert result == [1, 3]

        def test_without_constants(self):
            measure_final_parameters = Mock()
            measure_final_parameters.unique_index_values = Mock([1])

            measure_parameters = Mock()
            measure_parameters.unique_index_values = Mock([2])

            result = DataSource._measure_ids_for_which_extra_data_exists(
                measure_final_parameters,
                measure_parameters,
                None,
            )
            assert result == [1, 2]

    class TestCreateGlobalTables:
        mocked_entry = {
            "table_name": "mocked_table_name",
            "id_parameter": 66,
        }

        mocked_mapping_entry = {
            "mapping": "mocked_mapping",
        }

        @patch(DataSource._map_global_parameter_tables, [mocked_entry])
        @patch(DataSource._add_table_entry, "mocked_result")
        def test_without_mapping(self, sut):
            global_parameters = {
                "mocked_sheet_name": ["mocked_json_entry"],
            }
            result = sut._create_global_tables(global_parameters)
            assert result == "mocked_result"

        @patch(DataSource._map_global_parameter_tables, [mocked_mapping_entry])
        @patch(DataSource._add_global_tables_from_mapping, "mocked_result")
        def test_with_mapping(self, sut):
            global_parameters = {
                "mocked_sheet_name": [{"id_foo": 1, "2020": 99}],
            }
            result = sut._create_global_tables(global_parameters)
            assert result == "mocked_result"

    @patch(DataSource._add_table_entry, "mocked_result")
    def test_add_global_tables_from_mapping(self, sut):
        tables = {}
        json_entry = [
            {"index": 0, "Monetisation factor": "foo", "2000": 1},
        ]

        entry = {
            "mapping": {
                "key_column_name": "Monetisation factor",
                "entries": {
                    "foo": "mocked_mapping_entry",
                },
            },
        }

        result = sut._add_global_tables_from_mapping(
            tables,
            json_entry,
            entry,
        )
        assert result == "mocked_result"

    class TestAddTableEntry:
        def test_error(self, sut):
            entry = {"table_name": "error"}
            tables = {}
            result = sut._add_table_entry(
                tables,
                "mocked_json_entry",
                entry,
            )
            assert result == tables

        @patch(DataSource._read_default_table, Table([{"id_foo": 1, "2000": 1}]))
        @patch(DataSource._create_global_table, Table([{"id_foo": 1, "2000": 2}]))
        def test_without_entry(self, sut):
            entry = {"table_name": "my_table"}
            tables = {}
            result = sut._add_table_entry(
                tables,
                "mocked_json_entry",
                entry,
            )
            table = result["my_table"]
            assert table["2000"][1] == 2

    class TestReadDefaultTable:
        @patch(DataSource._table_from_database, None)
        def test_without_table(self, sut):
            with raises(KeyError):
                sut._read_default_table("mocked_table_name", "mocked_entry")

        @patch(DataSource._table_from_database, Table([{"id_foo": 1, "2000": 1}]))
        def test_without_id_parameter(self, sut):
            with raises(KeyError):
                sut._read_default_table("mocked_table_name", "mocked_entry")

        @patch(DataSource._table_from_database, Table([{"id_parameter": 1, "2000": 1}]))
        def test_without_id_technology(self, sut):
            with raises(KeyError):
                entry = {"id_technology": 1}
                sut._read_default_table("mocked_table_name", entry)

        @patch(DataSource._table_from_database, Table([{"id_region": 0, "id_parameter": 1, "2000": 1}]))
        def test_with_id_region(self, sut):
            sut._id_region = 0
            result = sut._read_default_table("mocked_table_name", "mocked_entry")
            assert result["2000"][1] == 1

    class TestCreateGlobalTable:
        def test_for_value_table(self):
            json_array = [{"id_foo": 99, "value": 3}]
            entry = {
                "table_name": "foo",
                "id_parameter": 1,
            }
            result = DataSource._create_global_table(json_array, entry)
            assert result["value"][1, 99] == 3

        def test_without_normalization_and_technology(self):
            json_array = [{"id_foo": 99, "2000": 3}]
            entry = {
                "table_name": "foo",
                "id_parameter": 1,
            }
            result = DataSource._create_global_table(json_array, entry)
            assert result["2000"][1, 99] == 3

        def test_with_normalization(self):
            json_array = [
                {"id_primary_energy_carrier": 1, "2000": 3},
                {"id_primary_energy_carrier": 2, "2000": 3},
            ]
            entry = {
                "table_name": "foo",
                "id_parameter": 1,
                "normalization_column_names": [],
            }
            result = DataSource._create_global_table(json_array, entry)
            assert result["2000"][1, 1] == 0.5

        def test_with_technology(self):
            json_array = [{"id_foo": 99, "2000": 3}]
            entry = {
                "table_name": "foo",
                "id_parameter": 1,
                "id_technology": 4,
            }
            result = DataSource._create_global_table(json_array, entry)
            assert result["2000"][1, 4, 99] == 3

    @patch(
        DataSource._fill_measure_specific_tables,
        "mocked_result",
    )
    def test_create_measure_specific_tables(self):
        measure_specific_parameters = {
            "1": {
                "mocked_sheet_name": [{"id_foo": 11, "2020": 99}],
                "mocked_second_sheet_name": [{"id_foo": 12, "2020": 999}],
            },
        }
        result = DataSource._create_measure_specific_tables(measure_specific_parameters)
        assert result == "mocked_result"

    class TestFillMeasureSpecificTables:
        mocked_specific_table_entry = {
            "table_name": "mocked_table_name",
            "table_type": "Table",
        }

        @patch(
            DataSource._map_measure_specific_parameter_tables,
            [mocked_specific_table_entry],
        )
        def test_with_table(self):
            tables = {}
            id_measure = "1"
            json_data = {
                "mocked_sheet_name": [{"id_foo": 11, "2020": 99}],
                "mocked_second_sheet_name": [{"id_foo": 12, "2020": 999}],
            }
            result = DataSource._fill_measure_specific_tables(tables, id_measure, json_data)
            table = result["mocked_table_name"]
            assert table["2020"][1, 11] == 99

        mocked_specific_value_table_entry = {
            "table_name": "mocked_table_name",
            "table_type": "ValueTable",
        }

        @patch(
            DataSource._map_measure_specific_parameter_tables,
            [mocked_specific_value_table_entry],
        )
        def test_with_value_table(self):
            tables = {}
            id_measure = "1"
            json_data = {
                "mocked_sheet_name": [{"id_foo": 11, "value": 99}],
                "mocked_second_sheet_name": [{"id_foo": 12, "value": 999}],
            }
            result = DataSource._fill_measure_specific_tables(tables, id_measure, json_data)
            table = result["mocked_table_name"]
            assert table["value"][1, 11] == 99

    extrapolated_table = Table(
        [
            {
                "id_measure": 1,
                "2000": 99,
                "2020": 199,
            }
        ]
    )

    @patch(extrapolation.extrapolate, extrapolated_table)
    def test_extrapolated_parameter_table(self):
        id_measure = 1
        id_subsector = 2
        id_action_type = 3
        years = [2000, 2020]
        parameter_table = Table(
            [
                {
                    "id_measure": 1,
                    "2000": 99,
                }
            ]
        )

        result = DataSource._extrapolated_parameter_table(
            parameter_table,
            id_measure,
            id_subsector,
            id_action_type,
            years,
        )
        assert result["2020"][1, 2, 3] == 199

    class TestLoopOverMeasuresAndCollectParameters:
        mocked_table = Table(
            [
                {
                    "id_foo": 1,
                    "2020": 99,
                }
            ]
        )

        @patch(DataSource._table_for_measure, mocked_table)
        def test_with_table(self):
            final_energy_saving_by_action_type = Table(
                [
                    {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 0},
                ]
            )

            result = DataSource._loop_over_measures_and_collect_parameters(
                final_energy_saving_by_action_type,
                "mocked_measure_ids_for_which_extra_data_exists",
                "mocked_parameter_table",
                "mocked_provide_default_value",
                is_value_table=False,
            )
            assert result["2020"][1] == 99

        mocked_value_table = ValueTable(
            [
                {
                    "id_foo": 1,
                    "value": 99,
                }
            ]
        )

        @patch(DataSource._table_for_measure, mocked_value_table)
        def test_with_value_table(self):
            final_energy_saving_by_action_type = Table(
                [
                    {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 0},
                ]
            )

            result = DataSource._loop_over_measures_and_collect_parameters(
                final_energy_saving_by_action_type,
                "mocked_measure_ids_for_which_extra_data_exists",
                "mocked_parameter_table",
                "mocked_provide_default_value",
                is_value_table=True,
            )
            assert result["value"][1] == 99

    class TestLoopOverMeasuresAndCollectTables:
        mocked_table = Table(
            [
                {
                    "id_foo": 1,
                    "2020": 99,
                }
            ]
        )

        @patch(DataSource._calculated_table_for_measure, mocked_table)
        def test_with_table(self):
            final_energy_saving_by_action_type = Table(
                [
                    {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 0},
                ]
            )

            result = DataSource._loop_over_measures_and_collect_tables(
                final_energy_saving_by_action_type,
                "mocked_measure_ids_for_which_extra_data_exists",
                "mocked_measure_final_parameters",
                "mocked_measure_parameters",
                "mocked_measure_constants",
                "mocked_determine_table_for_measure",
                "mocked_provide_default_value",
            )
            assert result["2020"][1] == 99

        mocked_value_table = ValueTable(
            [
                {
                    "id_foo": 1,
                    "value": 99,
                }
            ]
        )

        @patch(DataSource._calculated_table_for_measure, mocked_value_table)
        def test_with_value_table(self):
            final_energy_saving_by_action_type = Table(
                [
                    {"id_measure": 1, "id_subsector": 1, "id_action_type": 1, "2020": 0},
                ]
            )

            result = DataSource._loop_over_measures_and_collect_tables(
                final_energy_saving_by_action_type,
                "mocked_measure_ids_for_which_extra_data_exists",
                "mocked_measure_final_parameters",
                "mocked_measure_parameters",
                "mocked_measure_constants",
                "mocked_determine_table_for_measure",
                "mocked_provide_default_value",
            )
            assert result["value"][1] == 99

    class TestMapMeasureSpecificParameterTables:
        def test_with_existing_name(self):
            result = DataSource._map_measure_specific_parameter_tables("parameters")
            assert result == [{"table_name": "measure_parameters", "table_type": "Table"}]

        def test_with_missing_name(self):
            with raises(KeyError):
                DataSource._map_measure_specific_parameter_tables("Unknown_Sheet_Name")

    class TestMapGlobalParameterTables:
        def test_with_existing_name(self):
            result = DataSource._map_global_parameter_tables("FuelSplitCoefficient")
            assert result == [
                {"table_name": "11_subsectoral_energy_mix_share", "id_parameter": 11},
                {"table_name": "primes_final_sector_parameters", "id_parameter": 11},
            ]

        def test_with_missing_name(self):
            with raises(KeyError):
                DataSource._map_global_parameter_tables("Unknown_Sheet_Name")

    def test_parameter_query_from_where_clause(self):
        where_clause = {
            "id_region": "0",
            "id_foo": "1",
            "id_baa": [1, 2],
        }
        result = DataSource._parameter_query_from_where_clause(where_clause)
        assert result == "id_foo == 1 and id_baa in [1, 2]"

    class TestProvideDefaultTable:
        def test_with_years(self):
            id_measure = 1
            id_subsector = 2
            id_action_type = 3
            years = [2020]
            # pylint: disable=unnecessary-lambda-assignment
            # pylint: disable=multiple-statements
            provide_default = lambda _id_measure, _id_subsector, _id_action_type, _year, _saving: 99
            savings = Mock()
            result = DataSource._provide_default_table(
                provide_default,
                id_measure,
                id_subsector,
                id_action_type,
                savings,
                years,
            )
            assert result["2020"][1, 2, 3] == 99

        def test_without_years(self):
            id_measure = 1
            id_subsector = 2
            id_action_type = 3
            # pylint: disable=unnecessary-lambda-assignment
            # pylint: disable=multiple-statements
            provide_default = lambda _id_measure, _id_subsector, _id_action_type, _savings: 99

            result = DataSource._provide_default_table(
                provide_default,
                id_measure,
                id_subsector,
                id_action_type,
                "mocked_savings",
            )
            assert result["value"][1, 2, 3] == 99

    class TestQueryTable:
        class TestWithWhereClause:
            @patch(DataSource._parameter_query_from_where_clause, "")
            def test_with_empty_query(self):
                table = Table(
                    [
                        {"id_foo": 1, "2000": 11},
                        {"id_foo": 2, "2000": 22},
                    ]
                )
                table_name = "table_name"
                tables = {
                    table_name: table,
                }
                result = DataSource._query_table(
                    table_name,
                    "mocked_where_clause",
                    tables,
                )
                assert len(result) == 2
                assert result["2000"][1] == 11
                assert result["2000"][2] == 22

            @patch(DataSource._parameter_query_from_where_clause, "id_foo==1")
            def test_with_non_empty_query(self):
                table = Table(
                    [
                        {"id_foo": 1, "2000": 11},
                        {"id_foo": 2, "2000": 22},
                    ]
                )
                table_name = "table_name"
                tables = {
                    table_name: table,
                }
                result = DataSource._query_table(
                    table_name,
                    "mocked_where_clause",
                    tables,
                )
                assert len(result) == 1
                assert result["2000"][1] == 11

        def test_without_where_clause(self):
            table = Table(
                [
                    {"id_foo": 1, "2000": 11},
                    {"id_foo": 2, "2000": 22},
                ]
            )
            table_name = "table_name"
            tables = {
                table_name: table,
            }
            result = DataSource._query_table(
                table_name,
                {},
                tables,
            )
            assert result["2000"][1] == 11
            assert result["2000"][2] == 22

    def test_row_to_json_array(self):
        row = {
            "index": 0,
            "Monetisation factor": "foo",
            "Value": 3,
        }
        key_column_name = "Monetisation factor"
        result = DataSource._row_to_json_array(row, key_column_name)
        entry = result[0]
        assert entry["value"] == 3
        assert "Monetisation factor" not in entry
        assert "index" not in entry

    class TestTableForMeasure:
        @patch(DataSource._extrapolated_parameter_table, "mocked_result")
        def test_measure_with_details(self):
            multi_index = (1, 2, 3)
            measure_ids_for_which_extra_data_exists = [1]

            result = DataSource._table_for_measure(
                multi_index,
                "mocked_savings",
                measure_ids_for_which_extra_data_exists,
                "mocked_parameter_table",
                "mocked_provide_default_table",
                "mocked_years",
            )
            assert result == "mocked_result"

        @patch(DataSource._provide_default_table, "mocked_result")
        def test_measure_without_details(self):
            multi_index = (1, 2, 3)
            measure_ids_for_which_extra_data_exists = [99]
            provide_default_table = Mock("mocked_result")

            result = DataSource._table_for_measure(
                multi_index,
                "mocked_savings",
                measure_ids_for_which_extra_data_exists,
                "mocked_parameter_table",
                provide_default_table,
                "mocked_years",
            )
            assert result == "mocked_result"

    @patch(extrapolation.extrapolate, Mock(return_value="mocked_extrapolated_parameters"))
    @patch(DataSource.table, Mock(return_value="mocked_raw_default_parameters"))
    def test_default_annual_parameters(self, sut):
        result = sut._default_annual_parameters("mocked_parameter_table_name", 1, mocked_years)
        assert result == "mocked_extrapolated_parameters"
