# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from micat.log.color_handler import ColorHandler
from micat.test_utils.isi_mock import Mock, fixture, patch


@fixture(name='stream')
def stream_fixture():
    stream = Mock()
    stream.write = Mock()
    return stream


@fixture(name='sut')
def sut_fixture(stream):
    return ColorHandler(stream)


@fixture(name='record')
def record_fixture():
    record = Mock()
    record.levelno = logging.DEBUG
    record.msg = 'mocked_message'
    return record


def test_construction(sut):
    colors = sut._msg_colors  # pylint: disable = protected-access
    assert colors[logging.DEBUG] == 32


class TestEmit:
    def test_without_error(self, record, stream, sut):
        stream.write.assert_not_called()
        sut.emit(record)
        expected_output = f'\x1b[{32};1m{record.msg}\x1b[0m\n'
        stream.write.assert_called_once_with(expected_output)

    def mocked_write(self, message):
        raise BrokenPipeError()

    def test_with_error(self, record, sut):
        sut.stream.write = self.mocked_write
        with patch(print) as patched_print:
            sut.emit(record)
            expected_output = f'\x1b[{32};1m{record.msg}\x1b[0m\n'
            patched_print.assert_called_with(expected_output)
