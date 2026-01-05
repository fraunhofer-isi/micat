# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=unused-variable

import io

from micat.template import constants, xlsx_utils


def savings_template(request, database):
    template_args = _template_args(request)
    template_bytes = _savings_template(template_args, database)
    return template_bytes


def _template_args(request):
    savings = request.json
    args = {
        'savings': savings,
        'sheet_password': 'micat',
        'add_conditional_formatting': True,
        'savings_sheet_name': 'Savings',
        'lock_savings_sheet': True,
        'mappings_sheet_name': 'Mappings',
        'populate_with_savings': True,
    }
    return args


def _savings_template(template_args, database):
    output = io.BytesIO()
    workbook = xlsx_utils.empty_workbook(output)
    savings_sheet = _savings_sheet(template_args, workbook)
    workbook = _add_mappings_sheet(workbook, template_args, database)
    _populate_savings(savings_sheet, template_args)
    workbook.close()
    return output


def _populate_savings(savings_sheet, template_args):
    if not template_args['savings']:
        return
    if template_args['populate_with_savings']:
        for row_num, row_data in enumerate(template_args['savings']):
            for col_num, col_data in enumerate(row_data):
                savings_sheet.write(row_num, col_num, col_data)


def _add_mappings_sheet(workbook, template_args, database):
    mappings_sheet = workbook.add_worksheet(template_args['mappings_sheet_name'])

    id_subsector_table = database.id_table('id_subsector')
    id_action_type_table = database.id_table('id_action_type')
    mapping__subsector__action_type = database.mapping_table('mapping__subsector__action_type')

    mappings_sheet = _fill_mapping_sheet(
        mappings_sheet,
        id_subsector_table,
        id_action_type_table,
        mapping__subsector__action_type,
    )

    xlsx_utils.set_column_width(mappings_sheet, 30)

    password = template_args['sheet_password']
    xlsx_utils.protect_sheet(mappings_sheet, password, True)
    return workbook


def _fill_mapping_sheet(
    mappings_sheet,
    id_subsector_table,
    id_action_type_table,
    mapping__subsector__action_type,
):
    column_index = 0
    for id_subsector, subsector in id_subsector_table.iterrows():
        subsector_label = subsector['label']
        action_type_labels = _action_type_labels(
            id_subsector,
            mapping__subsector__action_type,
            id_action_type_table,
        )

        data = [subsector_label] + action_type_labels
        mappings_sheet.write_column(row=0, col=column_index, data=data)
        column_index += 1

    return mappings_sheet


def _action_type_labels(
    id_subsector,
    mapping__subsector__action_type,
    id_action_type_table,
):
    action_type_ids = mapping__subsector__action_type.target_ids(id_subsector)
    labels = id_action_type_table.labels(action_type_ids)
    return labels


def _header_format():
    return {
        'bg_color': '#C0C0C0',
        'bold': True,
        'locked': False,
    }


def _subsector_header_validator():
    return {
        'validate': 'custom',
        'value': '=EXACT(A1, "Subsector")',
    }


def _improvement_header_validator():
    return {
        'validate': 'custom',
        'value': '=EXACT(B1, "Improvement")',
    }


# pylint: disable=duplicate-code
def _year_header_validator():
    return {
        'validate': 'integer',
        'criteria': 'between',
        'minimum': 2000,
        'maximum': 2050,
        'input_title': 'Enter an year',
        'input_message': 'between 2000 and 2050',
    }


def _savings_cell_validator():
    return {
        'validate': 'decimal',
        'criteria': 'between',
        'minimum': 0,
        'maximum': 10**9,
        'input_title': 'Enter an saving',
        'input_message': 'between 0 and 10^9',
    }


def _subsector_list_dropdown_validator(mapping_sheet_name):
    subsector_validation_formula = _subsector_validation_formula(mapping_sheet_name)
    return {
        'validate': 'list',
        'source': subsector_validation_formula,
    }


def _subsector_validation_formula(mapping_sheet_name):
    return f'={mapping_sheet_name}!$1:$1'


