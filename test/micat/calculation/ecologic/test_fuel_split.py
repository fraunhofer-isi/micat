# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

import pandas as pd

from micat.calculation import extrapolation
from micat.calculation.ecologic import fuel_split
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table
from micat.table.value_table import ValueTable
from micat.test_utils.isi_mock import Mock, patch, raises

mocked_final_energy_savings_by_action_type = Table(
    [
        {'id_subsector': 1, 'id_action_type': 2, '2020': 2},
    ]
)

mocked_fuel_split_table = Table(
    [
        {'id_final_energy_carrier': 8, 'id_subsector': 1, 'id_action_type': 2, '2020': 4},
    ]
)


@patch(extrapolation.extrapolate)
@patch(fuel_split._raw_lambda)
@patch(fuel_split._basic_chi)
@patch(fuel_split._measure_specific_fuel_split, 'mocked_result')
def test_fuel_split_by_action_type():
    final_energy_saving_by_action_type = Mock()
    data_source = Mock()

    result = fuel_split.fuel_split_by_action_type(
        final_energy_saving_by_action_type,
        data_source,
        'mocked_id_mode',
        'mocked_id_region',
        'mocked_subsector_ids',
    )
    assert result == 'mocked_result'


def test_basic_chi():
    mocked_frame = Mock()
    mocked_frame.reduce = Mock('mocked_result')

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_frame)

    result = fuel_split._basic_chi(
        mocked_data_source,
        'mocked_id_region',
        'mocked_subsector_ids',
        'mocked_action_type_ids',
    )

    assert result == 'mocked_result'


class TestDetermineLambdaForMeasure:
    @patch(
        fuel_split._lambda_for_measure_with_non_effected_action_type,
        'mocked_result',
    )
    def test_non_effected_action_type(self):
        id_action_type = 2
        result = fuel_split._determine_lambda_for_measure(
            'mocked_id_measure',
            'mocked_id_subsector',
            id_action_type,
            'mocked_energy_saving',
            'mocked_extrapolated_final_parameters',
            'mocked_extrapolated_parameters',
            'mocked_constants',
        )
        assert result == 'mocked_result'

    @patch(
        fuel_split._lambda_for_measure_with_effected_action_type,
        'mocked_result',
    )
    def test_effected_action_type(self):
        id_action_type = 1
        result = fuel_split._determine_lambda_for_measure(
            'mocked_id_measure',
            'mocked_id_subsector',
            id_action_type,
            'mocked_energy_saving',
            'mocked_extrapolated_final_parameters',
            'mocked_extrapolated_parameters',
            'mocked_constants',
        )
        assert result == 'mocked_result'


def test_determine_chi_for_measure():
    id_measure = 1
    id_subsector = 2
    id_action_type = 3
    basic_chi = Table(
        [
            {
                'id_subsector': 2,
                'id_action_type': 3,
                'value': 99,
            }
        ]
    )
    result = fuel_split._determine_chi_for_measure(
        id_measure,
        id_subsector,
        id_action_type,
        basic_chi,
    )
    assert result['value'][1, 2, 3] == 1


@patch(
    fuel_split._eta_ante,
    Mock(10),
)
@patch(
    fuel_split._eta_post,
    Mock(12),
)
def test_energy_consumption():
    mocked_energy_saving = AnnualSeries({'2000': 2})

    result = fuel_split._energy_consumption(
        mocked_energy_saving,
        'mocked_extrapolated_final_parameters',
        'mocked_lambda_ante',
        'mocked_lambda_post',
    )
    assert result['2000'] == 2 * 10 / (12 - 10)


@patch(
    fuel_split._eta_ante,
    Mock(10),
)
@patch(
    fuel_split._eta_post,
    Mock(12),
)
def test_energy_consumption_difference():
    mocked_energy_saving = 2
    mocked_energy_consumption = 10
    mocked_lambda_ante = 0.5
    mocked_lambda_post = 0.2

    result = fuel_split._energy_consumption_difference(
        mocked_energy_saving,
        mocked_energy_consumption,
        mocked_lambda_ante,
        mocked_lambda_post,
    )
    assert result == 0.5 * (10 + 2) - 0.2 * 10


def test_eta_ante():
    extrapolated_final_parameters = Table(
        [
            {'id_parameter': 14, 'id_foo': 1, '2000': 1},
            {'id_parameter': 14, 'id_foo': 2, '2000': 1},
        ]
    )
    mocked_lambda_ante = 2

    result = fuel_split._eta_ante(
        extrapolated_final_parameters,
        mocked_lambda_ante,
    )
    assert result['2000'] == 2 * (1 + 1)


def test_eta_post():
    extrapolated_final_parameters = Table(
        [
            {'id_parameter': 15, 'id_foo': 1, '2000': 1},
            {'id_parameter': 15, 'id_foo': 2, '2000': 1},
        ]
    )
    mocked_lambda_post = 3

    result = fuel_split._eta_post(
        extrapolated_final_parameters,
        mocked_lambda_post,
    )
    assert result['2000'] == 3 * (1 + 1)


