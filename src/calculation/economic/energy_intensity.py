# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/36
from table.table import Table


def energy_intensity(
    gross_available_energy,
    gross_domestic_product_baseline,
    additional_gross_domestic_product,
    primary_non_energy_use,
    additional_primary_energy_saving,
):
    primary_energy_consumption_baseline = gross_available_energy - primary_non_energy_use
    sum_series_baseline = primary_energy_consumption_baseline.sum()
    energy_intensity_table_baseline = _intensity_table(
        sum_series_baseline,
        gross_domestic_product_baseline,
        'Baseline',
    )

    additional_gross_domestic_product = additional_gross_domestic_product.insert_index_column('id_parameter', 0, 10)
    additional_gross_domestic_product_all_measures = additional_gross_domestic_product.aggregate_to('id_parameter')

    gross_domestic_product = gross_domestic_product_baseline + additional_gross_domestic_product_all_measures

    additional_primary_energy_saving_all_measures = additional_primary_energy_saving.aggregate_to(
        ['id_primary_energy_carrier']
    )

    primary_energy_consumption = primary_energy_consumption_baseline - additional_primary_energy_saving_all_measures
    sum_series = primary_energy_consumption.sum()
    energy_intensity_table = _intensity_table(
        sum_series,
        gross_domestic_product,
        'Including saving',
    )

    result = Table.concat([energy_intensity_table_baseline, energy_intensity_table])
    return result


def _intensity_table(
    sum_series,
    gross_domestic_product,
    label,
):
    energy_intensity_series = sum_series / gross_domestic_product
    energy_intensity_table = energy_intensity_series.transpose('label', label)
    return energy_intensity_table