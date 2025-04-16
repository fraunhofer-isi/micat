# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/36
from micat.table.table import Table


# pylint: disable=too-many-locals
def energy_intensity(
    gross_available_energy,
    gross_domestic_product_baseline,
    additional_gross_domestic_product,
    #primary_non_energy_use,
    additional_primary_energy_saving,
):
    primary_energy_consumption_baseline = gross_available_energy #- primary_non_energy_use
    sum_series_baseline = primary_energy_consumption_baseline.sum()
    energy_intensity_table_baseline = _intensity_table(
        sum_series_baseline,
        gross_domestic_product_baseline,
        'Without savings',
    )

    additional_gross_domestic_product = additional_gross_domestic_product.insert_index_column('id_parameter', 0, 10)
    additional_gross_domestic_product_all_measures = additional_gross_domestic_product.aggregate_to('id_parameter')
    additional_gross_domestic_product_all_measures_in_bio = additional_gross_domestic_product_all_measures / 1000000000

    gross_domestic_product = gross_domestic_product_baseline + additional_gross_domestic_product_all_measures_in_bio

    additional_primary_energy_saving_all_measures = additional_primary_energy_saving.aggregate_to(
        ['id_primary_energy_carrier']
    )

    primary_energy_consumption = primary_energy_consumption_baseline - additional_primary_energy_saving_all_measures
    sum_series = primary_energy_consumption.sum()
    energy_intensity_table = _intensity_table(
        sum_series,
        gross_domestic_product,
        'With saving',
    )

    result = Table.concat([energy_intensity_table_baseline, energy_intensity_table])
    return result

def energy_intensity_difference(
    gross_available_energy,
    gross_domestic_product_baseline,
    additional_gross_domestic_product,
    #primary_non_energy_use,
    additional_primary_energy_saving,
):
    # Call the existing energy_intensity function
    energy_intensity_table = energy_intensity(
        gross_available_energy,
        gross_domestic_product_baseline,
        additional_gross_domestic_product,
        #primary_non_energy_use,
        additional_primary_energy_saving,
    )

    # Separate the "With saving" and "Without savings" rows
    with_savings = energy_intensity_table.query("label", "With saving")
    without_savings = energy_intensity_table.query("label", "Without savings")

    # Subtract "Without savings" from "With saving"
    difference = with_savings - without_savings

    return difference

def _intensity_table(
    sum_series,
    gross_domestic_product,
    label,
):
    energy_intensity_series = sum_series / gross_domestic_product
    energy_intensity_table = energy_intensity_series.transpose('label', label)
    return energy_intensity_table
