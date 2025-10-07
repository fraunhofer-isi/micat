# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation import extrapolation


def monetization_of_lost_working_days_due_to_air_pollution(
    reduction_of_lost_work_days,
    data_source,
    id_region,
):
    years = reduction_of_lost_work_days.years
    monetization_factors = _monetization_factors(data_source, id_region, years)
    monetization = reduction_of_lost_work_days * monetization_factors
    return monetization


def _monetization_factors(data_source, id_region, years):
    where_clause = {"id_region": str(id_region), "id_parameter": "19"}
    raw_monetization_factors = data_source.annual_series("iiasa_lost_working_days_monetization_factors", where_clause)
    monetization_factors = extrapolation.extrapolate_series(raw_monetization_factors, years)
    return monetization_factors
