# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import micat.calculation.extrapolation
from micat.calculation.economic import supplier_diversity
from micat.table.table import Table

# pylint: disable = protected-access
from micat.test_utils.isi_mock import Mock, patch


@patch(supplier_diversity._average_monthly_imported_energy)
@patch(supplier_diversity._risk_coefficient)
@patch(supplier_diversity._supplier_diversity, 10)
@patch(supplier_diversity._average_monthly_imported_energy)
def test_change_in_supplier_diversity_by_energy_efficiency_impact():
    mocked_impact_largest = Table([{'id_final_energy_carrier': 3, '2000': 1}])

    mocked_impact_other = Table([{'id_final_energy_carrier': 3, '2000': 1}])

    with patch(supplier_diversity._impact_of_energy_efficiency_on_largest_supplier, Mock(mocked_impact_largest)):
        with patch(supplier_diversity._impact_of_energy_efficiency_on_other_suppliers, Mock(mocked_impact_other)):
            result = supplier_diversity.change_in_supplier_diversity_by_energy_efficiency_impact(
                Mock(),
                'mocked_data_source',
                'mocked_id_region',
            )
            assert result['2000'][3] == 8


@patch(micat.calculation.extrapolation.extrapolate, 'mocked_result')
def test_average_monthly_imported_energy():
    data_source = Mock()
    data_source.table = Mock()

    result = supplier_diversity._average_monthly_imported_energy(
        data_source,
        'mocked_id_region',
        'mocked_years',
    )
    assert result == 'mocked_result'


def test_impact_of_energy_efficiency_on_largest_supplier():
    energy_saving_by_final_energy_carrier = 2

    average_monthly_imported_energy = Mock()
    average_monthly_imported_energy.multi_index_lookup = Mock(4)
    total_amount_of_imported_energy = 3

    mocked_risk_coefficient_for_max_values = Table(
        [{'id_measure': 3, 'id_subsector': 1, 'id_action_type': 1, '2000': 1}]
    )

    risk_coefficient = Mock()
    risk_coefficient.multi_index_lookup = Mock(mocked_risk_coefficient_for_max_values)

    result = supplier_diversity._impact_of_energy_efficiency_on_largest_supplier(
        energy_saving_by_final_energy_carrier,
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )
    assert result['2000'][3] == 4


def test_impact_of_energy_efficiency_on_other_suppliers():
    energy_saving_by_final_energy_carrier = 2

    average_monthly_imported_energy = Mock()
    average_monthly_imported_energy.set_values_by_index_table = Mock(4)
    total_amount_of_imported_energy = 3

    risk_coefficient = Table(
        [{'id_measure': 3, 'id_subsector': 1, 'id_action_type': 1, 'id_final_energy_carrier': 1, '2000': 1}]
    )

    result = supplier_diversity._impact_of_energy_efficiency_on_other_suppliers(
        energy_saving_by_final_energy_carrier,
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )
    assert result['2000'][3][1] == 4 * 4


def test_risk_coefficient():
    mocked_table = Mock()
    mocked_table.reduce = Mock('mocked_result')

    data_source = Mock()
    data_source.table = Mock(mocked_table)

    result = supplier_diversity._risk_coefficient(data_source)

    assert result == 'mocked_result'


def test_supplier_diversity():
    average_monthly_imported_energy = Table(
        [
            {'id_final_energy_carrier': 1, 'id_foo': 1, '2000': 1},
            {'id_final_energy_carrier': 1, 'id_foo': 2, '2000': 2},
        ]
    )

    total_amount_of_imported_energy = 1
    risk_coefficient = 2

    result = supplier_diversity._supplier_diversity(
        average_monthly_imported_energy,
        total_amount_of_imported_energy,
        risk_coefficient,
    )

    assert result['2000'][1] == 2 * 2 + 4 * 4
