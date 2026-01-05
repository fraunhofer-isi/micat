# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pytest import raises

from micat.test_utils.isi_mock import MagicMock
from micat.utils.api import parse_request


class TestParseRequest:
    def test_parse_request_without_error(self):
        http_request_mock = MagicMock()
        http_request_mock.query_string = MagicMock()
        http_request_mock.query_string.decode = MagicMock(return_value='a=1&b=[10,20]')
        http_request_mock.content_type = 'application/json'
        http_request_mock.json = {}
        result = parse_request(http_request_mock)
        assert result['a'] == '1'
        assert result['b'] == '[10,20]'

    def test_parse_request_with_error(self):
        http_request_mock = MagicMock()
        http_request_mock.query_string = MagicMock()
        http_request_mock.query_string.decode = MagicMock(return_value='a=1&b=[10,20]')
        with raises(AttributeError) as exception_info:
            parse_request(http_request_mock)
            assert exception_info.value
