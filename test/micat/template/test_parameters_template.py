# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
# pylint: disable=unused-variable

import io

import pandas as pd

from micat import utils
from micat.table import table
from micat.template import (
    database_utils,
    mocks,
    parameters_template,
    validators,
    xlsx_utils,
)
from micat.test_utils.isi_mock import Mock, patch

mocked_database_in_args = mocks.mocked_database()
mocked_columns = ["id", "label", "description"]
mocked_row = ["mocked_id", "mocked_label", "mocked_description"]
mocked_template_args = mocks.mocked_template_args()


@patch(
    parameters_template._template_args,
    "mocked_template_args",
)
@patch(
    parameters_template._parameters_template,
    "mocked_result",
)
def test_parameters_template():
    result = parameters_template.parameters_template(
        "mocked_request",
        "mocked_database",
    )
    assert result == "mocked_result"


@patch(
    utils.api.parse_request,
    {"id_mode": "1", "id_region": "2"},
)
def test_template_args():
    result = parameters_template._template_args(Mock())
    assert result["id_mode"] == 1
    assert result["id_region"] == 2


@patch(io.BytesIO, "mocked_io")
@patch(
    xlsx_utils.empty_workbook,
    mocks.mocked_workbook(),
)
@patch(parameters_template._subsector_final_create_parameter_sheet)
@patch(parameters_template._primary_create_parameter_sheet)
@patch(parameters_template._monetization_create_parameter_sheet)
@patch(parameters_template._create_options_sheet)
class TestParametersTemplate:
    def test_true_condition(self):
        mocked_args = {
            "coefficient_sheets": ["FuelSplitCoefficient", "ElectricityGeneration", "MonetisationFactors"],
            "years": [2015, 2016],
            "id_mode": 1,
            "id_region": 2,
            "id_subsector": 3,
        }
        mocked_database = Mock()
        mocked_database.id_table = Mock()

        output = parameters_template._parameters_template(
            mocked_args,
            mocked_database,
        )
        assert output == "mocked_io"

    def test_false_condition(self):
        mocked_args = {
            "coefficient_sheets": ["mocked_sheet_name3", "mocked_sheet_name4"],
            "years": [2015, 2016],
        }
        mocked_database = Mock()
        mocked_database.id_table = Mock()

        output = parameters_template._parameters_template(
            mocked_args,
            mocked_database,
        )
        assert output != "not_mocked_io"


@patch(parameters_template._add_parameters_header)
@patch(parameters_template._monetization_add_parameters_data_validation)
@patch(parameters_template._write_data_to_sheet, Mock())
@patch(table.Table, Mock())
def test_monetization_create_parameter_sheet():
    mocked_workbook = Mock()
    with patch(parameters_template._monetization_parameters_table) as mocked_monetization_parameter_table:
        parameters_template._monetization_create_parameter_sheet(
            mocked_workbook,
            "MonetizationParameters",
            mocked_template_args,
            "mocked_database",
        )
        mocked_monetization_parameter_table.assert_called_once()


mocked_dataframe = Mock()
mocked_dataframe.fillna = Mock(return_value="mocked_monetization_parameter_table")


@patch(database_utils.parameter_table, "mocked_parameter_table")
@patch(parameters_template._construct_monetization_parameter_table, Mock(return_value=mocked_dataframe))
def test_monetization_parameters_table():
    result = parameters_template._monetization_parameters_table("mocked_database", 0, 0)
    assert result == "mocked_monetization_parameter_table"


def test_construct_monetization_parameter_table():
    def _mocked_monetization_parameter_table(value):
        mocked_monetization_parameter_table = pd.DataFrame(
            [{"Parameter": "mocked_parameter_" + str(value), "value": value}]
        )
        return mocked_monetization_parameter_table

    mocked_table = Mock()
    mocked_table.to_data_frame = Mock(
        side_effect=[_mocked_monetization_parameter_table(1), _mocked_monetization_parameter_table(2)]
    )
    mocked_parameter_tables = {
        "mocked_parameter_1": mocked_table,
        "mocked_parameter_2": mocked_table,
    }
    result = parameters_template._construct_monetization_parameter_table(mocked_parameter_tables)
    assert result.loc[0, "Value"] == 1
    assert result.loc[1, "Value"] == 2


