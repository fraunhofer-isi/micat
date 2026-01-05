# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.calculation.social import lifetime
from micat.calculation.economic.investment import _annual_years, investment_cost_in_euro


def parameters(
    final_energy_saving_or_capacities,
    ecologic_indicators,
    id_region,
    data_source,
    starting_year,
):
    measure_specific_lifetime = lifetime.measure_specific_lifetime(
        final_energy_saving_or_capacities,
        data_source,
    )

    subsidy_rate = _subsidy_rate_by_measure(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    )

    years_to_extrapolate = final_energy_saving_or_capacities.years.copy()
    if starting_year and starting_year not in years_to_extrapolate:
        years_to_extrapolate = [starting_year] + years_to_extrapolate
    years_to_extrapolate = _annual_years(years_to_extrapolate)
    extrapolated_final_energy_saving_or_capacities = extrapolation.extrapolate(
        final_energy_saving_or_capacities, years_to_extrapolate
    )

    extrapolated_final_energy_saving_or_capacities = extrapolated_final_energy_saving_or_capacities.droplevel(
        ["id_subsector", "id_action_type"]
    )

    investment_costs = investment_cost_in_euro(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    ).droplevel(["id_action_type"])
    extrapolated_investment_costs = extrapolation.extrapolate(investment_costs, years_to_extrapolate)

    extrapolated_co2_savings = extrapolation.extrapolate(
        ecologic_indicators["reductionOfGreenHouseGasEmission"], years_to_extrapolate
    )

    cost_benefit_analysis_parameters = {
        "lifetime": measure_specific_lifetime,
        "subsidyRate": subsidy_rate,
        "totalAnnualEnergySavings": extrapolated_final_energy_saving_or_capacities,
        "totalAnnualCO2Savings": extrapolated_co2_savings,
        "investmentCosts": extrapolated_investment_costs,
    }
    return cost_benefit_analysis_parameters


def _default_subsidy_rate(
    data_source,
    id_region,
    years,
):
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": "35",
    }
    raw_subsidy_rate = data_source.annual_series("wuppertal_parameters", where_clause)
    subsidy_rate = extrapolation.extrapolate_series(raw_subsidy_rate, years)
    return subsidy_rate


def _subsidy_rate_by_measure(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
):
    years = final_energy_saving_or_capacities.years
    default_subsidy_rate = _default_subsidy_rate(data_source, id_region, years)

    def provide_default_subsidy_rate(_id_measure, _id_subsector, _id_action_type, year, _saving):
        value = default_subsidy_rate[str(year)]
        return value

    id_parameter = 35
    subsidy_rate = data_source.measure_specific_parameter(
        final_energy_saving_or_capacities,
        id_parameter,
        provide_default_subsidy_rate,
    )
    del subsidy_rate["id_subsector"]
    del subsidy_rate["id_action_type"]

    return subsidy_rate
