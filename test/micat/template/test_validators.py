# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.template import mocks, validators, xlsx_utils

# pylint: disable=protected-access
from micat.test_utils.isi_mock import patch, raises

mocked_template_args = mocks.mocked_template_args()


class TestMinYear:
    def test_min_year_success(self):
        for id_mode in range(1, 5):
            result = validators.min_year(id_mode)
            if id_mode in (1, 2):
                assert result == 2015
            else:
                assert result == 2000

    def test_min_year_failure(self):
        with raises(BaseException) as exception_info:
            validators.min_year(0)
        assert isinstance(exception_info.value, ValueError)


class TestMaxYear:
    def test_max_year_success(self):
        for id_mode in range(1, 5):
            result = validators.max_year(id_mode)
            if id_mode in (1, 2):
                assert result == 2050
            else:
                assert result == 2020

    def test_min_year_failure(self):
        with raises(BaseException) as exception_info:
            validators.max_year(0)
        assert isinstance(exception_info.value, ValueError)


@patch(xlsx_utils.slice_to_cell_string, 'A1:A1')
def test_exact_string_validator():
    result = validators.exact_string_validator('mocked_string_name', 0, 0, 0, 0)
    assert result['validate'] == 'custom'
    assert '"mocked_string_name"' in result['value']
    assert 'A1:A1' in result['value']


@patch(validators.min_year, 2015)
@patch(validators.max_year, 2050)
def test_year_header_validator():
    result = validators.year_header_validator(mocked_template_args['id_mode'])
    assert len(result) == 6
    assert result['minimum'] == 2015
    assert result['maximum'] == 2050


def test_parameter_cell_validator():
    assert len(validators.parameter_cell_validator()) == 6


@patch(
    validators._subsector_validation_formula,
    'mocked_formula',
)
def test_subsector_list_dropdown_validator():
    result = validators.subsector_list_dropdown_validator(
        mocked_template_args['options_sheet_name'],
        'mocked_subsectors',
    )
    assert len(result) == 2
    assert result['source'] == 'mocked_formula'


def test_subsector_validation_formula():
    result = validators._subsector_validation_formula(
        mocked_template_args['options_sheet_name'],
        'mocked_subsectors',
    )
    assert result[0] == '='
    assert mocked_template_args['options_sheet_name'] in result


@patch(
    validators._final_energy_carrier_validation_formula,
    'mocked_formula',
)
def test_final_energy_carrier_list_dropdown_validator():
    result = validators.final_energy_carrier_list_dropdown_validator(
        mocked_template_args['options_sheet_name'],
        'mocked_final_energy_carriers',
    )
    assert len(result) == 2
    assert 'mocked_formula' in result['source']


def test_final_energy_carrier_validation_formula():
    mocked_final_energy_carriers = ['mocked_final_energy_carrier1', 'mocked_final_energy_carrier2']
    result = validators._final_energy_carrier_validation_formula(
        mocked_template_args['options_sheet_name'],
        mocked_final_energy_carriers,
    )
    assert result[0] == '='
    assert mocked_template_args['options_sheet_name'] in result
    assert str(len(mocked_final_energy_carriers)) in result


@patch(
    validators._primary_energy_carrier_validation_formula,
    'mocked_formula',
)
def test_primary_energy_carrier_list_dropdown_validator():
    result = validators.primary_energy_carrier_list_dropdown_validator(
        mocked_template_args['options_sheet_name'],
        'mocked_subsectors',
    )
    assert len(result) == 2
    assert result['source'] == 'mocked_formula'


def test_primary_energy_carrier_list_dropdown_formula():
    result = validators._primary_energy_carrier_validation_formula(
        mocked_template_args['options_sheet_name'],
        'mocked_subsectors',
    )
    assert result[0] == '='
    assert mocked_template_args['options_sheet_name'] in result
