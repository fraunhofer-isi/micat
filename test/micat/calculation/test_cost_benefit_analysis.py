# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access

from micat.calculation import cost_benefit_analysis, extrapolation
from micat.calculation.social import lifetime
from micat.table.table import Table
from micat.test_utils.isi_mock import Mock, patch


@patch(
    lifetime.measure_specific_lifetime,
    Mock('mocked_lifetime'),
)
@patch(
    cost_benefit_analysis._subsidy_rate_by_measure,
    Mock('mocked_subsidy_rate'),
)
def test_parameters():
    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_reduce')

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    mocked_final_energy_saving_by_action_type = Mock()
    mocked_final_energy_saving_by_action_type.years = ['2000']

    parameters = cost_benefit_analysis.parameters(
        mocked_final_energy_saving_by_action_type,
        1,
        mocked_data_source,
    )
    assert parameters['lifetime'] == 'mocked_lifetime'
    assert parameters['subsidyRate'] == 'mocked_subsidy_rate'


@patch(
    extrapolation.extrapolate_series,
    Mock('mocked_result'),
)
def test_default_subsidy_rate():
    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_reduce')

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    result = cost_benefit_analysis._default_subsidy_rate(
        mocked_data_source,
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


@patch(
    cost_benefit_analysis._default_subsidy_rate,
    Mock(Mock()),
)
def test_subsidy_rate_by_measure():
    mocked_subsidy_rate = Table([{'id_measure': 1, 'id_subsector': 2, 'id_action_type': 3, '2000': 99}])

    def mocked_measure_specific_parameter(_energy_saving, _id_parameter, provide_default, _is_value_table=False):
        mocked_value = provide_default(1, 2, 3, 'mocked_year', 'mocked_saving')
        assert mocked_value
        return mocked_subsidy_rate

    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_reduce')

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)
    mocked_data_source.measure_specific_parameter = mocked_measure_specific_parameter

    mocked_final_energy_saving_by_action_type = Mock()
    mocked_final_energy_saving_by_action_type.years = ['2000']

    result = cost_benefit_analysis._subsidy_rate_by_measure(
        mocked_final_energy_saving_by_action_type,
        mocked_data_source,
        'mocked_id_region',
    )
    assert result['2000'][1] == 99
