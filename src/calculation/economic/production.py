# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np

from calculation import mode
from calculation.economic import eurostat, primes


def primary_production(
    data_source,
    id_mode,
    id_region,
    years,
):
    if mode.is_eurostat_mode(id_mode):
        eurostat_primary_parameters = eurostat.primary_parameters(data_source, id_region, years)
        extrapolated_primary_production = eurostat_primary_parameters.reduce('id_parameter', 1)
    else:
        primes_primary_parameters = primes.primary_parameters(data_source, id_region, years)
        extrapolated_primary_production = primes_primary_parameters.reduce('id_parameter', 1)

    return extrapolated_primary_production


def change_in_unit_costs_of_production(
    reduction_of_energy_cost,
    gross_domestic_product_primes,
    gross_domestic_product_primes_2015,
    data_source,
    id_region,
):
    change_in_energy_purchase = _change_in_energy_purchase(
        reduction_of_energy_cost,
    )
    # This is handled in the table.py file with validate_input_for_division()
    if change_in_energy_purchase.contains_inf():
        # Later we check for inf values to hande the special case of
        # zero output (=> division by zero).
        # This check is to ensure, that inf values only come from the division
        # and not from erroneous numerator data .
        raise ValueError('Change in energy purchase must not contain infinite values.')

    subsector_ids = change_in_energy_purchase.unique_index_values('id_subsector')

    output = _output(
        gross_domestic_product_primes,
        gross_domestic_product_primes_2015,
        data_source,
        id_region,
        subsector_ids,
    )
    change_in_unit_costs = -change_in_energy_purchase / output
    # Here we must find a way for when the numerator (input from the user) is also Zero, which returns NaN values.
    change_in_unit_costs = change_in_unit_costs.replace([np.inf, -np.inf], 0)

    del change_in_unit_costs['id_subsector']

    return change_in_unit_costs


def _change_in_energy_purchase(
    reduction_of_energy_cost,
):
    change_in_purchase = reduction_of_energy_cost.aggregate_to(['id_measure', 'id_subsector'])
    return change_in_purchase


def _output(
    gross_domestic_product,
    gross_domestic_product_2015,
    data_source,
    id_region,
    subsector_ids,
):
    output_2015 = _output_2015(data_source, id_region, subsector_ids)
    output = output_2015 * gross_domestic_product / gross_domestic_product_2015

    return output


def _output_2015(
    data_source,
    id_region,
    subsector_ids,
):
    where_clause = {
        'id_region': str(id_region),
        'id_subsector': subsector_ids,
    }
    eurostat_sector_parameters = data_source.table('eurostat_sector_parameters', where_clause)
    output_2015 = eurostat_sector_parameters.reduce('id_parameter', 50)
    return output_2015