def test_lambda_for_measure_with_effected_action_type():
    id_subsector = 2
    extrapolated_final_parameters = Table(
        [
            {'id_measure': 1, 'id_parameter': 16, 'id_final_energy_carrier': 1, '2020': 0.1},
            {'id_measure': 1, 'id_parameter': 16, 'id_final_energy_carrier': 2, '2020': 0.1},
        ]
    )

    result = fuel_split._lambda_for_measure_with_effected_action_type(
        id_subsector,
        extrapolated_final_parameters,
    )
    assert result['2020'][1, 2, 1] == 0.1


mocked_difference = Table(
    [
        {'id_measure': 1, 'id_parameter': 2, 'id_final_energy_carrier': 1, '2020': 2},
    ]
)


@patch(
    fuel_split._energy_consumption,
    'mocked_energy_consumption',
)
@patch(
    fuel_split._energy_consumption_difference,
    mocked_difference,
)
def test_lambda_for_measure_with_non_effected_action_type():
    id_subsector = 2
    energy_saving = pd.Series({'2020': 1})
    extrapolated_final_parameters = Table(
        [
            {'id_measure': 1, 'id_parameter': 14, 'id_final_energy_carrier': 1, '2020': 0.1},
            {'id_measure': 1, 'id_parameter': 14, 'id_final_energy_carrier': 2, '2020': 0.9},
            {'id_measure': 1, 'id_parameter': 15, 'id_final_energy_carrier': 1, '2020': 0.2},
            {'id_measure': 1, 'id_parameter': 15, 'id_final_energy_carrier': 2, '2020': 0.8},
            {'id_measure': 1, 'id_parameter': 17, 'id_final_energy_carrier': 1, '2020': 0.3},
            {'id_measure': 1, 'id_parameter': 17, 'id_final_energy_carrier': 2, '2020': 0.7},
            {'id_measure': 1, 'id_parameter': 18, 'id_final_energy_carrier': 1, '2020': 0.4},
            {'id_measure': 1, 'id_parameter': 18, 'id_final_energy_carrier': 2, '2020': 0.6},
        ]
    )

    result = fuel_split._lambda_for_measure_with_non_effected_action_type(
        id_subsector,
        energy_saving,
        extrapolated_final_parameters,
    )
    assert result['2020'][1, 2, 2, 1] == 1


def test_measure_specific_fuel_split():
    lambda_ = Table(
        [
            {
                'id_measure': 1,
                'id_subsector': 2,
                'id_action_type': 3,
                '2020': 2,
            }
        ]
    )
    chi = ValueTable(
        [
            {
                'id_measure': 1,
                'value': 2,
            }
        ]
    )
    result = fuel_split._measure_specific_fuel_split(lambda_, chi)
    assert result['2020'][1, 2, 3] == 1


def test_provide_default_lambda():
    id_measure = 1
    id_subsector = 2
    basic_lambda = Table(
        [
            {
                'id_subsector': 2,
                '2020': 99,
            }
        ]
    )
    result = fuel_split._provide_default_lambda(
        id_measure,
        id_subsector,
        'mocked_id_action_type',
        'mocked_years',
        basic_lambda,
    )
    assert result['2020'][1, 2] == 99


def test_provide_default_chi():
    id_measure = 1
    id_subsector = 2
    id_action_type = 3
    basic_chi = Table(
        [
            {
                'id_subsector': 2,
                'id_action_type': 3,
                '2020': 99,
            }
        ]
    )
    result = fuel_split._provide_default_chi(
        id_measure,
        id_subsector,
        id_action_type,
        'mocked_years',
        basic_chi,
    )
    assert result['2020'][1, 2, 3] == 99


class TestRawLambda:
    def test_eurostat_mode(self):
        mocked_frame = Mock()
        mocked_frame.reduce = Mock('mocked_result')

        mocked_data_source = Mock()
        mocked_data_source.table = Mock(mocked_frame)

        id_mode = 3

        result = fuel_split._raw_lambda(
            mocked_data_source,
            id_mode,
            'mocked_id_region',
            'mocked_subsector_ids',
        )

        assert result == 'mocked_result'

    class TestPrimesMode:
        def test_with_table(self):
            mocked_frame = Mock()
            mocked_frame.reduce = Mock('mocked_result')

            mocked_data_source = Mock()
            mocked_data_source.table = Mock(mocked_frame)

            id_mode = 1

            result = fuel_split._raw_lambda(
                mocked_data_source,
                id_mode,
                'mocked_id_region',
                'mocked_subsector_ids',
            )

            assert result == 'mocked_result'

        def test_without_table(self):
            mocked_frame = Mock()
            mocked_frame.reduce = Mock('mocked_result')

            mocked_data_source = Mock()
            mocked_data_source.table = Mock(None)

            id_mode = 1

            with raises(NotImplementedError):
                fuel_split._raw_lambda(
                    mocked_data_source,
                    id_mode,
                    'mocked_id_region',
                    'mocked_subsector_ids',
                )
