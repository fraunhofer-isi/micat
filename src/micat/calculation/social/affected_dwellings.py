# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np

from micat.calculation import extrapolation
from micat.table import table


def determine_number_of_affected_dwellings(final_energy_saving_by_action_type, data_source, id_region):
    number_of_affected_dwellings_user_input = _user_input_parameter(
        final_energy_saving_by_action_type,
        data_source,
        45,
    )

    annual_renovation_rate = _user_input_parameter(
        final_energy_saving_by_action_type,
        data_source,
        43,
    )

    national_dwelling_stock = data_source.annual_parameters_per_measure(
        final_energy_saving_by_action_type,
        '25_29_30_31_32_33_34_35_energy_poverty_coefficients',
        32,
        _provide_default_national_dwelling_stock,
        id_region,
    )

    number_of_affected_dwellings_per_ktoe = data_source.annual_parameters_per_measure(
        final_energy_saving_by_action_type,
        '41_48_investments_and_actions_per_ktoe',
        48,
        _provide_default_number_of_affected_dwellings_per_ktoe,
    )

    number_of_affected_dwellings = _number_of_affected_dwellings(
        final_energy_saving_by_action_type,
        number_of_affected_dwellings_user_input,
        annual_renovation_rate,
        national_dwelling_stock,
        number_of_affected_dwellings_per_ktoe,
    )

    return number_of_affected_dwellings


def _provide_default_number_of_affected_dwellings_per_ktoe(
    _id_region,
    id_parameter,
    _id_measure,
    _id_subsector,
    id_action_type,
    year,
    _saving,
    default_parameters_table,
):
    parameter_specific_table = default_parameters_table.reduce('id_parameter', id_parameter)
    parameters_by_action_type = parameter_specific_table.reduce('id_action_type', id_action_type)
    if parameters_by_action_type is None:
        return np.nan
    value = parameters_by_action_type[str(year)]
    return value


def _provide_default_national_dwelling_stock(
    id_region,
    id_parameter,
    _id_measure,
    _id_subsector,
    _id_action_type,
    year,
    _saving,
    default_parameters_table,
):
    parameter_specific_table = default_parameters_table.reduce('id_parameter', id_parameter)
    parameters_by_region = parameter_specific_table.reduce('id_region', id_region)
    if parameters_by_region is None:
        return np.nan
    value = parameters_by_region[str(year)]
    return value


def _user_input_parameter(final_energy_saving_by_action_type, data_source, id_parameter):
    measure_specific_parameter = data_source.measure_specific_parameter(
        final_energy_saving_by_action_type,
        id_parameter,
        _provide_default_parameter,
    )

    return measure_specific_parameter


def _number_of_affected_dwellings_per_ktoe(
    final_energy_saving_by_action_type,
    data_source,
):
    e3m_global_parameters = data_source.table('41_48_investments_and_actions_per_ktoe', {})
    years = final_energy_saving_by_action_type.years
    extrapolated_e3m_global_parameters = extrapolation.extrapolate(e3m_global_parameters, years)
    number_of_affected_dwellings_per_ktoe = extrapolated_e3m_global_parameters.reduce('id_parameter', 48)

    return number_of_affected_dwellings_per_ktoe


def _number_of_affected_dwellings(
    final_energy_saving_by_action_type,
    number_of_affected_dwellings_user_input,
    annual_renovation_rate,
    national_dwelling_stock,
    number_of_affected_dwellings_per_ktoe,
):
    final_energy_saving_by_action_type = final_energy_saving_by_action_type.to_data_frame()
    number_of_affected_dwellings_user_input = number_of_affected_dwellings_user_input.to_data_frame()
    annual_renovation_rate = annual_renovation_rate.to_data_frame()
    national_dwelling_stock = national_dwelling_stock.to_data_frame()
    number_of_affected_dwellings_per_ktoe = number_of_affected_dwellings_per_ktoe.to_data_frame()
    annual_renovation_rate_calculated = _calculate_annual_renovation_rate(
        final_energy_saving_by_action_type,
        annual_renovation_rate,
        number_of_affected_dwellings_per_ktoe,
        national_dwelling_stock,
    )
    number_of_affected_dwellings_calculated = _calculate_number_of_affected_dwellings(
        number_of_affected_dwellings_user_input,
        annual_renovation_rate_calculated,
    )
    number_of_affected_dwellings_calculated = table.Table(number_of_affected_dwellings_calculated)
    del number_of_affected_dwellings_calculated['id_subsector']
    del number_of_affected_dwellings_calculated['id_action_type']

    return number_of_affected_dwellings_calculated


