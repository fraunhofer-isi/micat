# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation, social
from micat.calculation.economic import investment
from micat.calculation.social import energy_poverty_national
from micat.input.data_source import DataSource
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch, raises


@patch(
    energy_poverty_national._energy_poverty_gap,
    ['mocked_energy_poverty_gap_owner', 'mocked_energy_poverty_gap_tenant'],
)
@patch(
    social.lifetime.measure_specific_lifetime,
    'mocked_lifetime',
)
@patch(
    energy_poverty_national._extrapolated_series,
    AnnualSeries({'2000': 1}),
)
@patch(social.dwelling.dwelling_stock)
@patch(
    social.dwelling.number_of_affected_dwellings,
    Table([{'id_measure': 1, '2000': 1}]),
)
@patch(
    investment.investment_cost_in_euro,
    Table([{'id_measure': 1, '2000': 1}]),
)
@patch(
    energy_poverty_national._share_of_energy_poor_population_owner,
    Table([{'id_measure': 1, '2000': 1}]),
)
@patch(
    energy_poverty_national._share_of_energy_poor_population_tenant,
    Table([{'id_measure': 1, '2000': 1}]),
)
class TestAlleviationOfEnergyPoverty:
    def test_mode_m2(self):
        final_energy_saving_by_action_type = Mock()
        data_source = Mock()

        result = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            final_energy_saving_by_action_type,
            'mocked_population_of_municipality',
            'mocked_reduction_of_energy_cost',
            data_source,
            'mocked_id_region',
        )
        assert result['2000'][1] == 0.01

    def test_mode_2m(self):
        final_energy_saving_by_action_type = Mock()
        data_source = Mock()

        result = energy_poverty_national.alleviation_of_energy_poverty_on_national_level(
            final_energy_saving_by_action_type,
            'mocked_population_of_municipality',
            'mocked_reduction_of_energy_cost',
            data_source,
            'mocked_id_region',
            True,
        )
        assert result['2000'][1] == 0.01


class TestEnergyPovertyGap:
    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_result')
    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    def test_mode_m2(self):
        with patch(
            extrapolation.extrapolate,
            Mock(self.mocked_table),
        ):
            result = energy_poverty_national._energy_poverty_gap(
                self.mocked_data_source, 'mocked_id_region', 'mocked_years'
            )
            assert result == ('mocked_result', 'mocked_result')

    def test_mode_2m(self):
        with patch(
            extrapolation.extrapolate,
            Mock(self.mocked_table),
        ):
            result = energy_poverty_national._energy_poverty_gap(
                self.mocked_data_source,
                'mocked_id_region',
                'mocked_years',
                True,
            )
            assert result == ('mocked_result', 'mocked_result')


@patch(
    extrapolation.extrapolate_series,
    'mocked_result',
)
def test_extrapolated_series():
    id_parameter = 1
    parameters = Table(
        [
            {'id_parameter': 1, '2000': 1, '2010': 3},
        ]
    )
    years = [2000, 2005]
    result = energy_poverty_national._extrapolated_series(
        id_parameter,
        parameters,
        years,
    )
    assert result == 'mocked_result'


class TestMeasureSpecificShareOfEnergyPoorPopulationOwner:
    @patch(DataSource.row_table, 'mocked_result')
    def test_non_residential(self):
        id_subsector = 1

        result = energy_poverty_national._measure_specific_share_of_energy_poor_population_owner(
            'mocked_id_measure',
            id_subsector,
            'mocked_id_action_type',
            'mocked_years',
            'mocked_share_input',
        )
        assert result == 'mocked_result'

    class TestResidential:
        id_subsector = 17
        extrapolated_final_parameters = Mock()

        @patch(
            DataSource.row_table,
            'mocked_result',
        )
        def test_action_type_1_2_3(self):
            id_action_type = 1

            mocked_series = Mock()
            mocked_series.transpose = Mock('mocked_result')

            with patch(
                energy_poverty_national._measure_specific_share_of_energy_poor_population_owner_others,
                Mock(mocked_series),
            ):
                result = energy_poverty_national._measure_specific_share_of_energy_poor_population_owner(
                    'mocked_id_measure',
                    self.id_subsector,
                    id_action_type,
                    self.extrapolated_final_parameters,
                    'mocked_share_input',
                )
                assert result == 'mocked_result'

        @patch(DataSource.row_table, 'mocked_result')
        def test_action_type_4(self):
            id_action_type = 4

            mocked_series = Mock()
            mocked_series.transpose = Mock('mocked_result')

            with patch(
                energy_poverty_national._measure_specific_share_of_energy_poor_population_electric,
                Mock(mocked_series),
            ):
                result = energy_poverty_national._measure_specific_share_of_energy_poor_population_owner(
                    'mocked_id_measure',
                    self.id_subsector,
                    id_action_type,
                    self.extrapolated_final_parameters,
                    'mocked_share_input',
                )
                assert result == 'mocked_result'

        @patch(DataSource.row_table, 'mocked_result')
        def test_action_type_5_6(self):
            id_action_type = 5

            result = energy_poverty_national._measure_specific_share_of_energy_poor_population_owner(
                'mocked_id_measure',
                self.id_subsector,
                id_action_type,
                self.extrapolated_final_parameters,
                'mocked_share_input',
            )
            assert result == 'mocked_result'

        @patch(DataSource.row_table, 'mocked_row_table')
        def test_action_type_other(self):
            id_action_type = 8

            with raises(KeyError):
                energy_poverty_national._measure_specific_share_of_energy_poor_population_owner(
                    'mocked_id_measure',
                    self.id_subsector,
                    id_action_type,
                    self.extrapolated_final_parameters,
                    'mocked_share_input',
                )


