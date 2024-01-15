# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd

from micat.table.abstract_table import AbstractTable
from micat.table.mapping_table import MappingTable
from micat.test_utils.isi_mock import Mock, fixture, patch, patch_property, raises


def mocked_data_frame():
    data_frame = Mock()
    data_frame.set_index = Mock()
    data_frame.columns = ['mocked_source_column', 'mocked_target_column']
    data_frame.empty = False
    return data_frame


@fixture(name='sut')
def sut_fixture():
    with patch(
        MappingTable._validate_and_filter,
        lambda self, df, name: df,
    ):
        return MappingTable(mocked_data_frame())


# noinspection PyUnusedLocal
def mocked_mapping_table__init__(self, data_frame, name=None):  # pylint: disable=unused-argument
    self._data_frame = 'mocked_frame'


class TestPublicApi:
    @patch(
        AbstractTable._data_frame_from_json,
        mocked_data_frame(),
    )
    @patch(
        MappingTable.__init__,
        mocked_mapping_table__init__,
    )
    def test_from_json(self):
        mapping_table = MappingTable.from_json('mocked_custom_json')
        data_frame = mapping_table._data_frame
        assert data_frame == 'mocked_frame'

    @patch(AbstractTable._apply_mapping_table, 'mocked_result')
    class TestApplyFor:
        @patch(AbstractTable._other_value, 'mocked_frame')
        @patch(AbstractTable._has_multi_index, False)
        def test_without_multi_index(self, sut):
            result = sut.apply_for('mocked_data_frame')
            assert result == 'mocked_result'

        mocked_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 2, '2000': 1}])
        mocked_frame.set_index(['id_foo', 'id_baa'], inplace=True)

        @patch(AbstractTable._other_value, mocked_frame)
        @patch(AbstractTable._has_multi_index, True)
        def test_with_multi_index(self, sut):
            result = sut.apply_for('mocked_data_frame')
            assert result == 'mocked_result'

    @patch(AbstractTable._apply_mapping_table_reversely, 'mocked_result')
    class TestApplyReverselyFor:
        @patch(AbstractTable._other_value, 'mocked_frame')
        @patch(AbstractTable._has_multi_index, False)
        def test_without_multi_index(self, sut):
            result = sut.apply_reversely_for('mocked_data_frame')
            assert result == 'mocked_result'

        mocked_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 2, '2000': 1}])
        mocked_frame.set_index(['id_foo', 'id_baa'], inplace=True)

        @patch(AbstractTable._other_value, mocked_frame)
        @patch(AbstractTable._has_multi_index, True)
        def test_with_multi_index(self, sut):
            result = sut.apply_reversely_for('mocked_data_frame')
            assert result == 'mocked_result'

    class TestSingleTargetId:
        @patch(MappingTable.target_ids, [])
        def test_without_id(self, sut):
            with raises(ValueError):
                sut.single_target_id('mocked_source_value')

        @patch(MappingTable.target_ids, [11])
        def test_with_single_id(self, sut):
            result = sut.single_target_id('mocked_source_value')
            assert result == 11

        @patch(MappingTable.target_ids, [1, 2])
        def test_with_multiple_ids(self, sut):
            with raises(ValueError):
                sut.single_target_id('mocked_source_value')

    @patch(MappingTable._target_query, 'query')
    def test_target_ids(self, sut):
        with patch_property(MappingTable.target_column, 'mocked_target_column'):
            result = sut.target_ids('mocked_source_value')
            assert result == []

    def test_source_column(self, sut):
        assert sut.source_column == 'mocked_source_column'

    def test_source_values(self):
        data_frame = pd.DataFrame(
            [
                {'id': 1, 'id_source': 1, 'id_target': 10},
                {'id': 2, 'id_source': 2, 'id_target': 20},
            ]
        )
        data_frame.set_index(['id'], inplace=True)
        sut = MappingTable(data_frame)

        with patch_property(MappingTable.source_column, 'id_source'):
            source_values = sut.source_values
            assert source_values == [1, 2]

    def test_target_column(self, sut):
        assert sut.target_column == 'mocked_target_column'

    def test_target_values(self):
        data_frame = pd.DataFrame(
            [
                {'id': 1, 'id_source': 1, 'id_target': 10},
                {'id': 2, 'id_source': 2, 'id_target': 20},
            ]
        )
        data_frame.set_index(['id'], inplace=True)
        sut = MappingTable(data_frame)

        with patch_property(MappingTable.target_column, 'id_target'):
            target_values = sut.target_values
            assert target_values == [10, 20]


class TestPrivateApi:
    @patch(MappingTable.__init__, mocked_mapping_table__init__)
    def test_create(self):
        id_table = MappingTable._create('mocked_data_frame_or_array')
        data_frame = id_table._data_frame
        assert data_frame == 'mocked_frame'

    @patch(
        AbstractTable._check_for_dummy_values_and_remove_them,
        'mocked_result',
    )
    def test_check_for_special_values_and_remove_them(self):
        result = MappingTable._check_for_special_values_and_remove_them(
            'mocked_data_frame',
            'mocked_name',
        )
        assert result == 'mocked_result'

    @patch(MappingTable._validate_index)
    @patch(
        MappingTable._check_for_special_values_and_remove_them,
        'mocked_result',
    )
    @patch(MappingTable._validate_entries)
    def test_validate_and_filter(self):
        result = MappingTable._validate_and_filter(
            'mocked_data_frame',
            'mocked_name',
        )
        assert result == 'mocked_result'

    class TestValidateEntries:
        @patch(AbstractTable._contains_nan, True)
        def test_with_nan(self):
            with raises(ValueError):
                MappingTable._validate_entries('mocked_data_frame')

        @patch(AbstractTable._contains_nan, False)
        def test_without_nan(self):
            MappingTable._validate_entries('mocked_data_frame')

    class TestValidateIndex:
        def test_with_id_index(self):
            data_frame = pd.DataFrame([{'id': 1, 'foo': 2}])
            data_frame.set_index(['id'], inplace=True)
            MappingTable._validate_entries(data_frame)

        def test_without_id_index(self):
            data_frame = pd.DataFrame([{'foo': 1}])
            with raises(ValueError):
                MappingTable._validate_index(data_frame)

    class TestTargetQuery:
        def test_with_string(self, sut):
            sut._data_frame = pd.DataFrame([{'source': 'foo', 'target': 12}])
            result = sut._target_query('foo')
            assert result == 'source=="foo"'

        def test_with_int_query(self, sut):
            sut._data_frame = pd.DataFrame([{'source': 'foo', 'target': 12}])
            result = sut._target_query(33)
            assert result == 'source==33'
