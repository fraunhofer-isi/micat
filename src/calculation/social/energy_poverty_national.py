# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/25
from calculation import extrapolation
from calculation.economic import investment
from calculation.social import dwelling, lifetime
from input.data_source import DataSource


# pylint: disable=too-many-locals
def alleviation_of_energy_poverty_on_national_level(
    final_energy_saving_by_action_type,
    population_of_municipality,
    reduction_of_energy_cost,
    data_source,
    id_region,
    mode_2m=False,
    number_of_affected_dwellings=None,
):
    years = final_energy_saving_by_action_type.years

    energy_poverty_gap_owner, energy_poverty_gap_tenant = _energy_poverty_gap(data_source, id_region, years, mode_2m)

    measure_specific_lifetime = lifetime.measure_specific_lifetime(final_energy_saving_by_action_type, data_source)

    wuppertal_parameters = data_source.table('wuppertal_parameters', {'id_region': str(id_region)})

    wuppertal_constant_parameters = data_source.table('wuppertal_constant_parameters', {'id_region': str(id_region)})

    if mode_2m:
        equivalence_coefficient = wuppertal_constant_parameters.reduce('id_parameter', 60)
    else:
        equivalence_coefficient = wuppertal_constant_parameters.reduce('id_parameter', 59)

    policy_targetedness = _extrapolated_series(25, wuppertal_parameters, years)

    average_rent = data_source.measure_specific_parameter_using_default_table(
        final_energy_saving_by_action_type,
        29,
        wuppertal_parameters,
    )

    average_size = _extrapolated_series(30, wuppertal_parameters, years)

    owner_occupier_rate = _extrapolated_series(33, wuppertal_parameters, years)

    rent_premium = data_source.measure_specific_parameter_using_default_table(
        final_energy_saving_by_action_type,
        34,
        wuppertal_parameters,
    )

    subsidy_rate = _extrapolated_series(35, wuppertal_parameters, years)

    if number_of_affected_dwellings is None:
        number_of_affected_dwellings = dwelling.number_of_affected_dwellings(
            final_energy_saving_by_action_type,
            data_source,
            id_region,
            population_of_municipality,
        )

    investment_in_euro = investment.investment_cost_in_euro(
        final_energy_saving_by_action_type,
        data_source,
    )

    share_of_energy_poor_population_owner_occupiers = _share_of_energy_poor_population_owner(
        final_energy_saving_by_action_type,
        reduction_of_energy_cost,
        equivalence_coefficient,
        measure_specific_lifetime,
        subsidy_rate,
        energy_poverty_gap_owner,
        number_of_affected_dwellings,
        investment_in_euro,
        data_source,
    )

    share_of_energy_poor_population_tenant = _share_of_energy_poor_population_tenant(
        final_energy_saving_by_action_type,
        reduction_of_energy_cost,
        equivalence_coefficient,
        measure_specific_lifetime,
        subsidy_rate,
        rent_premium,
        average_rent,
        energy_poverty_gap_tenant,
        number_of_affected_dwellings,
        investment_in_euro,
        data_source,
    )

    reduction = (
        number_of_affected_dwellings
        * policy_targetedness
        / 100
        * average_size
        * (
            share_of_energy_poor_population_owner_occupiers * owner_occupier_rate
            + share_of_energy_poor_population_tenant * (1 - owner_occupier_rate)
        )
    )

    return reduction


def _energy_poverty_gap(data_source, id_region, years, mode_2m=False):
    wuppertal_decile_parameters = data_source.table('wuppertal_decile_parameters', {'id_region': str(id_region)})
    extrapolated_decile_parameters = extrapolation.extrapolate(wuppertal_decile_parameters, years)
    if mode_2m:
        energy_poverty_gap_owner = extrapolated_decile_parameters.reduce('id_parameter', 57)
        energy_poverty_gap_tenant = extrapolated_decile_parameters.reduce('id_parameter', 58)
    else:
        energy_poverty_gap_owner = extrapolated_decile_parameters.reduce('id_parameter', 27)
        energy_poverty_gap_tenant = extrapolated_decile_parameters.reduce('id_parameter', 28)
    return energy_poverty_gap_owner, energy_poverty_gap_tenant


def _extrapolated_series(id_parameter, parameters, years):
    annual_series = parameters.reduce('id_parameter', id_parameter)
    extrapolated_series = extrapolation.extrapolate_series(annual_series, years)
    return extrapolated_series


