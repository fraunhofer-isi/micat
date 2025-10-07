# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/25
from micat.calculation import extrapolation
from micat.calculation.economic import investment
from micat.calculation.social import dwelling, lifetime
from micat.input.data_source import DataSource


# pylint: disable=too-many-locals
def alleviation_of_energy_poverty_on_national_level(
    final_energy_saving_or_capacities,
    population_of_municipality,
    reduction_of_energy_cost,
    data_source,
    id_region,
    mode_2m=False,
    number_of_affected_dwellings=None,
):
    years = final_energy_saving_or_capacities.years

    energy_poverty_gap_owner, energy_poverty_gap_tenant = _energy_poverty_gap(data_source, id_region, years, mode_2m)

    measure_specific_lifetime = lifetime.measure_specific_lifetime(final_energy_saving_or_capacities, data_source)

    wuppertal_parameters = data_source.table("wuppertal_parameters", {"id_region": str(id_region)})

    wuppertal_constant_parameters = data_source.table("wuppertal_constant_parameters", {"id_region": str(id_region)})

    if mode_2m:
        equivalence_coefficient = wuppertal_constant_parameters.reduce("id_parameter", 60)
    else:
        equivalence_coefficient = wuppertal_constant_parameters.reduce("id_parameter", 59)

    policy_targetedness = _extrapolated_series(25, wuppertal_parameters, years)

    average_rent = data_source.measure_specific_parameter_using_default_table(
        final_energy_saving_or_capacities,
        29,
        wuppertal_parameters,
    )

    average_size = _extrapolated_series(30, wuppertal_parameters, years)

    owner_occupier_rate = _extrapolated_series(33, wuppertal_parameters, years)

    rent_premium = data_source.measure_specific_parameter_using_default_table(
        final_energy_saving_or_capacities,
        34,
        wuppertal_parameters,
    )

    subsidy_rate = _extrapolated_series(35, wuppertal_parameters, years)

    if number_of_affected_dwellings is None:
        number_of_affected_dwellings = dwelling.number_of_affected_dwellings(
            final_energy_saving_or_capacities,
            data_source,
            id_region,
            population_of_municipality,
        )

    investment_in_euro = investment.investment_cost_in_euro(
        final_energy_saving_or_capacities,
        data_source,
    )

    share_of_energy_poor_population_owner_occupiers = _share_of_energy_poor_population_owner(
        final_energy_saving_or_capacities,
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
        final_energy_saving_or_capacities,
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
    wuppertal_decile_parameters = data_source.table("wuppertal_decile_parameters", {"id_region": str(id_region)})
    extrapolated_decile_parameters = extrapolation.extrapolate(wuppertal_decile_parameters, years)
    if mode_2m:
        energy_poverty_gap_owner = extrapolated_decile_parameters.reduce("id_parameter", 57)
        energy_poverty_gap_tenant = extrapolated_decile_parameters.reduce("id_parameter", 58)
    else:
        energy_poverty_gap_owner = extrapolated_decile_parameters.reduce("id_parameter", 27)
        energy_poverty_gap_tenant = extrapolated_decile_parameters.reduce("id_parameter", 28)
    return energy_poverty_gap_owner, energy_poverty_gap_tenant


def _extrapolated_series(id_parameter, parameters, years):
    annual_series = parameters.reduce("id_parameter", id_parameter)
    extrapolated_series = extrapolation.extrapolate_series(annual_series, years)
    return extrapolated_series


def _measure_specific_share_of_energy_poor_population_owner(
    id_measure,
    id_subsector,
    id_action_type,
    years,
    share_input,
):
    zero_table = DataSource.row_table(id_measure, years, 0)
    if id_subsector != 17:
        return zero_table

    if id_action_type in [5, 6]:
        return zero_table

    if id_action_type in [1, 2, 3]:
        annual_values = _measure_specific_share_of_energy_poor_population_owner_others(share_input)
        table = annual_values.transpose("id_measure", id_measure)
        return table
    elif id_action_type == 4:
        annual_values = _measure_specific_share_of_energy_poor_population_electric(share_input)
        table = annual_values.transpose("id_measure", id_measure)
        return table

    else:
        message = "Unknown id_ind_use value " + str(id_action_type) + " for subsector 17 (residential)"
        raise KeyError(message)


def _measure_specific_share_of_energy_poor_population_electric(share_input):
    reduction_of_energy_cost = share_input["reduction_of_energy_cost"]
    investment_in_euro = share_input["investment_in_euro"]
    m2_equivalence_coefficient = share_input["m2_equivalence_coefficient"]
    number_of_affected_dwellings = share_input["number_of_affected_dwellings"]
    measure_specific_lifetime = share_input["lifetime"]
    subsidy_rate = share_input["subsidy_rate"]
    energy_poverty_gap = share_input["energy_poverty_gap"]

    delta_di = (
        reduction_of_energy_cost / m2_equivalence_coefficient
        - investment_in_euro / m2_equivalence_coefficient / measure_specific_lifetime * (1 - subsidy_rate / 100)
    ) / number_of_affected_dwellings

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap)
        return number_for_value

    number_of_deciles = delta_di.map(number_of_smaller_deciles)

    share = number_of_deciles / 10
    return share


def _measure_specific_share_of_energy_poor_population_owner_others(share_input):
    reduction_of_energy_cost = share_input["reduction_of_energy_cost"]
    investment_in_euro = share_input["investment_in_euro"]
    m2_equivalence_coefficient = share_input["m2_equivalence_coefficient"]
    number_of_affected_dwellings = share_input["number_of_affected_dwellings"]
    measure_specific_lifetime = share_input["lifetime"]
    subsidy_rate = share_input["subsidy_rate"]
    energy_poverty_gap = share_input["energy_poverty_gap"]

    delta_di = (
        reduction_of_energy_cost / m2_equivalence_coefficient
        - investment_in_euro / m2_equivalence_coefficient / measure_specific_lifetime * (1 - subsidy_rate / 100)
    ) / number_of_affected_dwellings

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap)
        return number_for_value

    number_of_deciles = delta_di.map(number_of_smaller_deciles)
    share = number_of_deciles / 10
    return share


