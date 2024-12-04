# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def parameters(data_source, id_region, years):
    regional_parameter_data = _parameters_raw(data_source, id_region)
    extrapolated_parameter_data = extrapolation.extrapolate(regional_parameter_data, years)
    return extrapolated_parameter_data


def primary_parameters(data_source, id_region, years):
    regional_parameter_data = _primary_parameters_raw(data_source, id_region)
    extrapolated_parameter_data = extrapolation.extrapolate(regional_parameter_data, years)
    return extrapolated_parameter_data


def technology_parameters(data_source, id_region, years):
    regional_parameter_data = _technology_parameters_raw(data_source, id_region)
    extrapolated_parameter_data = extrapolation.extrapolate(regional_parameter_data, years)
    return extrapolated_parameter_data


def _parameters_raw(data_source, id_region):
    where_clause = {
        'id_region': str(id_region),
    }
    table = data_source.table('10_24_GDP_population_primes', where_clause)
    return table


def _primary_parameters_raw(data_source, id_region):
    where_clause = {
        'id_region': str(id_region),
    }
    table = data_source.table('1_2_GAE_PP_primes', where_clause)
    return table


def _technology_parameters_raw(data_source, id_region):
    where_clause = {
        'id_region': str(id_region),
    }
    table = data_source.table('47_RES_utilisation_primes', where_clause)
    return table
