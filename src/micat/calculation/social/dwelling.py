# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation
from micat.calculation.economic import population
from micat.input.data_source import DataSource
from micat.series.annual_series import AnnualSeries
from micat.table.table import Table


def number_of_affected_dwellings(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
    population_of_municipality,
):
    years = final_energy_saving_by_action_type.years
    improvement_actions_per_energy_unit = _improvement_actions_per_energy_unit(data_source, years)
    scaled_dwelling_stock = dwelling_stock(
        final_energy_saving_by_action_type,
        data_source,
        id_region,
        population_of_municipality,
    )

    def provide_default_number_of_affected_dwellings(
        id_measure,
        id_subsector,
        id_action_type,
        savings,
    ):
        return _provide_default_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            id_action_type,
            savings,
            improvement_actions_per_energy_unit,
        )

    # fmt: off
    number_of_affected_dwellings_for_measures = data_source.measure_specific_calculation(
        final_energy_saving_by_action_type,
        lambda id_measure, id_subsector, id_action_type, energy_saving, extrapolated_final_parameters,
               extrapolated_parameters, constants:
        _measure_specific_number_of_affected_dwellings(
            id_measure,
            id_subsector,
            id_action_type,
            energy_saving,
            extrapolated_parameters,
            improvement_actions_per_energy_unit,
            scaled_dwelling_stock,
        ),
        provide_default_number_of_affected_dwellings,
    )
    # fmt: on
    return number_of_affected_dwellings_for_measures


def dwelling_stock(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
    population_of_municipality,
):
    wuppertal_parameters = data_source.table('wuppertal_parameters', {'id_region': str(id_region)})

    dwelling_stock_raw = data_source.measure_specific_parameter_using_default_table(
        final_energy_saving_by_action_type,
        32,
        wuppertal_parameters,
    )

    years = final_energy_saving_by_action_type.years
    scaled_dwelling_stock = population.scale_by_population(
        dwelling_stock_raw,
        population_of_municipality,
        data_source,
        id_region,
        years,
    )
    return scaled_dwelling_stock


def _improvement_actions_per_energy_unit(data_source, years):
    e3m_global_parameters = data_source.table('e3m_global_parameters', {})
    raw_improvement_actions_per_energy_unit = e3m_global_parameters.reduce('id_parameter', 48)
    improvement_actions_per_energy_unit = extrapolation.extrapolate(raw_improvement_actions_per_energy_unit, years)
    return improvement_actions_per_energy_unit


def _measure_specific_number_of_affected_dwellings(
    id_measure,
    id_subsector,
    id_action_type,
    energy_saving,
    extrapolated_parameters,
    improvement_actions_per_energy_unit,
    scaled_dwelling_stock,
):
    years = extrapolated_parameters.years

    zero_row_table = DataSource.row_table(id_measure, years, 0)

    if id_subsector != 17:
        return zero_row_table

    scaled_dwelling_stock_for_measure = scaled_dwelling_stock.reduce('id_measure', id_measure)

    # id_subsector = 17 is mapped to the id_action_type values 1...6
    # and those id_action_type values are handled in different ways:

    if id_action_type in [5, 6]:
        return zero_row_table
    elif id_action_type in [1, 2, 3]:
        improvement_actions = improvement_actions_per_energy_unit.reduce('id_action_type', id_action_type)
        result = _measure_specific_number_of_affected_dwellings_others(
            energy_saving,
            extrapolated_parameters,
            improvement_actions,
            scaled_dwelling_stock_for_measure,
        )
        table = _result_to_table(
            result,
            id_measure,
            years,
        )
        return table
    elif id_action_type == 4:
        result = _measure_specific_number_of_affected_dwellings_electric(
            extrapolated_parameters,
            scaled_dwelling_stock_for_measure,
        )
        table = _result_to_table(
            result,
            id_measure,
            years,
        )
        return table
    else:
        message = 'Unknown id_action_type value' + str(id_action_type) + ' for subsector 17 (residential)'
        raise KeyError(message)


def _result_to_table(
    result,
    id_measure,
    years,
):
    if isinstance(result, Table):
        return result
    elif isinstance(result, AnnualSeries):
        series = result
        table = series.transpose('id_measure', id_measure)
    else:
        value = result
        table = DataSource.row_table(id_measure, years, value)
    return table


def _measure_specific_number_of_affected_dwellings_electric(
    extrapolated_parameters,
    scaled_dwelling_stock,
):
    number_of_affected_dwellings_from_user = extrapolated_parameters.reduce('id_parameter', 45)
    annual_renovation_rate_from_user = extrapolated_parameters.reduce('id_parameter', 43)

    if number_of_affected_dwellings_from_user is None:
        if annual_renovation_rate_from_user is None:
            return 0
        else:
            number_of_affected_dwellings_electric = annual_renovation_rate_from_user / 100 * scaled_dwelling_stock
            return number_of_affected_dwellings_electric
    else:
        return number_of_affected_dwellings_from_user


def _measure_specific_number_of_affected_dwellings_others(
    energy_saving,
    extrapolated_parameters,
    improvement_actions_per_energy_unit,
    scaled_dwelling_stock,
):
    number_of_affected_dwellings_from_user = extrapolated_parameters.reduce('id_parameter', 45)
    annual_renovation_rate_from_user = extrapolated_parameters.reduce('id_parameter', 43)

    if number_of_affected_dwellings_from_user is None:
        if annual_renovation_rate_from_user is None:
            number_of_affected_dwellings_other = energy_saving * improvement_actions_per_energy_unit
            return number_of_affected_dwellings_other
        else:
            return annual_renovation_rate_from_user / 100 * scaled_dwelling_stock
    else:
        return number_of_affected_dwellings_from_user


# pylint: disable=duplicate-code
def _provide_default_number_of_affected_dwellings(
    id_measure,
    id_subsector,
    id_action_type,
    energy_savings,
    improvement_actions_per_energy_unit,
):
    years = energy_savings.years
    zero_row_table = DataSource.row_table(id_measure, years, 0)
    if id_subsector != 17:
        return zero_row_table

    # id_subsector = 17 is mapped to the id_action_type values 1...6
    # and those id_action_type values are handled in different ways:

    if id_action_type in [5, 6]:
        return zero_row_table
    elif id_action_type in [1, 2, 3]:
        improvement_actions = improvement_actions_per_energy_unit.reduce('id_action_type', id_action_type)
        series = improvement_actions * energy_savings
        table = series.transpose('id_measure', id_measure)
        return table
    elif id_action_type == 4:
        return zero_row_table
    else:
        message = 'Unknown id_action_type value' + str(id_action_type) + ' for subsector 17 (residential)'
        raise KeyError(message)
