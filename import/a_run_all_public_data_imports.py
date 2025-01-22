# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sys

src_path = os.path.join(os.path.dirname(__file__), "../src")
sys.path.append(src_path)

from micat.data_import.database_import import DatabaseImport


def main():
    current_directory = os.getcwd()
    current_script_name = os.path.join(os.getcwd(), os.path.basename(__file__))
    excluded_scripts = [current_script_name]
    DatabaseImport.execute_import_scripts_in_folder(
        src_path,
        current_directory,
        excluded_scripts,
    )


if __name__ == "__main__":
    main()
