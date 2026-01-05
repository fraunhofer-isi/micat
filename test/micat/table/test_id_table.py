# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd

from micat.table.abstract_table import AbstractTable
from micat.table.id_table import IdTable
from micat.test_utils.isi_mock import Mock, fixture, patch, raises


# pylint: disable=duplicate-code
def mocked_data_frame():
    data_frame = Mock()
    data_frame.set_index = Mock()
    data_frame.columns = ['mocked_column']
    data_frame.empty = False
    return data_frame


# noinspection PyUnusedLocal
def mocked_id_table__init__(self, data_frame, name=None):  # pylint: disable=unused-argument
    self._data_frame = 'mocked_frame'


@fixture(name='sut')
def fixture_sut():
    # noinspection PyProtectedMember
    with patch(AbstractTable._construct_data_frame, Mock(mocked_data_frame())):
        return IdTable('mocked_data_frame', 'mocked_name')


class TestPublicApi:
    @patch(AbstractTable._construct_data_frame, Mock(mocked_data_frame()))
    def test_construction(self):
        id_table = IdTable(mocked_data_frame())
        data_frame = id_table._data_frame
        assert data_frame.columns == ['mocked_column']

    @patch(AbstractTable._data_frame_from_json, Mock(mocked_data_frame()))
    @patch(IdTable.__init__, mocked_id_table__init__)
    def test_from_json(self):
        id_table = IdTable.from_json('mocked_custom_json')
        data_frame = id_table._data_frame
        assert data_frame == 'mocked_frame'

    def test_get(self, sut):
        data_frame = pd.DataFrame(
            [
                {'id': 3, 'label': 'mocked_label', 'description': 'mocked_description'},
            ]
        )
        data_frame.set_index(['id'], inplace=True)
        sut._data_frame = data_frame
        result = sut.get(3)
        assert result['label'] == 'mocked_label'
        assert result['description'] == 'mocked_description'

    class TestIdByDescription:
        def test_with_exiting_entry(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id': 3, 'label': 'mocked_label', 'description': 'mocked_description'},
                ]
            )
            data_frame.set_index(['id'], inplace=True)
            sut._data_frame = data_frame

            result = sut.id_by_description('mocked_description')
            assert result == 3

        def test_without_entry(self, sut):
            data_frame = pd.DataFrame(
                [
                    {'id': 3, 'label': 'mocked_label', 'description': 'mocked_description'},
                ]
            )
            data_frame.set_index(['id'], inplace=True)
            data_frame.name = 'id_foo'
            sut._data_frame = data_frame

            with raises(KeyError):
                sut.id_by_description('non_existing_description')

    class TestLabel:
        def test_with_existing_entry(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'label': 'foo', 'description': 'foo_description'},
                    {'id': 2, 'label': 'baa', 'description': 'baa_description'},
                    {'id': 3, 'label': 'qux', 'description': 'qux_description'},
                ]
            )

            result = sut.label(2)
            assert result == 'baa'

        def test_without_entry(self, sut):
            sut._data_frame = pd.DataFrame(
                [
                    {'id': 1, 'label': 'foo', 'description': 'foo_description'},
                    {'id': 2, 'label': 'baa', 'description': 'baa_description'},
                    {'id': 3, 'label': 'qux', 'description': 'qux_description'},
                ]
            )
            sut._data_frame.name = 'id_foo'

            with raises(KeyError):
                sut.label(4)

    @patch(IdTable._check_if_all_labels_can_be_replaced)
    def test_label_to_id(self, sut):
        data_frame = pd.DataFrame(
            [
                {'foo': 'mocked_label', 'value': 1},
            ]
        )

        id_data_frame = pd.DataFrame(
            [
                {'id': 3, 'label': 'mocked_label', 'description': 'mocked_description'},
            ]
        )
        id_data_frame.set_index(['id'], inplace=True)
        id_data_frame.name = 'id_foo'
        sut._data_frame = id_data_frame

        result = sut.label_to_id(data_frame, 'foo')
        assert result['id_foo'][0] == 3

    def test_labels(self, sut):
        sut._data_frame = pd.DataFrame(
            [
                {'id': 1, 'label': 'foo', 'description': 'foo_description'},
                {'id': 2, 'label': 'baa', 'description': 'baa_description'},
                {'id': 3, 'label': 'qux', 'description': 'qux_description'},
            ]
        )

        result = sut.labels([1, 3])
        assert result == ['foo', 'qux']

    def test_id_values(self, sut):
        data_frame = pd.DataFrame(
            [
                {'id': 3, 'label': 'mocked_label', 'description': 'mocked_description'},
            ]
        )
        data_frame.set_index(['id'], inplace=True)
        sut._data_frame = data_frame

        result = sut.id_values
        assert result == [3]


class TestPrivateApi:
    @patch(IdTable.__init__, mocked_id_table__init__)
    def test_create(self):
        id_table = IdTable._create('mocked_data_frame_or_array')
        data_frame = id_table._data_frame
        assert data_frame == 'mocked_frame'

    class TestCheckIfAllLabelsCanBeReplaced:
        def test_with_existing_labels(self):
            data_frame = pd.DataFrame(
                [
                    {'foo': 'mocked_label'},
                ]
            )
            column_name = 'foo'

            mapping = pd.DataFrame(
                [
                    {'id': 1, 'foo': 'mocked_label', 'target': 3},
                ]
            )
            mapping.set_index(['id'], inplace=True)

            IdTable._check_if_all_labels_can_be_replaced(
                data_frame,
                column_name,
                mapping,
            )

        def test_without_existing_labels(self):
            data_frame = pd.DataFrame(
                [
                    {'foo': 'mocked_label'},
                ]
            )
            column_name = 'foo'

            mapping = pd.DataFrame(
                [
                    {'id': 1, 'foo': 'mocked_other_label', 'target': 3},
                ]
            )
            mapping.set_index(['id'], inplace=True)

            with raises(KeyError):
                IdTable._check_if_all_labels_can_be_replaced(
                    data_frame,
                    column_name,
                    mapping,
                )

    def test_name(self, sut):
        data_frame = Mock()
        data_frame.name = 'mocked_name'
        sut._data_frame = data_frame

        result = sut._name
        assert result == 'mocked_name'
