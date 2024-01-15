# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/31
from micat.calculation.economic import investment, population, primes


# pylint: disable=duplicate-code
def impact_on_gross_domestic_product(
    final_energy_saving_by_action_type,
    data_source,
    id_region,
):
    annual_investment_in_euro = investment.annual_investment_cost_in_euro(
        final_energy_saving_by_action_type,
        data_source,
    )

    action_type_ids = final_energy_saving_by_action_type.unique_index_values('id_action_type')

    e3m_parameters = data_source.table(
        'e3m_parameters',
        {
            'id_region': str(id_region),
            'id_action_type': action_type_ids,
        },
    )
    gdp_coefficient_in_euro_per_euro = e3m_parameters.reduce('id_parameter', 38)

    additional_gdp_in_euro = annual_investment_in_euro * gdp_coefficient_in_euro_per_euro
    del additional_gdp_in_euro['id_action_type']

    return additional_gdp_in_euro


def gross_domestic_product(
    data_source,
    id_region,
    years,
    population_of_municipality=None,
):
    primes_parameters_raw = primes.parameters(data_source, id_region, years)
    gross_domestic_product_raw = primes_parameters_raw.reduce('id_parameter', 10)

    scaled_gross_domestic_product = population.scale_by_population(
        gross_domestic_product_raw,
        population_of_municipality,
        data_source,
        id_region,
        years,
    )
    return scaled_gross_domestic_product


def gross_domestic_product_2015(
    data_source,
    id_region,
    population_of_municipality=None,
):
    primes_parameters = primes.parameters(data_source, id_region, [2015])
    raw_gross_domestic_product = primes_parameters.reduce('id_parameter', 10)
    gross_domestic_product_2015_raw = raw_gross_domestic_product['2015']

    scaled_gross_domestic_product_2015 = population.scale_by_population(
        gross_domestic_product_2015_raw,
        population_of_municipality,
        data_source,
        id_region,
        2015,
    )
    return scaled_gross_domestic_product_2015
