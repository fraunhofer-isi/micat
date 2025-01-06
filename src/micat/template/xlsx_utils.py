# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
import pandas as pd
import xlsxwriter

from micat.template import constants


def protect_sheet(sheet, password, hide=False):
    sheet.protect(password=password)
    if hide:
        sheet.hide()


def set_column_width(sheet, width):
    sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=width)


def empty_workbook(output):
    return xlsxwriter.workbook.Workbook(output)


def get_column_widths(dataframe):
    idx_max = max([len(str(index)) for index in dataframe.index.values] + [len(str(dataframe.index.name))])
    column_widths = [idx_max] + [
        max([len(str(column)) for column in dataframe[column].values] + [len(str(column))])
        for column in dataframe.columns
    ]
    return column_widths


def autofit_column_width(worksheet, dataframe):
    column_widths = get_column_widths(dataframe)
    for index, width in enumerate(column_widths):
        worksheet.set_column(index, index, width)


def create_nan_list(length):
    return np.full((1, length), np.nan).tolist()[0]


def read_sheets(path_to_excel_file, decimal=','):
    sheet_to_df_map = pd.read_excel(path_to_excel_file, sheet_name=None, decimal=decimal)
    return sheet_to_df_map


def columns_as_list(data_frame):
    return list(data_frame.columns)


def append_new_columns(data_frame, new_columns, without_duplicates=True):
    columns = [str(column_name) for column_name in data_frame.columns.values] + new_columns
    if without_duplicates:
        columns = list(dict.fromkeys(columns))
    expanded_data_frame = data_frame.reindex(columns=columns)
    return expanded_data_frame


def shape_to_a1_style_string(shape):
    start_cell = xlsxwriter.utility.xl_rowcol_to_cell(0, 0)
    end_cell = xlsxwriter.utility.xl_rowcol_to_cell(shape[0], shape[1])
    a1_style_string = f'{start_cell}:{end_cell}'
    return a1_style_string


def slice_to_cell_string(first_row, first_col, last_row, last_col):
    cell_start = xlsxwriter.utility.xl_rowcol_to_cell(first_row, first_col)
    cell_end = xlsxwriter.utility.xl_rowcol_to_cell(last_row, last_col)
    cell_string = f'{cell_start}:{cell_end}'
    return cell_string
