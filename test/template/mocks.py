# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from test_utils.mock import Mock


def mocked_sheet():
    sheet = Mock()
    sheet.set_row = Mock()
    sheet.write_row = Mock()
    sheet.data_validation = Mock()
    sheet.set_column = Mock()
    sheet.hide = Mock()
    sheet.protect = Mock()
    sheet.write_column = Mock()
    return sheet


def mocked_workbook():
    workbook = Mock()
    workbook.add_format = Mock()
    workbook.add_worksheet = Mock(mocked_sheet())
    workbook.close = Mock()
    return workbook


def mocked_database():
    database = Mock()
    database.table = Mock()
    database.mapping_table = Mock()
    return database


def mocked_template_args():
    template_args = {
        'coefficient_sheets': ['mocked_sheet1', 'mocked_sheet2', 'mocked_sheet3', 'mocked_sheet4'],
        'id_mode': 1,
        'id_region': 1,
        'sheet_password': 'micat',
        'options_sheet_name': 'Options',
    }
    return template_args
