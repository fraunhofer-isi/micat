# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import io
import math

import numpy as np
from test_utils.mock import Mock, patch, patch_by_string

from calculation import extrapolation
from calculation.ecologic import fuel_split
from calculation.economic import investment, population
from calculation.social import dwelling
from series.annual_series import AnnualSeries
from table.table import Table
from template import measure_specific_parameters_template
from utils import api


@patch(
    measure_specific_parameters_template._template_args,
    'mocked_template_args',
)
@patch(
    measure_specific_parameters_template._measure_specific_template,
    'mocked_result',
)
def test_measure_specific_parameters_template():
    result = measure_specific_parameters_template.measure_specific_parameters_template(
        'mocked_request',
        'mocked_database',
        'mocked_confidential_database',
    )
    assert result == 'mocked_result'


@patch(measure_specific_parameters_template._fill_measure_specific_template)
@patch(io.BytesIO, 'mocked_result')
def test_measure_specific_template():
    mocked_template_args = {
        'measure': 'mocked_measure',
    }
    with patch_by_string('openpyxl.load_workbook', Mock()) as mocked_load_workbook:
        result = measure_specific_parameters_template._measure_specific_template(
            mocked_template_args,
            'mocked_database',
            'mocked_confidential_database',
        )
        mocked_load_workbook.assert_called_once()
        assert result == 'mocked_result'


@patch(population.population_of_municipality)
@patch(measure_specific_parameters_template._final_energy_saving_by_action_type)
@patch(measure_specific_parameters_template._wuppertal_parameters)
@patch(measure_specific_parameters_template._fill_main_sheet)
@patch(measure_specific_parameters_template._fill_fuel_switch_sheet)
@patch(measure_specific_parameters_template._fill_residential_sheet)
@patch(measure_specific_parameters_template._fill_context_sheet)
def test_fill_measure_specific_template():
    workbook = Mock()
    template_args = Mock()

    measure_specific_parameters_template._fill_measure_specific_template(
        workbook,
        template_args,
        'mocked_database',
        'mocked_confidential_database',
    )


@patch(extrapolation.extrapolate, 'mocked_result')
def test_wuppertal_parameters():
    context = Mock()
    final_energy_saving_by_action_type = Mock()
    data_source = Mock()

    result = measure_specific_parameters_template._wuppertal_parameters(
        context,
        final_energy_saving_by_action_type,
        data_source,
    )
    assert result == 'mocked_result'


@patch(measure_specific_parameters_template._interpolate_annual_data)
@patch(measure_specific_parameters_template._fill_unit)
@patch(measure_specific_parameters_template._fill_annual_savings)
@patch(measure_specific_parameters_template._fill_investment_cost)
@patch(measure_specific_parameters_template._fill_subsidy_rate)
@patch(measure_specific_parameters_template._fill_lifetime)
def test_fill_main_sheet():
    final_energy_saving_by_action_type = Mock()

    with patch(measure_specific_parameters_template._fill_share_affected) as mocked_fill:
        measure_specific_parameters_template._fill_main_sheet(
            'mocked_sheet',
            'mocked_context',
            final_energy_saving_by_action_type,
            'mocked_wuppertal_parameters',
            'mocked_data_source',
        )
        mocked_fill.assert_called_once()


def test_fill_fuel_switch_sheet():
    with patch(measure_specific_parameters_template._interpolate_annual_data) as mocked_interpolate:
        measure_specific_parameters_template._fill_fuel_switch_sheet(
            'mocked_sheet',
            'mocked_years',
        )
        mocked_interpolate.assert_called_once()


@patch(measure_specific_parameters_template._interpolate_annual_data)
@patch(measure_specific_parameters_template._fill_number_of_affected_dwellings)
@patch(measure_specific_parameters_template._fill_energy_poverty_targeteness)
@patch(measure_specific_parameters_template._fill_dwelling_stock)
@patch(measure_specific_parameters_template._fill_average_hh_per_building)
@patch(measure_specific_parameters_template._fill_average_rent)
def test_fill_residential_sheet():
    final_energy_saving_by_action_type = Mock()

    with patch(measure_specific_parameters_template._fill_rent_premium) as mocked_fill_rent_premium:
        measure_specific_parameters_template._fill_residential_sheet(
            'mocked_sheet',
            'mocked_context',
            final_energy_saving_by_action_type,
            'mocked_wuppertal_parameters',
            'mocked_data_source',
        )

        mocked_fill_rent_premium.assert_called_once()


