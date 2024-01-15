# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
import pandas as pd
import xlsxwriter
from test_utils.mock import Mock, patch, patch_by_string

from template import mocks, xlsx_utils


def test_protect_sheet():
    mocked_sheet = mocks.mocked_sheet()
    xlsx_utils.protect_sheet(mocked_sheet, 'micat', True)
    assert mocked_sheet.protect.called is True
    assert mocked_sheet.hide.called is True


def test_set_column_width():
    mocked_sheet = Mock()
    mocked_sheet.set_column = Mock()

    xlsx_utils.set_column_width(mocked_sheet, 'mocked_width')

    assert mocked_sheet.set_column.called


def test_empty_workbook():
    with patch(xlsxwriter.workbook.Workbook) as mocked_workbook:
        result = xlsx_utils.empty_workbook('mocked_output')
        assert result is not None
        mocked_workbook.assert_called_once()


def test_get_column_widths():
    mocked_dataframe = pd.DataFrame([['a', 'b']], columns=['Column A', 'Column B'])
    column_widths = xlsx_utils.get_column_widths(mocked_dataframe)
    assert column_widths == [4, 8, 8]


@patch(
    xlsx_utils.get_column_widths,
    [4, 8, 8],
)
def test_autofit_column_width():
    mocked_dataframe = Mock()
    mocked_worksheet = Mock()
    mocked_worksheet.set_column = Mock()
    xlsx_utils.autofit_column_width(mocked_worksheet, mocked_dataframe)
    assert mocked_worksheet.set_column.call_count == 3


mocked_array = Mock()
mocked_array.tolist = Mock(return_value=[[np.nan, np.nan, np.nan]])


@patch(np.full, Mock(mocked_array))
def test_create_nan_list():
    nan_list = xlsx_utils.create_nan_list(3)
    assert len(nan_list) == 3


@patch_by_string('pandas.read_excel', 'mocked_result')
def test_read_sheets():
    result = xlsx_utils.read_sheets('mocked/path/to/excelfile')
    assert result == 'mocked_result'


def test_columns_as_list():
    mocked_data_frame = Mock()
    mocked_data_frame.columns = ['a', 'b', 'c']
    result = xlsx_utils.columns_as_list(mocked_data_frame)
    assert result == ['a', 'b', 'c']


class TestAppendNewColumns:
    mocked_data_frame = Mock()
    mocked_data_frame.columns = Mock()
    mocked_data_frame.columns.values = Mock(return_value=['a', 'b', 'c'])
    mocked_data_frame.reindex = Mock(return_value='mocked_expanded_dataframe')
    mocked_new_columns = ['c', 'd', 'e']

    def test_append_new_columns_with_duplicates(self):
        result = xlsx_utils.append_new_columns(self.mocked_data_frame, self.mocked_new_columns, False)
        assert result == 'mocked_expanded_dataframe'

    def test_append_new_columns_without_duplicates(self):
        result = xlsx_utils.append_new_columns(self.mocked_data_frame, self.mocked_new_columns)
        assert result == 'mocked_expanded_dataframe'


def test_shape_to_a1_style_string():
    with patch(xlsxwriter.utility.xl_rowcol_to_cell) as patched_xl_rowcol_to_cell:
        patched_xl_rowcol_to_cell.side_effect = ['A1', 'C3']
        result = xlsx_utils.shape_to_a1_style_string((2, 2))
        assert patched_xl_rowcol_to_cell.called
        assert result == 'A1:C3'


@patch(xlsxwriter.utility.xl_rowcol_to_cell, Mock(side_effect=['A1', 'B2']))
def test_slice_to_cell_string():
    result = xlsx_utils.slice_to_cell_string(0, 0, 1, 1)
    assert result == 'A1:B2'