# pylint: disable = too-many-arguments
def _measure_specific_share_of_energy_poor_population_owner(
    id_measure,
    id_subsector,
    id_action_type,
    years,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    number_of_affected_dwellings,
    investment_in_euro,
    measure_specific_lifetime,
    subsidy_rate,
    energy_poverty_gap_owner,
):
    zero_table = DataSource.row_table(id_measure, years, 0)
    if id_subsector != 17:
        return zero_table

    if id_action_type in [5, 6]:
        return zero_table

    if id_action_type in [1, 2, 3]:
        annual_values = _measure_specific_share_of_energy_poor_population_owner_others(
            reduction_of_energy_cost,
            m2_equivalence_coefficient,
            number_of_affected_dwellings,
            investment_in_euro,
            measure_specific_lifetime,
            subsidy_rate,
            energy_poverty_gap_owner,
        )
        table = annual_values.transpose('id_measure', id_measure)
        return table
    elif id_action_type == 4:
        annual_values = _measure_specific_share_of_energy_poor_population_electric(
            reduction_of_energy_cost,
            m2_equivalence_coefficient,
            number_of_affected_dwellings,
            investment_in_euro,
            measure_specific_lifetime,
            subsidy_rate,
            energy_poverty_gap_owner,
        )
        table = annual_values.transpose('id_measure', id_measure)
        return table

    else:
        message = 'Unknown id_ind_use value ' + str(id_action_type) + ' for subsector 17 (residential)'
        raise KeyError(message)


def _measure_specific_share_of_energy_poor_population_electric(
    energy_cost_savings,
    m2_equivalence_coefficient,
    number_of_renovated_dwellings,
    investment_in_euro,
    measure_specific_lifetime,
    subsidy_rate,
    energy_poverty_gap,
):
    delta_di = (
        energy_cost_savings / m2_equivalence_coefficient
        - investment_in_euro / m2_equivalence_coefficient / measure_specific_lifetime * (1 - subsidy_rate / 100)
    ) / number_of_renovated_dwellings

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap)
        return number_for_value

    number_of_deciles = delta_di.map(number_of_smaller_deciles)

    share = number_of_deciles / 10
    return share


def _measure_specific_share_of_energy_poor_population_owner_others(
    energy_cost_savings,
    m2_equivalence_coefficient,
    number_of_affected_dwellings,
    investment_in_euro,
    measure_specific_lifetime,
    subsidy_rate,
    energy_poverty_gap_owner,
):
    delta_di = (
        energy_cost_savings / m2_equivalence_coefficient
        - investment_in_euro / m2_equivalence_coefficient / measure_specific_lifetime * (1 - subsidy_rate / 100)
    ) / number_of_affected_dwellings

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap_owner)
        return number_for_value

    number_of_deciles = delta_di.map(number_of_smaller_deciles)
    share = number_of_deciles / 10
    return share


# pylint: disable = too-many-arguments
def _measure_specific_share_of_energy_poor_population_tenant(
    id_measure,
    id_subsector,
    id_action_type,
    years,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    number_of_affected_dwellings,
    investment_in_euro,
    lifetime_for_measure,
    subsidy_rate,
    rent_premium,
    average_rent,
    energy_poverty_gap_tenant,
):
    zero_row_table = DataSource.row_table(id_measure, years, 0)
    if id_subsector != 17:
        return zero_row_table

    if id_action_type in [5, 6]:
        return zero_row_table

    elif id_action_type in [1, 2, 3]:
        annual_values = _measure_specific_share_of_energy_poor_population_tenant_others(
            reduction_of_energy_cost,
            m2_equivalence_coefficient,
            number_of_affected_dwellings,
            rent_premium,
            average_rent,
            energy_poverty_gap_tenant,
        )
        table = annual_values.transpose('id_measure', id_measure)
        return table
    elif id_action_type == 4:
        annual_values = _measure_specific_share_of_energy_poor_population_electric(
            reduction_of_energy_cost,
            m2_equivalence_coefficient,
            number_of_affected_dwellings,
            investment_in_euro,
            lifetime_for_measure,
            subsidy_rate,
            energy_poverty_gap_tenant,
        )
        table = annual_values.transpose('id_measure', id_measure)
        return table

    else:
        message = 'Unknown id_action_type value' + str(id_action_type) + ' for subsector 17 (residential)'
        raise KeyError(message)


