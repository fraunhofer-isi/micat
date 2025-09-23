# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/42
from micat.calculation.ecologic import fuel_split


def energy_saving(primary_energy_saving_by_action_type):
    aggregated_saving = _aggregate_primary_energy_saving(primary_energy_saving_by_action_type)
    return aggregated_saving


# pylint: disable=duplicate-code
def energy_saving_by_final_energy_carrier(
    final_energy_saving_or_capacities,
    data_source,
    id_region,
    subsector_ids,
):
    fuel_split_by_action_type = fuel_split.fuel_split_by_action_type(
        final_energy_saving_or_capacities,
        data_source,
        id_region,
        subsector_ids,
    )
    saving_by_final_energy_carrier = _final_energy_saving_or_capacities_and_energy_carrier(
        fuel_split_by_action_type,
        final_energy_saving_or_capacities,
    )
    return saving_by_final_energy_carrier


def _final_energy_saving_or_capacities_and_energy_carrier(
    fuel_split_by_action_type,
    final_energy_saving_or_capacities,
):
    final_energy_saving_by_energy_carrier = final_energy_saving_or_capacities * fuel_split_by_action_type
    return final_energy_saving_by_energy_carrier


def _aggregate_primary_energy_saving(primary_energy_saving_by_action_type):
    aggregated_saving = primary_energy_saving_by_action_type.aggregate_to(["id_measure", "id_primary_energy_carrier"])
    return aggregated_saving
