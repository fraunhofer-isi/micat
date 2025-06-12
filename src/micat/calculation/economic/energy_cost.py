# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/34
# pylint: disable = duplicate-code
from micat.calculation import extrapolation
from micat.table.table import Table


def reduction_of_energy_cost(
    energy_saving_by_final_energy_carrier_in_ktoe,
    data_source,
    id_region,
):
    e3m_energy_prices = _e3m_energy_prices(
        energy_saving_by_final_energy_carrier_in_ktoe,
        data_source,
    )

    energy_price_for_region = e3m_energy_prices.reduce("id_region", id_region)
    energy_price = energy_price_for_region.reduce("id_parameter", 13)

    years = energy_saving_by_final_energy_carrier_in_ktoe.years
    interpolated_energy_price_in_mio_euro_per_ktoe = extrapolation.extrapolate(energy_price, years)
    interpolated_energy_price_in_euro_per_ktoe = interpolated_energy_price_in_mio_euro_per_ktoe

    total_reduction_of_energy_costs_in_euro = _reduction_of_energy_costs_in_euro(
        energy_saving_by_final_energy_carrier_in_ktoe,
        interpolated_energy_price_in_euro_per_ktoe,
    )

    return total_reduction_of_energy_costs_in_euro


def _e3m_energy_prices(energy_saving_by_final_energy_carrier_in_ktoe, data_source):
    subsector_ids = energy_saving_by_final_energy_carrier_in_ktoe.unique_index_values("id_subsector")
    mapping_subsector_sector = data_source.mapping_table("mapping__subsector__sector", {"id_subsector": subsector_ids})
    e3m_energy_prices = data_source.table(
        "e3m_energy_prices",
        {
            "id_sector": [int(mapping_subsector_sector["id_sector"].iloc[0])],
        },
    )
    # Add the subsector as an index
    e3m_energy_prices._data_frame["id_subsector"] = subsector_ids[0]
    e3m_energy_prices._data_frame = e3m_energy_prices._data_frame.set_index("id_subsector", append=True)
    # Remove the id_sector index level
    e3m_energy_prices._data_frame = e3m_energy_prices._data_frame.reset_index(level="id_sector")
    e3m_energy_prices._data_frame = e3m_energy_prices._data_frame.drop(columns=["id_sector"])
    # Since all values are in M€, multiply by 1e6 to convert to Euro
    e3m_energy_prices._data_frame = e3m_energy_prices._data_frame * 1000000
    return e3m_energy_prices


def _reduction_of_energy_costs_in_euro(
    energy_saving_by_final_energy_carrier_in_ktoe,
    interpolated_energy_price_in_euro_per_ktoe,
):
    reduction_in_euro = energy_saving_by_final_energy_carrier_in_ktoe * interpolated_energy_price_in_euro_per_ktoe
    return reduction_in_euro


def _past_reduction_of_energy_costs(
    years,
    energy_saving_by_final_energy_carrier_in_ktoe,
    interpolated_energy_price_in_euro_per_ktoe,
):
    past_years = [str(year) for year in years if year <= 2021]
    reduction_in_euro = energy_saving_by_final_energy_carrier_in_ktoe * interpolated_energy_price_in_euro_per_ktoe
    if len(past_years) != 0:
        reduction_in_euro = reduction_in_euro.sort()[past_years]
    else:
        reduction_in_euro = None
    return reduction_in_euro


def _total_reduction_of_energy_costs_in_euro(
    reduction_of_energy_costs_in_euro,
    reduction_of_energy_costs_in_euro_outlook,
):
    if reduction_of_energy_costs_in_euro is None:
        total_reduction_of_energy_costs_in_euro = reduction_of_energy_costs_in_euro_outlook
    elif reduction_of_energy_costs_in_euro_outlook is None:
        total_reduction_of_energy_costs_in_euro = reduction_of_energy_costs_in_euro
    else:
        total_reduction_of_energy_costs_in_euro = Table.concat_years(
            [reduction_of_energy_costs_in_euro, reduction_of_energy_costs_in_euro_outlook]
        )
    return total_reduction_of_energy_costs_in_euro


def reduction_of_energy_cost_by_final_energy_carrier(
    reduction_of_energy_cost_by_action_type,
):
    reduction_by_final_energy_carrier = reduction_of_energy_cost_by_action_type.aggregate_to(
        ["id_measure", "id_final_energy_carrier"],
    )
    return reduction_by_final_energy_carrier
