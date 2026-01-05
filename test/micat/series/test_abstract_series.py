# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import pandas as pd

from micat.series.abstract_series import AbstractSeries
from micat.test_utils.isi_mock import patch, raises


class TestConstruction:
    def test_with_series(self):
        series = pd.Series({'2000': 1, '2020': 2})
        result = AbstractSeries(series)
        assert (result._series == series).all()

    def test_with_dictionary(self):
        result = AbstractSeries({'2000': 1, '2020': 2})
        assert result._series['2000'] == 1
        assert result._series['2020'] == 2

    @patch(
        AbstractSeries._create_series_from_data_frame,
        'mocked_series',
    )
    def test_with_data_frame(self):
        single_row_data_frame = pd.DataFrame([{'id_foo': 1, '2010': 10, '2020': 20}])
        single_row_data_frame.set_index(['id_foo'], inplace=True)

        result = AbstractSeries(single_row_data_frame)
        assert result._series == 'mocked_series'


class TestCreateSeriesFromDataFrame:
    def test_empty_data_frame(self):
        empty_data_frame = pd.DataFrame()
        with raises(ValueError):
            AbstractSeries._create_series_from_data_frame(empty_data_frame)

    def test_single_row_data_frame(self):
        single_row_data_frame = pd.DataFrame([{'id_foo': 1, 'id_baa': 1, '2010': 10, '2020': 20}])
        single_row_data_frame.set_index(['id_foo', 'id_baa'], inplace=True)
        result = AbstractSeries._create_series_from_data_frame(single_row_data_frame)
        assert len(result) == 2
        assert result['2010'] == 10
        assert result['2020'] == 20

    @patch(
        AbstractSeries._create_series_from_single_column_data_frame,
        'mocked_series',
    )
    def test_single_column_data_frame(self):
        single_column_data_frame = pd.DataFrame(
            [
                {'id_year': 2010, 'value': 10},
                {'id_year': 2020, 'value': 20},
            ]
        )
        single_column_data_frame.set_index(['id_year'], inplace=True)
        result = AbstractSeries._create_series_from_data_frame(single_column_data_frame)
        assert result == 'mocked_series'

    @patch(
        AbstractSeries._create_series_from_single_column_data_frame,
        'mocked_series',
    )
    def test_multi_column_data_frame(self):
        single_column_data_frame = pd.DataFrame(
            [
                {'id_year': 2010, '2000': 10, '2020': 20},
                {'id_year': 2020, '2000': 20, '2020': 20},
            ]
        )
        single_column_data_frame.set_index(['id_year'], inplace=True)
        with raises(ValueError):
            AbstractSeries._create_series_from_data_frame(single_column_data_frame)


class TestCreateSeriesFromSingleColumnDataFrame:
    def test_multi_index(self):
        single_column_data_frame = pd.DataFrame(
            [
                {'id_foo': 1, 'id_baa': 1, 'value': 10},
                {'id_foo': 1, 'id_baa': 2, 'value': 20},
            ]
        )
        single_column_data_frame.set_index(['id_foo', 'id_baa'], inplace=True)

        with raises(KeyError):
            AbstractSeries._create_series_from_single_column_data_frame(single_column_data_frame)

    def test_single_annual_index(self):
        single_column_data_frame = pd.DataFrame(
            [
                {'id_year': 2010, 'value': 10},
                {'id_year': 2020, 'value': 20},
            ]
        )
        single_column_data_frame.set_index(['id_year'], inplace=True)

        result = AbstractSeries._create_series_from_single_column_data_frame(single_column_data_frame)
        assert len(result) == 2
        assert result['2010'] == 10
        assert result['2020'] == 20


def test_items():
    sut = AbstractSeries({'2000': 1, '2020': 2})
    items_list = list(sut.items())
    assert len(items_list) == 2
    assert items_list[0] == ('2000', 1)
    assert items_list[1] == ('2020', 2)


def test_a_preview():
    sut = AbstractSeries({'2000': 1, '2020': 2})
    assert isinstance(sut.a_preview, pd.Series)
