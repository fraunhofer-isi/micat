# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def change_in_supplier_diversity_by_energy_efficiency_impact(
    energy_saving_by_final_energy_carrier,
    data_source,
    id_region,
):
    years = energy_saving_by_final_energy_carrier.years
    average_monthly_imported_energy = _average_monthly_imported_energy(data_source, id_region, years)
    total_amount_of_imported_energy = average_monthly_imported_energy.aggregate_to('id_final_energy_carrier')
    risk_coefficient = _risk_coefficient(data_source)

    supplier_diversity = _supplier_diversity(
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )

    impact_of_energy_efficiency_on_largest_supplier = _impact_of_energy_efficiency_on_largest_supplier(
        energy_saving_by_final_energy_carrier,
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )

    impact_of_energy_efficiency_on_other_suppliers = _impact_of_energy_efficiency_on_other_suppliers(
        energy_saving_by_final_energy_carrier,
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )

    change = supplier_diversity - (
        impact_of_energy_efficiency_on_largest_supplier + impact_of_energy_efficiency_on_other_suppliers
    )

    considered_final_energy_carrier_ids = [
        2,  # oil
        3,  # coal
        4,  # gas
    ]
    query = 'id_final_energy_carrier in ' + str(considered_final_energy_carrier_ids)
    filtered_change = change.query(query)

    return filtered_change


def _average_monthly_imported_energy(data_source, id_region, years):
    where_clause = {
        'id_region': str(id_region),
    }
    eurostat_partner_relation_parameters = data_source.table('eurostat_partner_relation_parameters', where_clause)
    raw_average_monthly_imported_energy = eurostat_partner_relation_parameters.reduce('id_parameter', 51)
    average_monthly_imported_energy = extrapolation.extrapolate(raw_average_monthly_imported_energy, years)
    return average_monthly_imported_energy


def _impact_of_energy_efficiency_on_largest_supplier(
    energy_saving_by_final_energy_carrier,
    average_monthly_imported_energy,
    total_amount_of_imported_energy,
    risk_coefficient,
):
    indices_for_max_values = average_monthly_imported_energy.indices_for_max_annual_values(['id_final_energy_carrier'])
    index_order = ['id_partner_region', 'id_final_energy_carrier']
    max_imported_energy = average_monthly_imported_energy.multi_index_lookup(indices_for_max_values, index_order)
    risk_coefficient_for_max_values = risk_coefficient.multi_index_lookup(indices_for_max_values, index_order)

    numerator = max_imported_energy - energy_saving_by_final_energy_carrier
    denominator = total_amount_of_imported_energy - energy_saving_by_final_energy_carrier
    fraction = numerator / denominator
    product = fraction * risk_coefficient_for_max_values

    impact_on_largest_supplier = product * product
    del impact_on_largest_supplier['id_subsector']
    del impact_on_largest_supplier['id_action_type']

    return impact_on_largest_supplier


def _impact_of_energy_efficiency_on_other_suppliers(
    energy_saving_by_final_energy_carrier,
    average_monthly_imported_energy,
    total_amount_of_imported_energy,
    risk_coefficient,
):
    indices_for_max_values = average_monthly_imported_energy.indices_for_max_annual_values(['id_final_energy_carrier'])
    index_order = ['id_partner_region', 'id_final_energy_carrier']

    # we set the entries for the max values to zero, so that they will not contribute to the sum:
    adapted_imported_energy = average_monthly_imported_energy.set_values_by_index_table(
        indices_for_max_values,
        index_order,
        0,
    )

    numerator = adapted_imported_energy * risk_coefficient
    denominator = total_amount_of_imported_energy - energy_saving_by_final_energy_carrier
    fraction = numerator / denominator

    impact_on_suppliers = fraction * fraction
    impact_on_other_suppliers = impact_on_suppliers.aggregate_to(['id_measure', 'id_final_energy_carrier'])

    return impact_on_other_suppliers


def _risk_coefficient(data_source):
    eurostat_partner_parameters = data_source.table('eurostat_partner_parameters', {})
    risk_coefficient = eurostat_partner_parameters.reduce('id_parameter', 52)
    return risk_coefficient


def _supplier_diversity(
    average_monthly_imported_energy,
    total_amount_of_imported_energy,
    risk_coefficient,
):
    product = average_monthly_imported_energy * risk_coefficient / total_amount_of_imported_energy

    squared_product = product * product
    supplier_diversity = squared_product.aggregate_to('id_final_energy_carrier')

    return supplier_diversity
