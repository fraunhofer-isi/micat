# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.data_import.table_validator import TableValidator
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, fixture, patch


@fixture(name="sut")
def fixture_sut():
    mocked_database = Mock()
    return TableValidator(mocked_database)


class TestCheckIfIdsArePresent:
    def test_with_equal_ids(self, sut):
        mocked_table = Mock()
        mocked_table.unique_index_values = Mock("mocked_ids")
        available_id_values = "mocked_ids"

        existing_values, missing_entries = sut._check_if_ids_are_present(
            mocked_table,
            "mocked_id_name",
            available_id_values,
            "mocked_id_table",
            "mocked_details",
        )
        assert existing_values == set("mocked_ids")
        assert missing_entries == []

    class TestWithDifferentIds:
        @patch(print)
        def test_with_empty_details(self, sut):
            mocked_table = Mock()
            mocked_table.unique_index_values = Mock(["mocked_existing_id"])
            available_id_values = ["mocked_id"]

            mocked_id_table = Mock()

            mocked_details = {}

            existing_values, missing_entries = sut._check_if_ids_are_present(
                mocked_table,
                "mocked_id_name",
                available_id_values,
                mocked_id_table,
                mocked_details,
            )
            assert existing_values == set(["mocked_existing_id"])
            assert len(missing_entries) == 1

        @patch(print)
        def test_with_details(self, sut):
            mocked_table = Mock()
            mocked_table.unique_index_values = Mock([1, 2, 3])
            available_id_values = [2, 3, 4]

            mocked_id_table = Mock()

            mocked_series = Mock()
            mocked_series.name = "mocked_series"

            mocked_id_table.get = Mock(mocked_series)

            existing_values, missing_entries = sut._check_if_ids_are_present(
                mocked_table,
                "mocked_id_name",
                available_id_values,
                mocked_id_table,
                "mocked_details",
            )
            assert existing_values == set([1, 2, 3])
            assert len(missing_entries) == 1


def test_include_missing_id_entries():
    parent_details = {
        "id_region": 1,
    }

    missing_id_entries = [33]
    missing_entries = []
    missing_entries = TableValidator._include_missing_id_entries(
        missing_entries,
        parent_details,
        "mocked_id_name",
        missing_id_entries,
    )
    assert len(missing_entries) == 1
    entry = missing_entries[0]
    assert entry["id_region"] == 1
    assert entry["mocked_id_name"] == 33


class TestValidate:
    def test_id_region(self, sut):
        sut._validate_id_region_and_below = Mock()
        table = Table(
            [
                {
                    "id_region": 1,
                    "value": 1,
                }
            ]
        )
        sut.validate(table)
        sut._validate_id_region_and_below.assert_called_once()

    def test_id_parameter(self, sut):
        sut._validate_id_parameter_and_below = Mock()
        table = Table(
            [
                {
                    "id_parameter": 1,
                    "value": 1,
                }
            ]
        )
        sut.validate(table)
        sut._validate_id_parameter_and_below.assert_called_once()

    def test_id_subsector(self, sut):
        sut._validate_id_subsector_and_below = Mock()
        table = Table(
            [
                {
                    "id_subsector": 1,
                    "value": 1,
                }
            ]
        )
        sut.validate(table)
        sut._validate_id_subsector_and_below.assert_called_once()

    def test_id_final_energy_carrier(self, sut):
        sut._validate_id_final_energy_carrier = Mock()
        table = Table(
            [
                {
                    "id_final_energy_carrier": 1,
                    "value": 1,
                }
            ]
        )
        sut.validate(table)
        sut._validate_id_final_energy_carrier.assert_called_once()

    def test_id_primary_energy_carrier(self, sut):
        sut._validate_id_primary_energy_carrier = Mock()
        table = Table(
            [
                {
                    "id_primary_energy_carrier": 1,
                    "value": 1,
                }
            ]
        )
        sut.validate(table)
        sut._validate_id_primary_energy_carrier.assert_called_once()


def test_check_if_id_is_complete(sut):
    sut._database = Mock()
    sut._database.id_table = Mock()

    sut._check_if_ids_are_present = Mock("mocked_result")

    result = sut._check_if_id_is_complete(
        "mocked_table",
        "mocked_id_name",
        "mocked_description",
    )
    assert result == "mocked_result"


def test_action_type_ids(sut):
    sut._database = Mock()

    mocked_mapping_table = Mock()
    mocked_mapping_table.target_ids = Mock("mocked_result")

    sut._database.mapping_table = Mock(mocked_mapping_table)
    result = sut._action_type_ids("mocked_id_subsector")
    assert result == "mocked_result"