def test_fill_context_sheet():
    sheet = Mock()
    context = Mock()
    measure_specific_parameters_template._fill_context_sheet(sheet, context)
    sheet.cell.assert_called()


def test_annual_columns():
    mocked_cell = Mock()
    mocked_cell.value = 'foo'

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
    cell._style = 'mocked_style'
    result = measure_specific_parameters_template._cell_style(cell)
    assert result == 'mocked_style'


class TestCellValue:
    def test_with_na(self):
        cell = Mock()
        cell.value = '=NA()'
        result = measure_specific_parameters_template._cell_value(cell)
        assert math.isnan(result)

    def test_normal_usage(self):
        cell = Mock()
        cell.value = 33
        result = measure_specific_parameters_template._cell_value(cell)
        assert result == 33


@patch(
    measure_specific_parameters_template._cell_value,
    'mocked_cell_value',
)
def test_columns_to_table():
    mocked_column = ['header', 'cell']
    columns = [
        mocked_column,
        mocked_column,
    ]
    result = measure_specific_parameters_template._columns_to_table(columns)
    assert result['mocked_cell_value'][0] == 'mocked_cell_value'


@patch(measure_specific_parameters_template._cell_value, 'mocked_cell_value')
def test_extrapolated_nan_table():
    raw_annual_table = Table([{'id_foo': 1, '2010': 1, '2030': 3}])
    years = [2010, 2020, 2030]
    result = measure_specific_parameters_template._extrapolated_nan_table(raw_annual_table, years)
    assert len(result) == 1
    assert np.isnan(result['2010'][0])
    assert np.isnan(result['2020'][0])
    assert np.isnan(result['2030'][0])


def test_fill_annual_data():
    sheet = Mock()
    annual_table = Table([{'id_foo': 1, '2000': 10}])
    cell_styles = Mock()
    measure_specific_parameters_template._fill_annual_data(sheet, annual_table, cell_styles)
    sheet.cell.assert_called()


def test_fill_annual_savings():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_annual_savings(
            'mocked_sheet',
            'mocked_final_energy_saving_by_action_type',
        )
        patched_fill.assert_called_once()


class TestFillAnnualSeries:
    def test_with_table(self):
        sheet = Mock()
        start_column_index = 2
        row_index = 3
        series_or_table = Table([{'id_foo': 1, '2000': 10}])
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
        series_or_table = AnnualSeries({'2000': 10})
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
            {'id_foo': 1, 'id_baa': 1, '2000': 1, '2020': 2},
            {'id_foo': 1, 'id_baa': 2, '2000': 10, '2020': 20},
        ]
    )
    measure_specific_parameters_template._fill_table(sheet, start_column_index, start_row_index, table)
    sheet.cell.assert_called()


@patch(dwelling.dwelling_stock)
@patch(measure_specific_parameters_template._fill_annual_series)
def test_fill_dwelling_stock():
    context = Mock()

    measure_specific_parameters_template._fill_dwelling_stock(
        'mocked_sheet',
        context,
        'mocked_final_energy_saving_by_action_type',
        'mocked_data_source',
    )


def test_fill_average_hh_per_building():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_average_hh_per_building(
            'mocked_sheet',
            Mock(),
        )
        patched_fill.assert_called_once()


def test_fill_average_rent():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_average_rent(
            'mocked_sheet',
            Mock(),
        )
        patched_fill.assert_called_once()


def test_fill_rent_premium():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_rent_premium(
            'mocked_sheet',
            Mock(),
        )
        patched_fill.assert_called_once()


def test_fill_energy_poverty_targeteness():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_energy_poverty_targeteness(
            'mocked_sheet',
            Mock(),
        )
        patched_fill.assert_called_once()


@patch(investment.investment_cost_in_euro)
def test_fill_investment_cost():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_investment_cost(
            'mocked_sheet',
            'mocked_final_energy_saving_by_action_type',
            'mocked_data_source',
        )
        patched_fill.assert_called_once()


