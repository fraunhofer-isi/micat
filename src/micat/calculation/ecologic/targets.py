# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/44
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/296


def impact_on_res_targets(
    gross_available_energy,
    total_primary_energy_saving,
):
    renewable_gae = gross_available_energy.reduce("id_primary_energy_carrier", [4, 5])
    renewable_gae_sum = renewable_gae.sum()

    total_gae_sum = gross_available_energy.sum()
    total_pes_sum = total_primary_energy_saving.aggregate_to(["id_measure"])

    sum_difference = total_gae_sum - total_pes_sum

    change_of_share = renewable_gae_sum / sum_difference - renewable_gae_sum / total_gae_sum
    return change_of_share.fillna(0)


def impact_on_res_targets_monetization(
    change_of_share,
    gross_available_energy,
    total_primary_energy_saving,
    cost_of_res_statistical_transfer,
):
    total_gae_sum = gross_available_energy.sum()

    total_pes_sum = total_primary_energy_saving.aggregate_to(["id_measure"])

    sum_difference = total_gae_sum - total_pes_sum

    cost_of_statistical_transfer = change_of_share * sum_difference * cost_of_res_statistical_transfer

    return cost_of_statistical_transfer
