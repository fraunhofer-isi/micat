# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

class DatabaseException(Exception):
    def __init__(self, message='Database error'):
        self.message = message
        super().__init__(self.message)