class TestIncludeMissingSubEntriesForSubsector:
    @patch(TableValidator._action_type_ids, ["mocked_action_type_id"])
    @patch(
        TableValidator._include_missing_sub_entries_for_action_type,
        "mocked_result",
    )
    def test_with_id_action_type(self, sut):
        mocked_id_table = Mock()
        mocked_id_table.label = Mock()

        sut._database.id_table = Mock(mocked_id_table)
        missing_entries = []
        mocked_parent_details = {}
        id_column_names = ["id_action_type"]

        result = sut._include_missing_sub_entries_for_subsector(
            missing_entries,
            "mocked_id_subsector",
            mocked_parent_details,
            id_column_names,
        )

        assert result == "mocked_result"

    @patch(
        TableValidator._include_missing_sub_entries_for_action_type,
        "mocked_result",
    )
    def test_without_id_action_type(self, sut):
        missing_entries = []
        mocked_parent_details = {}
        id_column_names = []

        result = sut._include_missing_sub_entries_for_subsector(
            missing_entries,
            "mocked_id_subsector",
            mocked_parent_details,
            id_column_names,
        )

        assert result == "mocked_result"


class TestIncludeMissingSubEntriesForActionType:
    def test_with_id_final_energy_carrier(self, sut):
        mocked_id_table = Mock()
        mocked_id_table.id_values = ["mocked_id_value"]
        mocked_id_table.label = Mock()
        sut._database.id_table = Mock(mocked_id_table)

        missing_entries = []
        parent_details = {}
        id_column_names = ["id_final_energy_carrier"]
        result = sut._include_missing_sub_entries_for_action_type(
            missing_entries,
            parent_details,
            id_column_names,
        )

        assert len(result) == 1

    def test_with_id_primary_energy_carrier(self, sut):
        mocked_id_table = Mock()
        mocked_id_table.id_values = ["mocked_id_value"]
        mocked_id_table.label = Mock()
        sut._database.id_table = Mock(mocked_id_table)

        missing_entries = []
        parent_details = {}
        id_column_names = ["id_primary_energy_carrier"]
        result = sut._include_missing_sub_entries_for_action_type(
            missing_entries,
            parent_details,
            id_column_names,
        )

        assert len(result) == 1


class TestValidateIdActionTypeAndBelow:
    def test_with_extra_columns(self, sut):
        sut._database = Mock()
        sut._database.id_table = Mock()

        sut._check_if_ids_are_present = Mock((["mocked_id"], [(0, "mocked_missing_id")]))

        sut._include_missing_sub_entries_for_action_type = Mock()
        sut.validate = Mock("mocked_missing_entries")

        mocked_table = Mock()
        mocked_table.column_names = (["id_foo", "id_baa"], ["2000"], [])
        mocked_parent_details = {}

        result = sut._validate_id_action_type_and_below(
            mocked_table,
            "mocked_available_id_values",
            mocked_parent_details,
            "mocked_id_column_names",
            "mocked_missing_entries",
        )
        assert result == "mocked_missing_entries"


@patch(
    TableValidator._check_if_id_is_complete,
    ([], []),
)
@patch(
    TableValidator._include_missing_id_entries,
    "mocked_result",
)
def test_validate_id_final_energy_carrier(sut):
    missing_entries = []
    result = sut._validate_id_final_energy_carrier(
        "mocked_table",
        "mocked_details",
        missing_entries,
    )
    assert result == "mocked_result"


@patch(
    TableValidator._check_if_id_is_complete,
    ([], []),
)
@patch(
    TableValidator._include_missing_id_entries,
    "mocked_result",
)
def test_validate_id_primary_energy_carrier(sut):
    missing_entries = []
    result = sut._validate_id_primary_energy_carrier(
        "mocked_table",
        "mocked_details",
        missing_entries,
    )
    assert result == "mocked_result"


class TestValidateIdRegionAndBelow:
    @patch(
        TableValidator._include_missing_id_entries,
        "mocked_result",
    )
    def test_only_with_id_region(self, sut):
        sut._check_if_id_is_complete = Mock((["mocked_id_region"], []))
        sut.validate = Mock()

        mocked_table = Mock()
        mocked_table.column_names = (["id_region"], [], [])
        mocked_table.reduce = Mock()

        result = sut._validate_id_region_and_below(
            mocked_table,
            "mocked_parent_details",
            "mocked_missing_entries",
        )

        sut._check_if_id_is_complete.assert_called_once()
        mocked_table.reduce.assert_not_called()

        assert result == "mocked_result"

    class TestWithMoreIdColumns:
        def test_with_used_id(self, sut):
            mocked_id_table = Mock()
            mocked_id_table.id_values = ["mocked_id_region"]
            sut._database.id_table = Mock(mocked_id_table)

            sut._check_if_id_is_complete = Mock((["mocked_id_region"], []))
            sut.validate = Mock()

            mocked_table = Mock()
            mocked_table.column_names = (["id_region", "id_foo"], [], [])
            mocked_table.reduce = Mock()
            sut._validate_id_region_and_below(
                mocked_table,
                {},
                "mocked_missing_entries",
            )

            sut._check_if_id_is_complete.assert_called_once()
            mocked_table.reduce.assert_called_once()

        @patch(print)
        def test_with_unused_id(self, sut):
            mocked_id_table = Mock()
            mocked_id_table.id_values = ["mocked_available_id_region"]
            sut._database.id_table = Mock(mocked_id_table)

            sut._check_if_id_is_complete = Mock((["mocked_id_region"], []))
            sut.validate = Mock()

            mocked_table = Mock()
            mocked_table.column_names = (["id_region", "id_foo"], [], [])
            mocked_table.reduce = Mock()
            sut._validate_id_region_and_below(
                mocked_table,
                "mocked_parent_details",
                "mocked_missing_entries",
            )

            sut._check_if_id_is_complete.assert_called_once()
            mocked_table.reduce.assert_not_called()


