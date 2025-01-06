# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
# pylint: disable=unused-variable
import copy
import io

from micat.template import mocks, savings_template, xlsx_utils
from micat.test_utils.isi_mock import Mock, patch
from micat.utils import api

mocked_template_args = {
    'savings': [
        ['Subsector', 'Improvement', 2015, 2020, 2025],
        ['mocked_subsector1', 'mocked_improvement1', 0, 102.0, 232.2],
        ['mocked_subsector2', 'mocked_improvement2', 0, 430, 774],
        ['mocked_subsector1', 'mocked_improvement2', 0, 516, 1204],
    ],
    'sheet_password': 'micat',
    'add_conditional_formatting': True,
    'savings_sheet_name': 'Savings',
    'lock_savings_sheet': True,
    'mappings_sheet_name': 'Mappings',
    'populate_with_savings': True,
}


@patch(
    savings_template._template_args,
    mocked_template_args,
)
@patch(
    savings_template._savings_template,
    'mocked_result',
)
def test_savings_template():
    result = savings_template.savings_template(
        'mocked_request',
        'mocked_database',
    )
    assert result == 'mocked_result'


@patch(api.parse_request, {'savings': '{}'})
def test_template_args():
    mocked_request = Mock()
    mocked_request.json = Mock
    result = savings_template._template_args(mocked_request)
    assert len(result) == 7


@patch(io.BytesIO, 'mocked_io')
@patch(
    xlsx_utils.empty_workbook,
    mocks.mocked_workbook(),
)
@patch(
    savings_template._savings_sheet,
    mocks.mocked_sheet(),
)
@patch(
    savings_template._add_mappings_sheet,
    mocks.mocked_sheet(),
)
@patch(savings_template._populate_savings)
def test__savings_template():
    result = savings_template._savings_template(
        mocked_template_args,
        'mocked_database',
    )
    assert result == 'mocked_io'


class TestPopulateSavings:
    def test_populate_savings(self):
        mocked_savings_sheet = mocks.mocked_sheet()
        savings_template._populate_savings(mocked_savings_sheet, mocked_template_args)
        call_count = len(mocked_template_args['savings'][0]) * len(mocked_template_args['savings'])
        assert mocked_savings_sheet.write.call_count == call_count

    def test_populate_savings_with_empty_savings(self):
        mocked_empty_template_args = {'savings': {}}
        mocked_savings_sheet = mocks.mocked_sheet()
        savings_template._populate_savings(mocked_savings_sheet, mocked_empty_template_args)
        assert mocked_savings_sheet.write.call_count == 0


@patch(savings_template._fill_mapping_sheet)
def test_add_mappings_sheet():
    mocked_workbook = mocks.mocked_workbook()

    mocked_database = Mock()
    mocked_database.id_table = Mock()
    mocked_database.mapping_table = Mock()

    with patch(xlsx_utils.set_column_width) as mocked_set_column_width:
        with patch(xlsx_utils.protect_sheet) as mocked_protect_sheet:
            savings_template._add_mappings_sheet(
                mocked_workbook,
                mocked_template_args,
                mocked_database,
            )
            assert mocked_workbook.add_worksheet.called
            assert mocked_set_column_width.called
            assert mocked_protect_sheet.called


@patch(
    savings_template._action_type_labels,
    ['mocked_action_type_label'],
)
def test_fill_mapping_sheet():
    mocked_sheet = Mock()
    mocked_sheet.write_column = Mock()

    mocked_id_subsector_table = Mock()
    mocked_subsector_series = {'label': 'mocked_subsector_label'}
    mocked_id_subsector_table.iterrows = Mock(return_value=[(1, mocked_subsector_series)])

    savings_template._fill_mapping_sheet(
        mocked_sheet,
        mocked_id_subsector_table,
        'mocked_id_action_type_table',
        'mocked_mapping_table',
    )

    assert mocked_sheet.write_column.called


def test_action_type_labels():
    mocked_mapping = Mock()
    mocked_mapping.target_ids = Mock()

    mocked_id_action_type_table = Mock()
    mocked_id_action_type_table.labels = Mock(return_value='mocked_result')

    result = savings_template._action_type_labels(
        'mocked_id_subsector',
        mocked_mapping,
        mocked_id_action_type_table,
    )
    assert result == 'mocked_result'


def test_header_format():
    assert len(savings_template._header_format()) == 3


def test_subsector_header_validator():
    assert len(savings_template._subsector_header_validator()) == 2


def test_improvement_header_validator():
    assert len(savings_template._improvement_header_validator()) == 2


def test_year_header_validator():
    assert len(savings_template._year_header_validator()) == 6


def test_savings_cell_validator():
    assert len(savings_template._savings_cell_validator()) == 6


@patch(
    savings_template._subsector_validation_formula,
    'mocked_formula',
)
def test_subsector_list_dropdown_validator():
    result = savings_template._subsector_list_dropdown_validator(mocked_template_args['mappings_sheet_name'])
    assert len(result) == 2
    assert result['source'] == 'mocked_formula'


def test_subsector_validation_formula():
    result = savings_template._subsector_validation_formula(mocked_template_args['mappings_sheet_name'])
    assert result[0] == '='
    assert mocked_template_args['mappings_sheet_name'] in result


