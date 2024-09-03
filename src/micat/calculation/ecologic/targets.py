# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/44
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/296

from micat.table.table import Table


def impact_on_res_targets(
        gross_available_energy,
        total_primary_energy_saving,
):
    renewable_gae = gross_available_energy.reduce('id_primary_energy_carrier', [4, 5])
    renewable_gae_sum = renewable_gae.sum()

    total_gae_sum = gross_available_energy.sum()
    total_pes_sum = total_primary_energy_saving.aggregate_to(['id_measure'])

    sum_difference = total_gae_sum - total_pes_sum

    targets_table_baseline = _targets_table(renewable_gae_sum, total_gae_sum, 'Without savings')
    targets_table_baseline['case'] = 'baseline'
    targets_table = _targets_table(renewable_gae_sum, sum_difference, 'With savings')
    targets_table['case'] = 'with_savings'

    result = Table.concat([targets_table_baseline, targets_table])
    return result


def impact_on_res_targets_monetization(
        targets_tables,
        gross_available_energy,
        total_primary_energy_saving,
        cost_of_res_statistical_transfer,
):
    change_of_share = targets_tables[targets_tables['case'] == 'with_savings'] - targets_tables[
        targets_tables['case'] == 'baseline']

    total_gae_sum = gross_available_energy.sum()

    total_pes_sum = total_primary_energy_saving.aggregate_to(['id_measure'])

    sum_difference = total_gae_sum - total_pes_sum

    cost_of_statistical_transfer = change_of_share * sum_difference * cost_of_res_statistical_transfer

    return cost_of_statistical_transfer


def _targets_table(
        ren_gae,
        tot_gae,
        label,
):
    targets_series = ren_gae / tot_gae
    targets_table = targets_series.transpose('label', label)
    return targets_table