@patch(measure_specific_parameters_template._lifetime)
def test_fill_lifetime():
    sheet = Mock()
    measure_specific_parameters_template._fill_lifetime(
        sheet,
        'mocked_context',
        'mocked_database',
    )
    sheet.cell.assert_called_once()


def test_lifetime():
    context = Mock()

    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_result')

    database = Mock()
    database.table = Mock(mocked_table)
    result = measure_specific_parameters_template._lifetime(
        context,
        database,
    )
    assert result == 'mocked_result'


@patch(fuel_split.fuel_split_by_action_type)
def test_fill_share_affected():
    with patch(measure_specific_parameters_template._fill_table) as patched_fill:
        measure_specific_parameters_template._fill_share_affected(
            'mocked_sheet', Mock(), 'mocked_final_energy_saving_by_action_type', 'mocked_data_source'
        )
        patched_fill.assert_called_once()


def test_fill_subsidy_rate():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_subsidy_rate(
            'mocked_sheet',
            Mock(),
        )
        patched_fill.assert_called_once()


@patch(dwelling.number_of_affected_dwellings)
def test_fill_number_of_affected_dwellings():
    with patch(measure_specific_parameters_template._fill_annual_series) as patched_fill:
        measure_specific_parameters_template._fill_number_of_affected_dwellings(
            'mocked_sheet',
            Mock(),
            'mocked_final_energy_saving_by_action_type',
            'mocked_data_source',
        )
        patched_fill.assert_called_once()


def test_fill_unit():
    sheet = {}
    context = {'unit': {'symbol': 'mocked_unit_symbol'}}
    result = measure_specific_parameters_template._fill_unit(sheet, context)
    assert result['D2'] == 'mocked_unit_symbol'


class TestInterpolateAnnualData:
    @patch(extrapolation.extrapolate)
    @patch(measure_specific_parameters_template._fill_annual_data, 'mocked_result')
    def test_with_non_nan(self):
        mocked_raw_annual_table = Mock()
        mocked_raw_annual_table.contains_non_nan = Mock(True)
        mocked_parts = ('mocked_sheet_without_annual_data', mocked_raw_annual_table, 'mocked_cell_style')

        with patch(measure_specific_parameters_template._split_sheet, mocked_parts):
            result = measure_specific_parameters_template._interpolate_annual_data(
                'mocked_sheet',
                Mock(),
            )
            assert result == 'mocked_result'

    @patch(measure_specific_parameters_template._extrapolated_nan_table)
    @patch(measure_specific_parameters_template._fill_annual_data, 'mocked_result')
    def test_without_non_nan(self):
        mocked_raw_annual_table = Mock()
        mocked_raw_annual_table.contains_non_nan = Mock(False)
        mocked_parts = ('mocked_sheet_without_annual_data', mocked_raw_annual_table, 'mocked_cell_style')

        with patch(measure_specific_parameters_template._split_sheet, mocked_parts):
            result = measure_specific_parameters_template._interpolate_annual_data(
                'mocked_sheet',
                Mock(),
            )
            assert result == 'mocked_result'


def test_final_energy_saving_by_action_type():
    measure = {
        'id': 1,
        '2000': 0,
        '2010': 10,
    }
    context = {
        'id_subsector': 2,
        'id_action_type': 3,
    }
    result = measure_specific_parameters_template._final_energy_saving_by_action_type(
        measure,
        context,
    )

    assert result['2000'][1, 2, 3] == 0
    assert result['2010'][1, 2, 3] == 10


@patch(measure_specific_parameters_template._annual_columns)
@patch(measure_specific_parameters_template._columns_to_table)
def test_split_sheet():
    sheet = Mock()
    result = measure_specific_parameters_template._split_sheet(sheet)
    assert len(result) == 3


@patch(
    api.parse_request,
    {'id_mode': '1', 'id_region': '2', 'json': {}},
)
def test_template_args():
    result = measure_specific_parameters_template._template_args('mocked_request')
    assert result['id_mode'] == '1'
    assert result['id_region'] == '2'
