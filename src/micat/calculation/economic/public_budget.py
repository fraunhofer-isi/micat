# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.calculation.economic import investment


def impact_on_public_budget(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
):
    years = final_energy_saving_or_capacities.years
    action_type_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_action_type"
    )
    subsector_ids = final_energy_saving_or_capacities.unique_index_values(
        "id_subsector"
    )

    where_clause = {
        "id_region": str(id_region),
        "id_action_type": action_type_ids,
        "id_subsector": subsector_ids,
    }

    public_revenues = data_source.table(
        "public_budget_e3m",
        {**where_clause, "id_parameter": "82"},
    )
    del public_revenues["id_parameter"]
    public_revenues = extrapolation.extrapolate(public_revenues, years)

    unemployment_expenses = data_source.table(
        "public_budget_e3m",
        {**where_clause, "id_parameter": "83"},
    )
    del unemployment_expenses["id_parameter"]
    # Negate before extrapolation because extrapolate() clips negatives to zero,
    # then negate back to restore the original sign.
    unemployment_expenses = unemployment_expenses * -1
    unemployment_expenses = extrapolation.extrapolate(unemployment_expenses, years)
    unemployment_expenses = unemployment_expenses * -1

    beta = _beta_by_measure(final_energy_saving_or_capacities, data_source, id_region)

    investment_cost = investment.investment_cost_in_euro(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
    )
    del investment_cost["id_action_type"]

    subsidy_rate = _subsidy_rate_by_measure(
        final_energy_saving_or_capacities, data_source, id_region
    )

    # PB = (C/ES × PR) - (C/ES × UE × β) - (INV × SR / 100)
    revenue_term = final_energy_saving_or_capacities * public_revenues
    unemployment_term = final_energy_saving_or_capacities * unemployment_expenses

    del revenue_term["id_subsector"]
    del revenue_term["id_action_type"]
    del unemployment_term["id_subsector"]
    del unemployment_term["id_action_type"]

    unemployment_term = unemployment_term * beta
    subsidy_term = investment_cost * subsidy_rate / 100

    public_budget = revenue_term - unemployment_term - subsidy_term
    return public_budget


def _default_beta(data_source, id_region, years):
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": "84",
    }
    raw_beta = data_source.annual_series("wuppertal_parameters", where_clause)
    beta = extrapolation.extrapolate_series(raw_beta, years)
    return beta


def _beta_by_measure(final_energy_saving_or_capacities, data_source, id_region):
    years = final_energy_saving_or_capacities.years
    default_beta = _default_beta(data_source, id_region, years)

    def provide_default_beta(
        _id_measure, _id_subsector, _id_action_type, year, _saving
    ):
        value = default_beta[str(year)]
        return value

    id_parameter = 84
    beta = data_source.measure_specific_parameter(
        final_energy_saving_or_capacities,
        id_parameter,
        provide_default_beta,
    )
    del beta["id_subsector"]
    del beta["id_action_type"]
    return beta


def _default_subsidy_rate(data_source, id_region, years):
    where_clause = {
        "id_region": str(id_region),
        "id_parameter": "35",
    }
    raw_subsidy_rate = data_source.annual_series("wuppertal_parameters", where_clause)
    subsidy_rate = extrapolation.extrapolate_series(raw_subsidy_rate, years)
    return subsidy_rate


def _subsidy_rate_by_measure(final_energy_saving_or_capacities, data_source, id_region):
    years = final_energy_saving_or_capacities.years
    default_subsidy_rate = _default_subsidy_rate(data_source, id_region, years)

    def provide_default_subsidy_rate(
        _id_measure, _id_subsector, _id_action_type, year, _saving
    ):
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
