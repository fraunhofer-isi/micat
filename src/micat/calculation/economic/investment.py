# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/38
from micat.calculation import extrapolation


def annual_investment_cost_in_euro(final_energy_saving_by_action_type, data_source):
    # Investment cost is specified as cumulated data
    # in order to determine the annual investment, we subtract the
    # value of the previous year (or zero).
    # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat_confidential/-/issues/461
    cumulated_investment_cost = investment_cost_in_euro(
        final_energy_saving_by_action_type,
        data_source,
    )

    years = final_energy_saving_by_action_type.years
    annual_years = _annual_years(years)
    interpolated_cumulated_investment_cost = extrapolation.extrapolate(cumulated_investment_cost, annual_years)
    annual_investment_cost = interpolated_cumulated_investment_cost.map(
        lambda value, index, column_name: _difference_to_previous_year(
            value, index, column_name, interpolated_cumulated_investment_cost
        )
    )

    filtered_annual_investment_cost = extrapolation.extrapolate(annual_investment_cost, years)
    return filtered_annual_investment_cost


def investment_cost_in_euro(
    final_energy_saving_by_action_type,
    data_source,
):
    years = final_energy_saving_by_action_type.years
    investment_cost_per_ktoe = _investment_cost_per_ktoe(data_source, years)

    def _provide_default_investment(_id_measure, _id_subsector, id_action_type, year, saving):
        default_investment = _default_investment(
            saving,
            investment_cost_per_ktoe,
            id_action_type,
            year,
        )
        # Round to 2 decimal places (not anymore: and convert to million euros)
        return round(default_investment, 2)

    investment = data_source.measure_specific_parameter(
        final_energy_saving_by_action_type,
        40,  # id_parameter for investment cost
        _provide_default_investment,
    )

    del investment["id_subsector"]
    return investment


def _annual_years(years):
    first_year = years[0]
    last_year = years[len(years) - 1]
    annual_years = list(range(first_year, last_year + 1))
    return annual_years


def _difference_to_previous_year(
    value,
    index,
    column_name,
    cumulated_data,
):
    year = int(column_name)
    previous_year = year - 1
    previous_column_name = str(previous_year)
    if previous_column_name in cumulated_data:
        previous_value = cumulated_data[previous_column_name][index]
        difference = value - previous_value
        return difference
    else:
        return value


def _default_investment(
    saving,
    investment_cost_per_ktoe,
    id_action_type,
    year,
):
    specific_investment_cost = _specific_investment_cost(investment_cost_per_ktoe, id_action_type, year)
    investment = saving * specific_investment_cost
    # Convert to million euros, otherwise the results will be displayed in mio. €
    return investment * 1_000_000


def _specific_investment_cost(
    investment_cost_per_ktoe,
    id_action_type,
    year,
):
    specific_investment_cost_series = investment_cost_per_ktoe.reduce("id_action_type", id_action_type)
    specific_investment_cost = specific_investment_cost_series[str(year)]
    return specific_investment_cost


def _investment_cost_per_ktoe(data_source, years):
    e3m_global_parameters = data_source.table("41_48_investments_and_actions_per_ktoe", {})
    investment_cost_per_ktoe_raw = e3m_global_parameters.reduce("id_parameter", 41)

    investment_cost_per_ktoe = extrapolation.extrapolate(investment_cost_per_ktoe_raw, years)
    return investment_cost_per_ktoe