def _calculate_number_of_affected_dwellings(
    number_of_affected_dwellings,
    annual_renovation_rate_calculated,
):
    number_of_affected_dwellings_calculated = number_of_affected_dwellings.copy()
    _fill_number_of_affected_dwellings_calculated_nan_values(
        number_of_affected_dwellings_calculated,
        annual_renovation_rate_calculated,
    )
    _fill_table_values_for_id_action_type_greater_than_four(
        number_of_affected_dwellings_calculated,
    )

    return number_of_affected_dwellings_calculated


def _fill_number_of_affected_dwellings_calculated_nan_values(
    number_of_affected_dwellings,
    annual_renovation_rate_calculated,
):
    located = number_of_affected_dwellings.isna()
    number_of_affected_dwellings[located] = annual_renovation_rate_calculated[located]


def _fill_table_values_for_id_action_type_greater_than_four(
    table_values,
):
    index_selected = table_values.index.get_level_values('id_action_type') > 4
    table_values.loc[index_selected] = 0


def _calculate_annual_renovation_rate(
    final_energy_saving_by_action_type,
    annual_renovation_rate,
    number_of_affected_dwellings_per_ktoe,
    national_dwelling_stock,
):
    annual_renovation_rate_calculated = annual_renovation_rate.copy()
    annual_renovation_rate_calculated = annual_renovation_rate_calculated / 100 * national_dwelling_stock
    _fill_annual_renovation_rate_nan_values_for_id_action_type_four(annual_renovation_rate_calculated)
    _fill_annual_renovation_rate_nan_values_for_id_action_type_less_than_four(
        final_energy_saving_by_action_type,
        annual_renovation_rate_calculated,
        number_of_affected_dwellings_per_ktoe,
    )
    _fill_table_values_for_id_action_type_greater_than_four(annual_renovation_rate_calculated)

    return annual_renovation_rate_calculated


def _fill_annual_renovation_rate_nan_values_for_id_action_type_four(
    annual_renovation_rate,
):
    index_selected = annual_renovation_rate.index.get_level_values('id_action_type') == 4
    filtered_data_frame = annual_renovation_rate.loc[index_selected]
    annual_renovation_rate[filtered_data_frame.isna()] = 0


def _fill_annual_renovation_rate_nan_values_for_id_action_type_less_than_four(
    final_energy_saving_by_action_type,
    annual_renovation_rate,
    number_of_affected_dwellings_per_ktoe,
):
    index_selected = annual_renovation_rate.index.get_level_values('id_action_type') < 4
    filtered_data_frame = annual_renovation_rate.loc[index_selected]
    calculated_annual_renovation_rate_data_frame = (
        final_energy_saving_by_action_type * number_of_affected_dwellings_per_ktoe
    )
    annual_renovation_rate[filtered_data_frame.isna()] = calculated_annual_renovation_rate_data_frame[
        filtered_data_frame.isna()
    ]


def _provide_default_parameter(
    _id_measure,
    _id_subsector,
    _id_action_type,
    _year,
    _saving,
):
    return np.nan


def _national_dwelling_stock(
    data_source,
    id_region,
    years,
):
    wuppertal_parameters = data_source.table('25_29_30_31_32_33_34_35_energy_poverty_coefficients', {'id_region': str(id_region)})
    extrapolated_wuppertal_parameters = extrapolation.extrapolate(wuppertal_parameters, years)
    national_dwelling_stock = extrapolated_wuppertal_parameters.reduce('id_parameter', 32)

    return national_dwelling_stock