@patch(
    energy_poverty_national._number_of_smaller_deciles,
    5,
)
def test_measure_specific_share_of_energy_poor_population_electric():
    mocked_series = AnnualSeries({'2000': 1})
    share_input = {
        'reduction_of_energy_cost': mocked_series,
        'm2_equivalence_coefficient': 2,
        'number_of_affected_dwellings': mocked_series,
        'investment_in_euro': mocked_series,
        'lifetime': mocked_series,
        'subsidy_rate': mocked_series,
        'energy_poverty_gap': mocked_series,
    }

    result = energy_poverty_national._measure_specific_share_of_energy_poor_population_electric(share_input)
    assert result['2000'] == 0.5


@patch(
    energy_poverty_national._number_of_smaller_deciles,
    5,
)
def test_measure_specific_share_of_energy_poor_population_owner_others():
    mocked_series = AnnualSeries({'2000': 1})
    share_input = {
        'reduction_of_energy_cost': mocked_series,
        'm2_equivalence_coefficient': 2,
        'number_of_affected_dwellings': mocked_series,
        'investment_in_euro': mocked_series,
        'lifetime': mocked_series,
        'subsidy_rate': mocked_series,
        'energy_poverty_gap': mocked_series,
    }

    result = energy_poverty_national._measure_specific_share_of_energy_poor_population_owner_others(share_input)
    assert result['2000'] == 0.5


class TestMeasureSpecificShareOfEnergyPoorPopulationTenant:
    @patch(DataSource.row_table, 'mocked_result')
    def test_non_residential(self):
        id_subsector = 1

        result = energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant(
            'mocked_id_measure',
            id_subsector,
            'mocked_id_action_type',
            'mocked_years',
            'mocked_share_input',
        )
        assert result == 'mocked_result'

    class TestResidential:
        id_subsector = 17
        extrapolated_final_parameters = Mock()

        mocked_series = Mock()
        mocked_series.transpose = Mock('mocked_result')

        @patch(
            energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant_others,
            Mock(mocked_series),
        )
        @patch(
            DataSource.row_table,
            'mocked_result',
        )
        def test_action_type_1_2_3(self):
            id_action_type = 1

            result = energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant(
                'mocked_id_measure',
                self.id_subsector,
                id_action_type,
                'mocked_years',
                'mocked_share_input',
            )
            assert result == 'mocked_result'

        @patch(
            energy_poverty_national._measure_specific_share_of_energy_poor_population_electric,
            Mock(mocked_series),
        )
        @patch(
            DataSource.row_table,
            'mocked_result',
        )
        def test_action_type_4(self):
            id_action_type = 4

            result = energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant(
                'mocked_id_measure',
                self.id_subsector,
                id_action_type,
                'mocked_years',
                'mocked_share_input',
            )
            assert result == 'mocked_result'

        @patch(DataSource.row_table, 'mocked_result')
        def test_action_type_5_6(self):
            id_action_type = 5

            result = energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant(
                'mocked_id_measure',
                self.id_subsector,
                id_action_type,
                'mocked_years',
                'mocked_share_input',
            )
            assert result == 'mocked_result'

        @patch(DataSource.row_table, 'mocked_row_table')
        def test_action_type_other(self):
            id_action_type = 8

            with raises(KeyError):
                energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant(
                    'mocked_id_measure',
                    self.id_subsector,
                    id_action_type,
                    'mocked_years',
                    'mocked_share_input',
                )