class TestValidateIdParameterAndBelow:
    def test_only_with_id_parameter(self, sut):
        sut._check_if_id_is_complete = Mock(["mocked_id_region"])
        sut.validate = Mock("mocked_result")

        mocked_table = Mock()
        mocked_table.unique_index_values = Mock(["mocked_id_parameter"])

        mocked_series = AnnualSeries({"2000": 1})

        mocked_table.reduce = Mock(mocked_series)

        result = sut._validate_id_parameter_and_below(
            mocked_table,
            Mock(),
            "mocked_missing_entries",
        )

        sut.validate.assert_not_called()
        assert result == "mocked_missing_entries"

    def test_with_more_id_columns(self, sut):
        sut._check_if_id_is_complete = Mock(["mocked_id_region"])
        sut.validate = Mock("mocked_result")

        mocked_table = Mock()
        mocked_table.unique_index_values = Mock(["mocked_id_parameter"])

        mocked_parameter_table = Table([{"id_foo": 1, "2000": 1}])

        mocked_table.reduce = Mock(mocked_parameter_table)

        mocked_parent_details = {}

        result = sut._validate_id_parameter_and_below(
            mocked_table,
            mocked_parent_details,
            "mocked_missing_entries",
        )

        sut.validate.assert_called_once()

        assert result == "mocked_result"


class TestValidateIdSubsectorAndBelow:
    class TestWithUsedIdSubsector:
        def test_with_id_action_type(self, sut):
            mocked_id_table = Mock()
            mocked_id_table.id_values = ["mocked_id_sector"]
            sut._database.id_table = Mock(mocked_id_table)

            sut._check_if_id_is_complete = Mock((["mocked_id_sector"], []))

            mocked_table = Mock()
            mocked_table.reduce = Mock()

            sut._action_type_ids = Mock()
            sut._validate_id_action_type_and_below = Mock()

            id_column_names = ["id_subsector", "id_action_type"]

            mocked_parent_details = {}

            sut._validate_id_subsector_and_below(
                mocked_table,
                mocked_parent_details,
                "mocked_missing_entries",
                id_column_names,
            )

            sut._validate_id_action_type_and_below.assert_called_once()

        class TestWithoutIdActionType:
            @patch(TableValidator._include_missing_id_entries, "mocked_result")
            def test_only_with_id_subsector(self, sut):
                mocked_id_table = Mock()
                mocked_id_table.id_values = ["mocked_id_sector"]
                sut._database.id_table = Mock(mocked_id_table)

                sut._check_if_id_is_complete = Mock((["mocked_id_sector"], []))

                mocked_table = Mock()

                mocked_subsector_table = AnnualSeries({"2000": 1})

                mocked_table.reduce = Mock(mocked_subsector_table)

                id_column_names = ["id_subsector"]

                sut.validate = Mock()

                mocked_parent_details = {}

                result = sut._validate_id_subsector_and_below(
                    mocked_table,
                    mocked_parent_details,
                    "mocked_missing_entries",
                    id_column_names,
                )

                sut.validate.assert_not_called()

                assert result == "mocked_result"

            def test_with_more_id_columns(self, sut):
                mocked_id_table = Mock()
                mocked_id_table.id_values = ["mocked_id_sector"]
                sut._database.id_table = Mock(mocked_id_table)

                sut._check_if_id_is_complete = Mock((["mocked_id_sector"], []))

                mocked_table = Mock()

                mocked_subsector_table = Mock()
                mocked_subsector_table.column_names = (["id_foo"], [])

                mocked_table.reduce = Mock(mocked_subsector_table)

                id_column_names = ["id_subsector"]

                sut.validate = Mock("mocked_result")

                mocked_parent_details = {}

                result = sut._validate_id_subsector_and_below(
                    mocked_table,
                    mocked_parent_details,
                    "mocked_missing_entries",
                    id_column_names,
                )

                sut.validate.assert_called_once()

                assert result == "mocked_result"

    @patch(
        TableValidator._include_missing_sub_entries_for_subsector,
        "mocked_result",
    )
    def test_with_unused_id_subsector(self, sut):
        mocked_id_table = Mock()
        mocked_id_table.id_values = ["mocked_id_sector"]
        sut._database.id_table = Mock(mocked_id_table)

        sut._check_if_id_is_complete = Mock((["mocked_existing_id_sector"], []))

        id_column_names = ["id_subsector", "id_action_type"]

        mocked_parent_details = {}

        result = sut._validate_id_subsector_and_below(
            "mocked_table",
            mocked_parent_details,
            "mocked_missing_entries",
            id_column_names,
        )

        assert result == "mocked_result"
