# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=protected-access
import inspect
import logging
import time

import pytest

from micat.log import color_handler, logger
from micat.test_utils.isi_mock import Mock, patch


@pytest.fixture(name="sut")
def fixture_sut():
    return logger.Logger(is_active=True)


class TestConstruction:
    def test_protected_attributes(self, sut):
        assert sut._is_active is True
        assert sut._start_time == 0


def mocked_inspection_frame():
    frame_mock = Mock()
    frame_mock.f_back = Mock()
    frame_mock.f_back.f_code = 'mocked_function'
    return frame_mock


@patch(
    inspect.currentframe,
    Mock(mocked_inspection_frame()),
)
def test_info():
    with patch(logger.Logger.log_info) as mocked_log_info:
        mocked_log_info.assert_not_called()
        logger.Logger.info('mocked_message')
        mocked_log_info.assert_called_once_with('mocked_message', 'mocked_function')


@patch(
    inspect.currentframe,
    Mock(mocked_inspection_frame()),
)
def test_warn():
    with patch(logger.Logger.log_warn) as mocked_log_info:
        mocked_log_info.assert_not_called()
        logger.Logger.warn('mocked_message')
        mocked_log_info.assert_called_once_with('mocked_message', 'mocked_function')


@patch(
    inspect.currentframe,
    Mock(mocked_inspection_frame()),
)
def test_error():
    with patch(logger.Logger.log_error) as mocked_log_info:
        mocked_log_info.assert_not_called()
        logger.Logger.error('mocked_message')
        mocked_log_info.assert_called_once_with('mocked_message', 'mocked_function')


@patch(time.time, 5.123456)
def test_current_time_in_ms():
    assert logger.Logger._current_time_in_ms() == 5123


def mocked_color_handler(self):
    self._name = 'mocked_color_handler'
    self.setLevel = Mock()
    self.setFormatter = Mock()


@patch(logging.getLogger)
@patch(logging.Formatter)
@patch(color_handler.ColorHandler.__init__, mocked_color_handler)
def test_create_logger():
    log = logger.Logger._create_logger()
    assert log.propagate == 0


class TestLogInfo:
    def test_active(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut.log_info('foo')
        logger.Logger.wrapped_logger.info.assert_called_once()

    def test_inactive(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut._is_active = False
        sut.log_info('foo')
        logger.Logger.wrapped_logger.info.assert_not_called()


class TestLogWarn:
    def test_active(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut.log_warn('baa')
        logger.Logger.wrapped_logger.warning.assert_called_once()

    def test_inactive(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut._is_active = False
        sut.log_warn('baa')
        logger.Logger.wrapped_logger.warning.assert_not_called()


class TestLogError:
    def test_active(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut.log_error('qux')
        logger.Logger.wrapped_logger.error.assert_called_once()

    def test_inactive(self, sut):
        logger.Logger.wrapped_logger = Mock()
        sut._is_active = False
        sut.log_error('qux')
        logger.Logger.wrapped_logger.error.assert_not_called()


class TestStartTimer:
    def test_active(self, sut):
        sut._current_time_in_ms = Mock(66)
        sut.start_timer()
        assert sut._start_time == 66

    def test_inactive(self, sut):
        sut._is_active = False
        sut.start_timer()
        assert sut._start_time == 0


class TestInfoElapsedTime:
    @patch(logger.Logger.log_info)
    def test_active(self, sut):
        sut._start_time = 10
        sut._current_time_in_ms = Mock(30)
        sut.info_elapsed_time('foo')

        logger.Logger.log_info.assert_called_once()  # pylint: disable=no-member

    @patch(logger.Logger.log_info)
    def test_inactive(self, sut):
        sut._is_active = False
        sut.info_elapsed_time('foo')
        logger.Logger.log_info.assert_not_called()  # pylint: disable=no-member