def _measure_specific_share_of_energy_poor_population_tenant(
    id_measure,
    id_subsector,
    id_action_type,
    years,
    share_input,
):
    zero_row_table = DataSource.row_table(id_measure, years, 0)
    if id_subsector != 17:
        return zero_row_table

    if id_action_type in [5, 6]:
        return zero_row_table

    elif id_action_type in [1, 2, 3]:
        annual_values = _measure_specific_share_of_energy_poor_population_tenant_others(share_input)
        table = annual_values.transpose("id_measure", id_measure)
        return table
    elif id_action_type == 4:
        annual_values = _measure_specific_share_of_energy_poor_population_electric(share_input)
        table = annual_values.transpose("id_measure", id_measure)
        return table

    else:
        message = "Unknown id_action_type value" + str(id_action_type) + " for subsector 17 (residential)"
        raise KeyError(message)


def _measure_specific_share_of_energy_poor_population_tenant_others(share_input):
    reduction_of_energy_cost = share_input["reduction_of_energy_cost"]
    m2_equivalence_coefficient = share_input["m2_equivalence_coefficient"]
    number_of_affected_dwellings = share_input["number_of_affected_dwellings"]
    rent_premium = share_input["rent_premium"]
    average_rent = share_input["average_rent"]
    energy_poverty_gap = share_input["energy_poverty_gap"]

    delta_di = (
        (reduction_of_energy_cost - rent_premium / 100 * average_rent)
        / number_of_affected_dwellings
        / m2_equivalence_coefficient
    )

    def number_of_smaller_deciles(value, year):
        number_for_value = _number_of_smaller_deciles(value, year, energy_poverty_gap)
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
    final_energy_saving_or_capacities,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    measure_specific_lifetime,
    subsidy_rate,
    energy_poverty_gap,
    number_of_affected_dwellings,
    investment_in_euro,
    data_source,
):
    years = final_energy_saving_or_capacities.years

    def _determine_table_for_measure(
        id_measure,
        id_subsector,
        id_action_type,
        _energy_saving,
        _extrapolated_final_parameters=None,
        _extrapolated_parameters=None,
        _constants=None,
    ):
        reduction_of_energy_cost_by_energy_carrier = reduction_of_energy_cost.reduce("id_measure", id_measure)
        reduction_of_energy_cost_for_measure = reduction_of_energy_cost_by_energy_carrier.sum()

        lifetime_for_measure = measure_specific_lifetime.reduce("id_measure", id_measure)
        number_of_affected_dwellings_for_measure = number_of_affected_dwellings.reduce("id_measure", id_measure)
        investment_in_euro_for_measure = investment_in_euro.reduce("id_measure", id_measure)

        share_input = {
            "reduction_of_energy_cost": reduction_of_energy_cost_for_measure,
            "m2_equivalence_coefficient": m2_equivalence_coefficient,
            "number_of_affected_dwellings": number_of_affected_dwellings_for_measure,
            "investment_in_euro": investment_in_euro_for_measure,
            "lifetime": lifetime_for_measure,
            "subsidy_rate": subsidy_rate,
            "energy_poverty_gap": energy_poverty_gap,
        }

        table = _measure_specific_share_of_energy_poor_population_owner(
            id_measure,
            id_subsector,
            id_action_type,
            years,
            share_input,
        )
        return table

    share = data_source.measure_specific_calculation(
        final_energy_saving_or_capacities,
        _determine_table_for_measure,
        _determine_table_for_measure,
    )
    return share


# pylint: disable = too-many-arguments, too-many-positional-arguments
def _share_of_energy_poor_population_tenant(
    final_energy_saving_or_capacities,
    reduction_of_energy_cost,
    m2_equivalence_coefficient,
    measure_specific_lifetime,
    subsidy_rate,
    rent_premium,
    average_rent,
    energy_poverty_gap,
    number_of_affected_dwellings,
    investment_in_euro,
    data_source,
):
    years = final_energy_saving_or_capacities.years

    def _determine_table_for_measure(
        id_measure,
        id_subsector,
        id_action_type,
        _energy_saving,
        _extrapolated_final_parameters=None,
        _extrapolated_parameters=None,
        _constants=None,
    ):
        reduction_of_energy_cost_by_energy_carrier = reduction_of_energy_cost.reduce("id_measure", id_measure)

        share_input = {
            "subsidy_rate": subsidy_rate,
            "energy_poverty_gap": energy_poverty_gap,
            "reduction_of_energy_cost": reduction_of_energy_cost_by_energy_carrier.sum(),
            "m2_equivalence_coefficient": m2_equivalence_coefficient,
            "number_of_affected_dwellings": number_of_affected_dwellings.reduce("id_measure", id_measure),
            "investment_in_euro": investment_in_euro.reduce("id_measure", id_measure),
            "lifetime": measure_specific_lifetime.reduce("id_measure", id_measure),
            "rent_premium": rent_premium.reduce("id_measure", id_measure),
            "average_rent": average_rent.reduce("id_measure", id_measure),
        }

        table = _measure_specific_share_of_energy_poor_population_tenant(
            id_measure,
            id_subsector,
            id_action_type,
            years,
            share_input,
        )
        return table

    share = data_source.measure_specific_calculation(
        final_energy_saving_or_capacities,
        _determine_table_for_measure,
        _determine_table_for_measure,
    )

    return share