def _improvement_validation_formula_part(mapping_sheet_name):
    return f'''
    OFFSET(
      {mapping_sheet_name}!$A$1,
      1,
      MATCH(
        A2,
        {mapping_sheet_name}!$1:$1,
        0
      )-1,
      COUNTA(
        OFFSET(
          {mapping_sheet_name}!$A$1,
          1,
          MATCH(
            A2,
            {mapping_sheet_name}!$1:$1,
            0
          )-1,
          {constants.MAX_ROWS}
        )
      )
    )'''


def _improvement_validation_formula(mapping_sheet_name):
    return f'={_improvement_validation_formula_part(mapping_sheet_name)}'


def _improvement_list_dropdown_validator(mapping_sheet_name):
    improvement_validation_formula = _improvement_validation_formula(mapping_sheet_name)
    return {
        'validate': 'list',
        'source': improvement_validation_formula,
    }


def _improvement_format_formula(mapping_sheet_name):
    return f'=COUNTIF({_improvement_validation_formula_part(mapping_sheet_name)},B2)=0'


def _conditional_improvement_format(mapping_sheet_name, invalid_format):
    improvement_format_formula = _improvement_format_formula(mapping_sheet_name)
    return {
        'type': 'formula',
        'criteria': improvement_format_formula,
        'format': invalid_format,
    }


def _add_savings_data_validation(savings_sheet, mapping_sheet_name):
    savings_sheet.data_validation(
        first_row=0,
        first_col=0,
        last_row=0,
        last_col=0,
        options=_subsector_header_validator(),
    )
    savings_sheet.data_validation(
        first_row=0,
        first_col=1,
        last_row=0,
        last_col=1,
        options=_improvement_header_validator(),
    )
    savings_sheet.data_validation(
        first_row=0,
        first_col=2,
        last_row=0,
        last_col=constants.MAX_COLS,
        options=_year_header_validator(),
    )
    savings_sheet.data_validation(
        first_row=1,
        first_col=2,
        last_row=constants.MAX_ROWS,
        last_col=constants.MAX_COLS,
        options=_savings_cell_validator(),
    )
    savings_sheet.data_validation(
        first_row=1,
        first_col=0,
        last_row=constants.MAX_ROWS,
        last_col=0,
        options=_subsector_list_dropdown_validator(mapping_sheet_name),
    )
    savings_sheet.data_validation(
        first_row=1,
        first_col=1,
        last_row=constants.MAX_ROWS,
        last_col=1,
        options=_improvement_list_dropdown_validator(mapping_sheet_name),
    )


def _add_savings_header(savings_sheet, workbook):
    header_format = workbook.add_format(_header_format())
    savings_sheet.set_row(row=0, height=None, cell_format=header_format)
    header = ['Subsector', 'Improvement']
    savings_sheet.write_row(row=0, col=0, data=header)


def _add_conditional_improvements_formatting(workbook, savings_sheet, mapping_sheet_name):
    invalid_format = workbook.add_format({'bold': True, 'font_color': '#9C0006', 'bg_color': '#FFC7CE'})
    savings_sheet.conditional_format(
        first_row=1,
        first_col=1,
        last_row=constants.MAX_ROWS,
        last_col=1,
        options=_conditional_improvement_format(mapping_sheet_name, invalid_format),
    )


def _lock_savings_sheet(workbook, savings_sheet, password):
    unlocked_format = workbook.add_format({'locked': False})
    savings_sheet.set_column(
        first_col=0,
        last_col=constants.MAX_COLS,
        width=30,
        cell_format=unlocked_format,
    )
    xlsx_utils.protect_sheet(savings_sheet, password, False)


def _savings_sheet(template_args, workbook):
    savings_sheet = workbook.add_worksheet(template_args['savings_sheet_name'])
    _add_savings_header(savings_sheet, workbook)
    _add_savings_data_validation(savings_sheet, template_args['mappings_sheet_name'])
    if template_args['add_conditional_formatting']:
        _add_conditional_improvements_formatting(workbook, savings_sheet, template_args['mappings_sheet_name'])
    if template_args['lock_savings_sheet']:
        _lock_savings_sheet(workbook, savings_sheet, template_args['sheet_password'])
    else:
        savings_sheet.set_column(first_col=0, last_col=constants.MAX_COLS, width=30)
    return savings_sheet