@patch(energy_poverty_national._number_of_smaller_deciles, 10)
def test_measure_specific_share_of_energy_poor_population_tenant_others():
    energy_cost_savings = AnnualSeries({'2000': 1})
    m2_equivalence_coefficient = 2
    number_of_affected_dwellings = 2
    rent_premium = 1
    average_rent = 2

    result = energy_poverty_national._measure_specific_sh_of_energy_poor_population_tenant_others(
        energy_cost_savings,
        m2_equivalence_coefficient,
        number_of_affected_dwellings,
        rent_premium,
        average_rent,
        'mocked_energy_poverty_gap_tenant',
    )

    assert result['2000'] == 1


def test_number_of_smaller_deciles():
    value = 0.5
    year = '2000'
    decile_values = Table(
        [
            {'id_decile': 1, '2000': 0.1},
            {'id_decile': 2, '2000': 0.2},
            {'id_decile': 3, '2000': 0.3},
            {'id_decile': 4, '2000': 0.4},
            {'id_decile': 5, '2000': 0.5},
            {'id_decile': 6, '2000': 0.6},
            {'id_decile': 7, '2000': 0.7},
            {'id_decile': 8, '2000': 0.8},
            {'id_decile': 9, '2000': 0.9},
            {'id_decile': 10, '2000': 1},
        ]
    )
    result = energy_poverty_national._number_of_smaller_deciles(value, year, decile_values)
    assert result == 4


def test_provide_default_investment():
    result = energy_poverty_national._provide_default_investment(
        'mocked_id_measure',
        'mocked__id_subsector',
        'mocked__id_action_type',
        'mocked_year',
    )
    assert result == 0


def test_provide_default_renovation_rate():
    result = energy_poverty_national._provide_default_renovation_rate(
        'mocked_id_measure',
        'mocked__id_subsector',
        'mocked__id_action_type',
        'mocked_year',
    )
    assert result == 0


def test_row_table():
    years = ['2000', '2010']
    id_measure = 2

    result = DataSource.row_table(
        id_measure,
        years,
        'mocked_value',
    )
    assert result['2000'][2] == 'mocked_value'
    assert result['2010'][2] == 'mocked_value'


@patch(energy_poverty_national._measure_specific_share_of_energy_poor_population_owner)
def test_share_of_energy_poor_population_owner():
    reduction_of_energy_cost = Mock()
    m2_equivalence_coefficient = 2
    measure_specific_lifetime = Mock()

    number_of_affected_dwellings = Mock()
    investment_in_euro = Mock()

    def mocked_measure_specific_calculation(
        _final_energy_saving_by_action_type,
        determine_table_for_measure,
        _provide_default_share_of_energy_poor_population_owner,
    ):
        determine_table_for_measure(
            'mocked_id_measure',
            'mocked_id_subsector',
            'mocked_id_action_type',
            'mocked__energy_saving',
            'mocked__extrapolated_final_parameters',
        )

        return 'mocked_result'

    data_source = Mock()
    data_source.measure_specific_calculation = mocked_measure_specific_calculation

    result = energy_poverty_national._share_of_energy_poor_population_owner(
        Mock(),
        reduction_of_energy_cost,
        m2_equivalence_coefficient,
        measure_specific_lifetime,
        'mocked_subsidy_rate',
        'mocked_energy_poverty_gap_owner',
        number_of_affected_dwellings,
        investment_in_euro,
        data_source,
    )

    assert result == 'mocked_result'


@patch(energy_poverty_national._measure_specific_share_of_energy_poor_population_tenant)
def test_share_of_energy_poor_population_tenant():
    reduction_of_energy_cost = Mock()
    m2_equivalence_coefficient = 2
    measure_specific_lifetime = Mock()
    rent_premium = Mock()

    number_of_affected_dwellings = Mock()
    investment_in_euro = Mock()

    def mocked_measure_specific_calculation(
        _final_energy_saving_by_action_type,
        determine_table_for_measure,
        _provide_default_share_of_energy_poor_population_owner,
    ):
        determine_table_for_measure(
            'mocked_id_measure',
            'mocked_id_subsector',
            'mocked_id_action_type',
            'mocked__energy_saving',
            'mocked__extrapolated_final_parameters',
        )

        return 'mocked_result'

    data_source = Mock()
    data_source.measure_specific_calculation = mocked_measure_specific_calculation

    result = energy_poverty_national._share_of_energy_poor_population_tenant(
        Mock(),
        reduction_of_energy_cost,
        m2_equivalence_coefficient,
        measure_specific_lifetime,
        'mocked_subsidy_rate',
        rent_premium,
        rent_premium,
        'mocked_energy_poverty_gap_tenant',
        number_of_affected_dwellings,
        investment_in_euro,
        data_source,
    )

    assert result == 'mocked_result'