def _measure_specific_share_of_energy_poor_population_tenant_others(
    energy_cost_savings,
    m2_equivalence_coefficient,
    number_of_affected_dwellings,
    rent_premium,
    average_rent,
    energy_poverty_gap_tenant,
):
    delta_di = (
        energy_cost_savings / m2_equivalence_coefficient - rent_premium / 100 * average_rent
    ) / number_of_affected_dwellings

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap_tenant)
        return number_for_value

    number_of_deciles = delta_di.map(number_of_smaller_deciles)
    share = number_of_deciles / 10
    return share


def _number_of_smaller_deciles(value, year, decile_values):
    annual_decile_values = decile_values[year]
    value_larger_then_decile_value = annual_decile_values < value
    number_of_smaller_deciles = value_larger_then_decile_value.sum()
    return number_of_smaller_deciles


def _provide_default_investment(
    _id_measure,
    _id_subsector,
    _id_action_type,
    _year,
):
    return 0


def _provide_default_renovation_rate(
    _id_measure,
    _id_subsector,
    _id_action_type,
    _year,
):
    return 0


def _share_of_energy_poor_population_owner(
    final_energy_saving_by_action_type,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    measure_specific_lifetime,
    subsidy_rate,
    energy_poverty_gap_owner,
    number_of_affected_dwellings,
    investment_in_euro,
    data_source,
):
    years = final_energy_saving_by_action_type.years

    def _determine_table_for_measure(
        id_measure,
        id_subsector,
        id_action_type,
        _energy_saving,
        _extrapolated_final_parameters=None,
        _extrapolated_parameters=None,
        _constants=None,
    ):
        reduction_of_energy_cost_by_energy_carrier = reduction_of_energy_cost.reduce('id_measure', id_measure)
        reduction_of_energy_cost_for_measure = reduction_of_energy_cost_by_energy_carrier.sum()

        lifetime_for_measure = measure_specific_lifetime.reduce('id_measure', id_measure)
        number_of_affected_dwellings_for_measure = number_of_affected_dwellings.reduce('id_measure', id_measure)
        investment_in_euro_for_measure = investment_in_euro.reduce('id_measure', id_measure)

        table = _measure_specific_share_of_energy_poor_population_owner(
            id_measure,
            id_subsector,
            id_action_type,
            years,
            reduction_of_energy_cost_for_measure,
            m2_equivalence_coefficient,
            number_of_affected_dwellings_for_measure,
            investment_in_euro_for_measure,
            lifetime_for_measure,
            subsidy_rate,
            energy_poverty_gap_owner,
        )
        return table

    share = data_source.measure_specific_calculation(
        final_energy_saving_by_action_type,
        _determine_table_for_measure,
        _determine_table_for_measure,
    )
    return share


# pylint: disable = too-many-arguments
def _share_of_energy_poor_population_tenant(
    final_energy_saving_by_action_type,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    measure_specific_lifetime,
    subsidy_rate,
    rent_premium,
    average_rent,
    energy_poverty_gap_tenant,
    number_of_affected_dwellings,
    investment_in_euro,
    data_source,
):
    years = final_energy_saving_by_action_type.years

    def _determine_table_for_measure(
        id_measure,
        id_subsector,
        id_action_type,
        _energy_saving,
        _extrapolated_final_parameters=None,
        _extrapolated_parameters=None,
        _constants=None,
    ):
        reduction_of_energy_cost_by_energy_carrier = reduction_of_energy_cost.reduce('id_measure', id_measure)
        reduction_of_energy_cost_for_measure = reduction_of_energy_cost_by_energy_carrier.sum()

        lifetime_for_measure = measure_specific_lifetime.reduce('id_measure', id_measure)

        rent_premium_for_measure = rent_premium.reduce('id_measure', id_measure)
        average_rent_for_measure = average_rent.reduce('id_measure', id_measure)

        number_of_renovated_dwellings_for_measure = number_of_affected_dwellings.reduce('id_measure', id_measure)
        investment_in_euro_for_measure = investment_in_euro.reduce('id_measure', id_measure)

        table = _measure_specific_share_of_energy_poor_population_tenant(
            id_measure,
            id_subsector,
            id_action_type,
            years,
            reduction_of_energy_cost_for_measure,
            m2_equivalence_coefficient,
            number_of_renovated_dwellings_for_measure,
            investment_in_euro_for_measure,
            lifetime_for_measure,
            subsidy_rate,
            rent_premium_for_measure,
            average_rent_for_measure,
            energy_poverty_gap_tenant,
        )
        return table

    share = data_source.measure_specific_calculation(
        final_energy_saving_by_action_type,
        _determine_table_for_measure,
        _determine_table_for_measure,
    )

    return share
