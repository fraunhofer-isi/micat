# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from data_import.database_import import DatabaseImport


def import_public_data():
    current_script_name = os.path.join(os.getcwd(), os.path.basename(__file__))
    DatabaseImport.execute_import_scripts_in_folder(os.getcwd(), [current_script_name])


if __name__ == "__main__":
    import_public_data()