@patch(parameters_template._add_parameters_header)
@patch(parameters_template._subsector_final_add_parameters_data_validation)
def test_subsector_final_create_parameter_sheet():
    mocked_workbook = mocks.mocked_workbook()

    with patch(parameters_template._subsector_final_add_parameter_data) as mocked_add_data:
        parameters_template._subsector_final_create_parameter_sheet(
            mocked_workbook,
            "mocked_sheet_name",
            mocked_template_args,
            "mocked_database",
            "mocked_id_subsector_table",
            "mocked_id_final_energy_carrier_table",
        )

        mocked_add_data.assert_called_once()


@patch(parameters_template._add_parameters_header)
@patch(parameters_template._primary_add_parameters_data_validation)
class TestPrimaryCreateParameterSheet:
    def test_true_sheet_name(
        self,
    ):
        mocked_workbook = Mock()
        with patch(parameters_template._primary_add_parameter_data) as mocked_add_data:
            parameters_template._primary_create_parameter_sheet(
                mocked_workbook,
                "ElectricityGeneration",
                mocked_template_args,
                "mocked_database",
                "mocked_id_primary_energy_carrier_table",
            )
            mocked_add_data.assert_called_once()

    def test_false_sheet_name(
        self,
    ):
        mocked_workbook = Mock()

        with patch(parameters_template._primary_add_parameter_data) as mocked_add_data:
            parameters_template._primary_create_parameter_sheet(
                mocked_workbook,
                "HeatGeneration",
                mocked_template_args,
                "mocked_database",
                "mocked_id_primary_energy_carrier_table",
            )

            mocked_add_data.assert_called_once()


@patch(xlsx_utils.protect_sheet)
def test_create_options_sheet():
    mocked_workbook = mocks.mocked_workbook()

    mocked_id_subsector_table = Mock()
    mocked_id_final_energy_carrier_table = Mock()
    mocked_id_primary_energy_carrier_table = Mock()

    result = parameters_template._create_options_sheet(
        mocked_workbook,
        mocked_template_args,
        mocked_id_subsector_table,
        mocked_id_final_energy_carrier_table,
        mocked_id_primary_energy_carrier_table,
    )
    assert mocked_workbook.add_worksheet.called
    assert result.write_column.call_count == 3
    assert result.set_column.called


def test_add_parameters_header():
    mocked_parameters_sheet = mocks.mocked_sheet()
    mocked_workbook = mocks.mocked_workbook()

    with patch(parameters_template._header_format) as mocked_header_format:
        parameters_template._add_parameters_header(mocked_parameters_sheet, mocked_workbook, ["mocked_header_column"])
        assert mocked_header_format.called
        assert mocked_workbook.add_format.called
        assert mocked_parameters_sheet.set_row.called
        assert mocked_parameters_sheet.write_row.called


@patch(validators.exact_string_validator)
@patch(validators.year_header_validator)
@patch(validators.parameter_cell_validator)
@patch(validators.subsector_list_dropdown_validator)
@patch(validators.final_energy_carrier_list_dropdown_validator)
def test_subsector_final_add_parameters_data_validation(*args):
    mocked_parameters_sheet = mocks.mocked_sheet()

    parameters_template._subsector_final_add_parameters_data_validation(
        mocked_parameters_sheet,
        "mocked_sheet_name",
        "mocked_id_mode",
        "mocked_id_subsectors_table",
        "mocked_id_final_energy_carriers_table",
    )

    assert mocked_parameters_sheet.data_validation.call_count == 6
    for arg in args:
        assert arg.called


