# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mock import patch as original_patch

from micat.description import descriptions
from micat.test_utils.isi_mock import mock_open, patch, patch_by_string
from micat.utils import api


class TestDescriptionByKey:
    @patch(descriptions.descriptions_as_json, {'foo': 'baa'})
    @patch(api.parse_request, {'key': 'foo'})
    def test_normal_usage(self):
        result = descriptions.description_by_key('mocked_request')
        assert result == 'baa'

    @patch(api.parse_request, {})
    def test_with_missing_key_argument(self):
        result = descriptions.description_by_key('mocked_request')
        assert result == "Error: You need to provide a 'key' argument in the request: description?key=foo."

    @patch(descriptions.descriptions_as_json, {'foo': 'baa'})
    @patch(api.parse_request, {'key': 'qux'})
    def test_with_missing_description_entry(self):
        result = descriptions.description_by_key('mocked_request')
        assert result == "Error: Description key 'qux' not found"


@patch_by_string('yaml.safe_load', 'mocked_result')
def test_description_as_json():
    with original_patch("builtins.open", mock_open(read_data="data")):
        result = descriptions.descriptions_as_json()
        assert result == 'mocked_result'
