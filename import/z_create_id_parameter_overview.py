# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from config import import_config

from micat.input.database import Database


def main():
    public_database_path, _raw_data_path = import_config.get_paths()

    database = Database(public_database_path)

    id_to_table_mapping = _create_id_to_table_mapping(database)

    for id_value, table_names in id_to_table_mapping.items():
        print(str(id_value) + ':' + str(table_names))


def _create_id_to_table_mapping(database):
    id_to_table_mapping = {}
    tables = database.table('sqlite_master', {'type': '"table"'})
    table_names = tables['name'].values
    for table_name in table_names:
        if table_name.startswith('id'):
            continue
        if table_name.startswith('mapping'):
            continue

        table = database.table(table_name, {})
        id_column_names, _, _ = table.column_names
        if 'id_parameter' in id_column_names:
            id_parameter_values = table.unique_index_values('id_parameter')
            for id_value in id_parameter_values:
                if id_value not in id_to_table_mapping:
                    id_to_table_mapping[id_value] = set()

                id_to_table_mapping[id_value].add(table_name)

    sorted_mapping = _sort_dictionary_by_keys(id_to_table_mapping)
    return sorted_mapping


def _sort_dictionary_by_keys(dictionary):
    sorted_dictionary = dict(sorted(dictionary.items()))
    return sorted_dictionary


if __name__ == "__main__":
    main()