def test_improvement_validation_formula_part():
    result = savings_template._improvement_validation_formula_part(mocked_template_args['mappings_sheet_name'])
    assert result[0] != '='
    assert mocked_template_args['mappings_sheet_name'] in result
    assert 'OFFSET' in result
    assert 'MATCH' in result
    assert 'COUNTA' in result


@patch(
    savings_template._improvement_validation_formula_part,
    'mocked_part',
)
def test_improvement_validation_formula():
    result = savings_template._improvement_validation_formula(mocked_template_args['mappings_sheet_name'])
    assert result == '=mocked_part'


@patch(
    savings_template._improvement_validation_formula,
    'mocked_formula',
)
def test_improvement_list_dropdown_validator():
    result = savings_template._improvement_list_dropdown_validator(mocked_template_args['mappings_sheet_name'])
    assert len(result) == 2
    assert 'mocked_formula' in result['source']


def test_improvement_format_formula():
    result = savings_template._improvement_format_formula(mocked_template_args['mappings_sheet_name'])
    assert result[0] == '='
    assert 'COUNTIF' in result
    assert mocked_template_args['mappings_sheet_name'] in result


@patch(
    savings_template._improvement_format_formula,
    'mocked_formula',
)
def test_conditional_improvement_format():
    result = savings_template._conditional_improvement_format(mocked_template_args['mappings_sheet_name'], {})
    assert len(result) == 3
    assert result['criteria'] == 'mocked_formula'
    assert result['format'] == {}


@patch(savings_template._subsector_header_validator)
@patch(savings_template._improvement_header_validator)
@patch(savings_template._year_header_validator)
@patch(savings_template._savings_cell_validator)
@patch(savings_template._subsector_list_dropdown_validator)
@patch(savings_template._improvement_list_dropdown_validator)
def test_add_savings_data_validation(*args):
    mocked_sheet = mocks.mocked_sheet()
    savings_template._add_savings_data_validation(mocked_sheet, mocked_template_args['mappings_sheet_name'])
    for mock in args:
        assert mock.called
    assert mocked_sheet.data_validation.call_count == 6


def test_add_savings_header():
    mocked_workbook = mocks.mocked_workbook()
    mocked_savings_sheet = mocks.mocked_sheet()
    savings_template._add_savings_header(mocked_savings_sheet, mocked_workbook)
    assert mocked_workbook.add_format.called
    assert mocked_savings_sheet.set_row.called
    assert mocked_savings_sheet.write_row.called


def test_add_conditional_improvements_formatting():
    mocked_workbook = mocks.mocked_workbook()
    mocked_savings_sheet = mocks.mocked_sheet()

    with patch(savings_template._conditional_improvement_format) as conditional_improvement_format_mock:
        savings_template._add_conditional_improvements_formatting(
            mocked_workbook,
            mocked_savings_sheet,
            mocked_template_args['mappings_sheet_name'],
        )
        assert mocked_workbook.add_format.called
        assert mocked_savings_sheet.conditional_format.called
        assert conditional_improvement_format_mock.called


def test_lock_savings_sheet():
    mocked_workbook = mocks.mocked_workbook()
    mocked_savings_sheet = mocks.mocked_sheet()

    with patch(xlsx_utils.protect_sheet) as protect_sheet_mock:
        savings_template._lock_savings_sheet(
            mocked_workbook,
            mocked_savings_sheet,
            'mocked_password',
        )
        assert mocked_workbook.add_format.called
        assert mocked_savings_sheet.set_column.called
        assert protect_sheet_mock.called


class TestSavingsSheet:
    def test_savings_sheet_without_conditional_formatting_and_lock(self):
        mocked_template_args_new = copy.deepcopy(mocked_template_args)
        mocked_template_args_new['add_conditional_formatting'] = False
        mocked_template_args_new['lock_savings_sheet'] = False
        mocked_workbook = mocks.mocked_workbook()

        with patch(savings_template._add_savings_header) as add_savings_header_mock:
            with patch(savings_template._add_savings_data_validation) as add_savings_data_validation_mock:
                with patch(
                    savings_template._add_conditional_improvements_formatting
                ) as add_conditional_improvements_formatting_mock:
                    with patch(savings_template._lock_savings_sheet) as lock_savings_sheet_mock:
                        result = savings_template._savings_sheet(mocked_template_args_new, mocked_workbook)
                        assert result.set_column.called
                        assert add_savings_header_mock.called
                        assert add_savings_data_validation_mock.called
                        assert not add_conditional_improvements_formatting_mock.called
                        assert not lock_savings_sheet_mock.called

    @patch(savings_template._add_savings_header)
    @patch(savings_template._add_savings_data_validation)
    @patch(savings_template._add_conditional_improvements_formatting)
    @patch(savings_template._lock_savings_sheet)
    def test_savings_sheet_with_conditional_formatting_and_lock(self, *args):
        mocked_workbook = mocks.mocked_workbook()
        result = savings_template._savings_sheet(mocked_template_args, mocked_workbook)
        assert not result.set_column.called
        for arg in args:
            assert arg.called
