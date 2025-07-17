# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from micat.calculation.economic import import_dependency
from micat.table.table import Table

# pylint: disable=protected-access
# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/23
from micat.test_utils.isi_mock import patch

primary_production = Table([{"id_primary_energy_carrier": 1, "2020": 1, "2030": 1}])

gross_available_energy = Table([{"id_primary_energy_carrier": 1, "2020": 40, "2030": 40}])

primary_non_energy_use = Table([{"id_primary_energy_carrier": 1, "2020": 2, "2030": 20}])

primary_energy_saving_by_action_type = Table(
    [
        {"id_action_type": 1, "id_subsector": 1, "id_primary_energy_carrier": 1, "2020": 36, "2030": 2},
    ]
)

energy_carrier_share_by_action_type = Table(
    [
        {"id_action_type": 1, "2020": 0.1, "2030": 0.2},
        {"id_action_type": 2, "2020": 0.5, "2030": 1},
    ]
)

table_mock = Table([{"id_foo": 1, "2000": 1}])


@patch(
    import_dependency._filter_for_relevant_primary_energy_carriers,
    "mocked_filtered_table",
)
@patch(
    import_dependency._import_dependency,
    table_mock,
)
@patch(
    import_dependency._import_dependency_with_savings,
    table_mock,
)
def test_reduction_of_import_dependency():
    result = import_dependency.impact_on_import_dependency(
        "mocked_primary_energy_saving_by_action_type",
        "mocked_primary_production",
        "mocked_gross_available_energy",
        #'mocked_primary_non_energy_use',
    )
    assert result["2000"][1] == 0


def test_filter_for_relevant_primary_energy_carriers():
    df = Table(
        [
            {"id_primary_energy_carrier": 1, "2000": 2001},
            {"id_primary_energy_carrier": 2, "2000": 2002},
            {"id_primary_energy_carrier": 3, "2000": 2003},
            {"id_primary_energy_carrier": 4, "2000": 2004},
        ]
    )

    result = import_dependency._filter_for_relevant_primary_energy_carriers(df)
    values = result["2000"].to_list()  # pylint: disable=unsubscriptable-object, no-member
    assert values == [2001, 2002, 2003]


def test_import_dependency():
    result = import_dependency._import_dependency(
        primary_production,
        gross_available_energy,
        # primary_non_energy_use,
    )
    assert result["2020"][1] == pytest.approx(1 - 1 / (40 - 2), abs=0.05)
    assert result["2030"][1] == pytest.approx(1 - 1 / (40 - 2), abs=0.05)


mocked_primary_energy_saving = Table(
    [
        {"id_measure": 1, "id_primary_energy_carrier": 1, "2020": 36, "2030": 2},
    ]
)


@patch(
    Table.aggregate_to,
    mocked_primary_energy_saving,
)
def test_import_dependency_with_savings():
    result = import_dependency._import_dependency_with_savings(
        primary_production,
        gross_available_energy,
        # primary_non_energy_use,
        primary_energy_saving_by_action_type,
    )
    assert result["2020"][1, 1] == pytest.approx(1 - 1 / (40 - 36), abs=0.05)