@patch(database_utils.column_names)
@patch(database_utils.filter_column_names_by_id_mode)
@patch(database_utils.table)
@patch(parameters_template._subsector_final_reorder_and_rename_columns)
@patch(parameters_template._write_data_to_sheet)
def test_subsector_final_add_parameter_data(*args):  # pylint: disable=unused-argument
    mocked_sheet = mocks.mocked_sheet()

    result = parameters_template._subsector_final_add_parameter_data(
        mocked_sheet,
        "mocked_database",
        "mocked_table_name",
        "mocked_id_mode",
        "mocked_id_region",
        "mocked_id_parameter",
        "mocked_id_subsector_table",
        "mocked_id_final_energy_carrier_table",
    )

    assert result is not None


@patch(validators.exact_string_validator)
@patch(validators.year_header_validator)
@patch(validators.parameter_cell_validator)
@patch(validators.primary_energy_carrier_list_dropdown_validator)
def test_primary_add_parameters_data_validation(*args):
    mocked_parameters_sheet = mocks.mocked_sheet()

    parameters_template._primary_add_parameters_data_validation(
        mocked_parameters_sheet,
        "mocked_sheet_name",
        "mocked_id_mode",
        "mocked_id_primary_energy_carriers_table",
    )

    assert mocked_parameters_sheet.data_validation.call_count == 4
    for arg in args:
        assert arg.called


@patch(validators.exact_string_validator)
@patch(validators.year_header_validator)
@patch(validators.parameter_cell_validator)
def test_monetization_add_parameters_data_validation(*args):
    mocked_parameters_sheet = mocks.mocked_sheet()

    parameters_template._monetization_add_parameters_data_validation(
        mocked_parameters_sheet,
        "mocked_id_mode",
    )

    assert mocked_parameters_sheet.data_validation.call_count == 4
    for arg in args:
        assert arg.called


@patch(database_utils.column_names)
@patch(database_utils.filter_column_names_by_id_mode)
@patch(database_utils.table)
@patch(parameters_template._primary_reorder_and_rename_columns)
@patch(parameters_template._write_data_to_sheet)
def test_primary_add_parameter_data(*args):  # pylint: disable=unused-argument
    mocked_sheet = mocks.mocked_sheet()

    result = parameters_template._primary_add_parameter_data(
        mocked_sheet,
        "mocked_database",
        "mocked_table_name",
        "mocked_id_mode",
        "mocked_id_region",
        "mocked_id_parameter",
        "mocked_id_primary_energy_carrier_table",
    )

    assert result is not None


def test_subsector_final_reorder_and_rename_columns():
    mocked_data_table = Mock()
    mocked_data_table.columns = Mock()
    mocked_data_table.columns.insert = Mock()
    mocked_data_table.rename = Mock()
    result = parameters_template._subsector_final_reorder_and_rename_columns(mocked_data_table)
    assert mocked_data_table.columns.insert.call_count == 2  # pylint: disable=no-member
    assert result.rename.called


def test_primary_reorder_and_rename_columns():
    mocked_data_table = Mock()
    mocked_data_table.columns = Mock()
    mocked_data_table.columns.insert = Mock()
    mocked_data_table.rename = Mock()
    result = parameters_template._primary_reorder_and_rename_columns(mocked_data_table)
    assert mocked_data_table.columns.insert.call_count == 1  # pylint: disable=no-member
    assert result.rename.called


def test_write_data_to_sheet():
    mocked_sheet = mocks.mocked_sheet()
    mocked_data_table = Mock()
    mocked_data_table.to_numpy_with_headers = Mock([[1, 2], [3, 4]])
    parameters_template._write_data_to_sheet(mocked_sheet, mocked_data_table)
    assert mocked_sheet.write.call_count == 4


def test_header_format():
    assert len(parameters_template._header_format()) == 3
