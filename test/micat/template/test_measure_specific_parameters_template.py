# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import math

import numpy as np

from micat.calculation import extrapolation
from micat.calculation.ecologic import fuel_split
from micat.calculation.economic import investment, population
from micat.calculation.social import dwelling
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table
from micat.template import measure_specific_parameters_template
from micat.test_utils.isi_mock import Mock, patch
from micat.utils import api


@patch(
    measure_specific_parameters_template._template_args,
    {
        "measure": {
            "id": 1,
            "2000": 0,
            "2010": 10,
            "subsector": {
                "id": 2,
                "name": "mocked_subsector_name",
            },
            "action_type": {
                "id": 3,
                "name": "mocked_action_type_name",
            },
            "unit": {
                "symbol": "mocked_unit_symbol",
            },
        },
        "id_region": 1,
        "id_subsector": 2,
        "id_action_type": 3,
        "id_mode": 1,
        "global_parameters": {},
    },
)
@patch(
    investment.investment_cost_in_euro,
    Table(
        [
            {"id_parameter": 1, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 2, "id_region": 1, 2000: 0.4, 2010: 0.5, 2020: 0.6},
        ]
    ),
)
@patch(
    fuel_split.fuel_split_by_action_type,
    Table(
        [
            {"id_parameter": 1, "id_region": 1, "id_final_energy_carrier": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 2, "id_region": 1, "id_final_energy_carrier": 2, 2000: 0.4, 2010: 0.5, 2020: 0.6},
            {"id_parameter": 3, "id_region": 1, "id_final_energy_carrier": 3, 2000: 0.7, 2010: 0.8, 2020: 0.9},
        ]
    ),
)
@patch(
    measure_specific_parameters_template._wuppertal_parameters,
    Table(
        [
            {"id_parameter": 31, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 25, "id_region": 1, 2000: 0.4, 2010: 0.5, 2020: 0.6},
            {"id_parameter": 35, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
            {"id_parameter": 29, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
            {"id_parameter": 34, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
        ]
    ),
)
@patch(
    dwelling.number_of_affected_dwellings,
    Table(
        [
            {"id_parameter": 1, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 2, "id_region": 1, 2000: 0.4, 2010: 0.5, 2020: 0.6},
            {"id_parameter": 3, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
        ]
    ),
)
@patch(dwelling.dwelling_stock, Table([{"id_parameter": 1, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3}]))
def test_measure_specific_parameters_template():
    data_source = Mock()
    data_source.table.return_value = Table(
        [
            {"id_parameter": 1, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 2, "id_region": 1, 2000: 0.4, 2010: 0.5, 2020: 0.6},
            {"id_parameter": 3, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
        ]
    )
    result = measure_specific_parameters_template.measure_specific_parameters_template(
        "mocked_request",
        data_source,
        data_source,
    )
    assert list(result.keys()) == ["affectedFuels", "residential", "fuelSwitch", "context", "main"]


@patch(population.population_of_municipality)
@patch(measure_specific_parameters_template._final_energy_saving_by_action_type)
@patch(measure_specific_parameters_template._wuppertal_parameters)
@patch(measure_specific_parameters_template._get_main_data)
@patch(measure_specific_parameters_template._get_fuel_data)
@patch(measure_specific_parameters_template._get_fuel_switch_data)
@patch(measure_specific_parameters_template._get_residential_data)
def test_get_measure_specific_data():
    data_source = Mock()

    measure_specific_parameters_template._get_measure_specific_data(
        {
            "measure": {
                "id": 1,
                "2000": 0,
                "2010": 10,
                "subsector": {
                    "id": 2,
                    "name": "mocked_subsector_name",
                },
                "action_type": {
                    "id": 3,
                    "name": "mocked_action_type_name",
                },
                "unit": {
                    "symbol": "mocked_unit_symbol",
                },
            },
            "id_region": 1,
            "id_subsector": 2,
            "id_action_type": 3,
            "id_mode": 1,
            "global_parameters": {},
        },
        data_source,
        data_source,
    )


@patch(extrapolation.extrapolate, "mocked_result")
def test_wuppertal_parameters():
    context = Mock()
    final_energy_saving_by_action_type = Mock()
    data_source = Mock()

    result = measure_specific_parameters_template._wuppertal_parameters(
        context,
        final_energy_saving_by_action_type,
        data_source,
    )
    assert result == "mocked_result"


@patch(measure_specific_parameters_template._interpolate_annual_data)
@patch(measure_specific_parameters_template._fill_unit)
def test_get_main_data():
    final_energy_saving_by_action_type = Mock()
    data_source = Mock()
    wuppertal_parameters = Mock()

    res = measure_specific_parameters_template._get_main_data(
        {
            "unit": {"symbol": "mocked_unit_symbol"},
            "id_region": 1,
            "id_subsector": 2,
            "id_action_type": 3,
            "id_measure": 4,
        },
        final_energy_saving_by_action_type,
        wuppertal_parameters,
        data_source,
    )
    assert len(res) == 4


def test_get_fuel_switch_data():
    data_source = Mock()
    data_source.table.return_value = Table(
        [
            {"id_parameter": 1, "id_region": 1, 2000: 0.1, 2010: 0.2, 2020: 0.3},
            {"id_parameter": 2, "id_region": 1, 2000: 0.4, 2010: 0.5, 2020: 0.6},
            {"id_parameter": 3, "id_region": 1, 2000: 0.7, 2010: 0.8, 2020: 0.9},
        ]
    )
    res = measure_specific_parameters_template._get_fuel_switch_data(
        [2000, 2010, 2020],
        "mocked_context",
        data_source,
    )

    assert len(res) == 3


def test_get_residential_data():
    final_energy_saving_by_action_type = Mock()
    context = Mock()
    data_source = Mock()
    wuppertal_parameters = Mock()
    res = measure_specific_parameters_template._get_residential_data(
        context,
        final_energy_saving_by_action_type,
        wuppertal_parameters,
        data_source,
    )

    assert len(res) == 7


def test_annual_columns():
    mocked_cell = Mock()
    mocked_cell.value = "foo"

    mocked_annual_cell = Mock()
    mocked_annual_cell.value = 2000

    mocked_columns = [[mocked_cell], [mocked_annual_cell]]

    sheet = Mock()
    sheet.columns = mocked_columns
    result = measure_specific_parameters_template._annual_columns(sheet)
    assert len(result) == 1
    assert result[0][0].value == 2000


def test_cell_style():
    cell = Mock()
    cell._style = "mocked_style"
    result = measure_specific_parameters_template._cell_style(cell)
    assert result == "mocked_style"


class TestCellValue:
    def test_with_na(self):
        cell = Mock()
        cell.value = "=NA()"
        result = measure_specific_parameters_template._cell_value(cell)
        assert math.isnan(result)

    def test_normal_usage(self):
        cell = Mock()
        cell.value = 33
        result = measure_specific_parameters_template._cell_value(cell)
        assert result == 33


@patch(
    measure_specific_parameters_template._cell_value,
    "mocked_cell_value",
)
def test_columns_to_table():
    mocked_column = ["header", "cell"]
    columns = [
        mocked_column,
        mocked_column,
    ]
    result = measure_specific_parameters_template._columns_to_table(columns)
    assert result["mocked_cell_value"][0] == "mocked_cell_value"


@patch(measure_specific_parameters_template._cell_value, "mocked_cell_value")
def test_extrapolated_nan_table():
    raw_annual_table = Table([{"id_foo": 1, "2010": 1, "2030": 3}])
    years = [2010, 2020, 2030]
    result = measure_specific_parameters_template._extrapolated_nan_table(raw_annual_table, years)
    assert len(result) == 1
    assert np.isnan(result["2010"][0])
    assert np.isnan(result["2020"][0])
    assert np.isnan(result["2030"][0])


def test_fill_annual_data():
    sheet = Mock()
    annual_table = Table([{"id_foo": 1, "2000": 10}])
    cell_styles = Mock()
    measure_specific_parameters_template._fill_annual_data(sheet, annual_table, cell_styles)
    sheet.cell.assert_called()


class TestFillAnnualSeries:
    def test_with_table(self):
        sheet = Mock()
        start_column_index = 2
        row_index = 3
        series_or_table = Table([{"id_foo": 1, "2000": 10}])
        measure_specific_parameters_template._fill_annual_series(
            sheet,
            start_column_index,
            row_index,
            series_or_table,
        )

        sheet.cell.assert_called()

    def test_with_series(self):
        sheet = Mock()
        start_column_index = 2
        row_index = 3
        series_or_table = AnnualSeries({"2000": 10})
        measure_specific_parameters_template._fill_annual_series(
            sheet,
            start_column_index,
            row_index,
            series_or_table,
        )

        sheet.cell.assert_called()


def test_fill_table():
    sheet = Mock()
    start_column_index = 2
    start_row_index = 3
    table = Table(
        [
            {"id_foo": 1, "id_baa": 1, "2000": 1, "2020": 2},
            {"id_foo": 1, "id_baa": 2, "2000": 10, "2020": 20},
        ]
    )
    measure_specific_parameters_template._fill_table(sheet, start_column_index, start_row_index, table)
    sheet.cell.assert_called()


def test_lifetime():
    context = Mock()

    mocked_table = Mock()
    mocked_table.reduce = Mock("mocked_result")

    database = Mock()
    database.table = Mock(mocked_table)
    result = measure_specific_parameters_template._lifetime(
        context,
        database,
    )
    assert result == "mocked_result"


def test_fill_unit():
    sheet = {}
    context = {"unit": {"symbol": "mocked_unit_symbol"}}
    result = measure_specific_parameters_template._fill_unit(sheet, context)
    assert result["D2"] == "mocked_unit_symbol"


class TestInterpolateAnnualData:
    @patch(extrapolation.extrapolate)
    @patch(measure_specific_parameters_template._fill_annual_data, "mocked_result")
    def test_with_non_nan(self):
        mocked_raw_annual_table = Mock()
        mocked_raw_annual_table.contains_non_nan = Mock(True)
        mocked_parts = (
            "mocked_sheet_without_annual_data",
            mocked_raw_annual_table,
            "mocked_cell_style",
        )

        with patch(measure_specific_parameters_template._split_sheet, mocked_parts):
            result = measure_specific_parameters_template._interpolate_annual_data(
                "mocked_sheet",
                Mock(),
            )
            assert result == "mocked_result"

    @patch(measure_specific_parameters_template._extrapolated_nan_table)
    @patch(measure_specific_parameters_template._fill_annual_data, "mocked_result")
    def test_without_non_nan(self):
        mocked_raw_annual_table = Mock()
        mocked_raw_annual_table.contains_non_nan = Mock(False)
        mocked_parts = (
            "mocked_sheet_without_annual_data",
            mocked_raw_annual_table,
            "mocked_cell_style",
        )

        with patch(measure_specific_parameters_template._split_sheet, mocked_parts):
            result = measure_specific_parameters_template._interpolate_annual_data(
                "mocked_sheet",
                Mock(),
            )
            assert result == "mocked_result"


def test_final_energy_saving_by_action_type():
    measure = {
        "id": 1,
        "2000": 0,
        "2010": 10,
    }
    context = {
        "id_subsector": 2,
        "id_action_type": 3,
    }
    result = measure_specific_parameters_template._final_energy_saving_by_action_type(
        measure,
        context,
    )

    assert result["2000"][1, 2, 3] == 0
    assert result["2010"][1, 2, 3] == 10


@patch(measure_specific_parameters_template._annual_columns)
@patch(measure_specific_parameters_template._columns_to_table)
def test_split_sheet():
    sheet = Mock()
    result = measure_specific_parameters_template._split_sheet(sheet)
    assert len(result) == 3


@patch(
    api.parse_request,
    {"id_mode": "1", "id_region": "2", "id_subsector": "1", "json": {}},
)
def test_template_args():
    result = measure_specific_parameters_template._template_args("mocked_request")
    assert result["id_mode"] == "1"
    assert result["id_region"] == "2"
