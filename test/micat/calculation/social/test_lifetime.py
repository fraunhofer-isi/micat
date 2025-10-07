# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.calculation.social import lifetime
from micat.table.table import Table

# pylint: disable=protected-access
from micat.test_utils.isi_mock import Mock, patch

mocked_lifetime = Table([{"id_measure": 1, "id_subsector": 2, "id_action_type": 3, "2000": 99}])


# pylint: disable=duplicate-code
@patch(lifetime._default_lifetime)
def test_measure_specific_lifetime():
    # noinspection PyUnusedLocal
    def mocked_measure_specific_parameter(
        _energy_saving,
        _id_parameter,
        provide_default,
        is_value_table=True,  # pylint: disable=unused-argument
    ):
        mocked_value = provide_default(1, 2, 3, "mocked_saving")
        assert mocked_value

        return mocked_lifetime

    mocked_table = Mock()
    mocked_table.reduce = Mock("mocked_reduce")

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)
    mocked_data_source.measure_specific_parameter = mocked_measure_specific_parameter

    mocked_final_energy_saving_or_capacities = Mock()
    mocked_final_energy_saving_or_capacities.years = ["2000"]

    result = lifetime.measure_specific_lifetime(
        mocked_final_energy_saving_or_capacities,
        mocked_data_source,
    )
    assert result["2000"][1] == 99


def test_default_lifetime():
    mocked_lifetime_table = Table([{"id_parameter": 36, "id_foo": 1, "2010": 10}])

    mocked_table = Mock()
    mocked_table.reduce = Mock(mocked_lifetime_table)

    mocked_data_source = Mock()
    mocked_data_source.table = Mock(mocked_table)

    mocked_subsector_ids = [1, 2, 3]
    mocked_action_type_ids = [4, 5, 6]
    result = lifetime._default_lifetime(
        mocked_data_source,
        mocked_subsector_ids,
        mocked_action_type_ids,
    )
    assert result["2010"][1] == 10
