# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.utils import list as list_utils


def test_string_to_integer():
    string_list = ['2020', '2030']
    result = list_utils.string_to_integer(string_list)
    assert result == [2020, 2030]


def test_intersection():
    left_list = [1, 2, 3]
    right_list = [2, 3, 4]
    result = list_utils.intersection(left_list, right_list)
    assert result == [2, 3]


def test_difference():
    left_list = [1, 2, 3]
    right_list = [2, 3, 4]
    result = list_utils.difference(left_list, right_list)
    assert result == [1]
