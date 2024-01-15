# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from input.database_exception import DatabaseException


def test_construction():
    result = DatabaseException('mocked_message')
    assert result.message == 'mocked_message'
