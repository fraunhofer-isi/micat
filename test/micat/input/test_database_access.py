# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sqlite3
from os.path import exists


def database_path():
    current_directory = os.getcwd()
    if current_directory.endswith('test'):
        return '../src/micat/data/public.sqlite'
    else:
        return 'src/micat/data/public.sqlite'


def test_database_exists():
    assert exists(database_path())


def test_database_access():
    # Ensures that sqlite database is accessible / there are no
    # issues with sqlite driver, missing or corrupted database file.
    query = 'SELECT name FROM sqlite_schema WHERE type ="table" AND name NOT LIKE "sqlite_%";'
    with sqlite3.connect(database_path()) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        headers = list(map(lambda entries: entries[0], cursor.description))
        assert headers == ['name']

        rows = cursor.fetchall()
        assert len(rows) > 0


def test_id_region_access():
    query = 'SELECT * FROM `id_region`'
    with sqlite3.connect(database_path()) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        headers = list(map(lambda entries: entries[0], cursor.description))
        assert headers == ['id', 'label', 'description']

        rows = cursor.fetchall()
        assert len(rows) > 0
