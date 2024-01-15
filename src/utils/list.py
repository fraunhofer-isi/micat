# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later


def string_to_integer(string_list):
    integer_list = list(map(int, string_list))
    return integer_list


def intersection(left_list, right_list):
    left_set = set(left_list)
    right_set = set(right_list)
    result = list(left_set & right_set)
    return result


def difference(left_list, right_list):
    left_set = set(left_list)
    right_set = set(right_list)
    result = list(left_set.difference(right_set))
    return result
