# © 2024 - 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from micat.template import validators


def column_names(database, table_name):
    query = f"""pragma table_info({table_name})"""
    where_clause = {}
    table_ = database.query(query, where_clause)
    column_names_ = table_["name"].values
    return column_names_


def filter_column_names_by_id_mode(column_names_, id_mode, years=None):
    year_columns = _year_range(id_mode)
    if years is not None:
        year_columns = set(year_columns).intersection(years)
        if len(year_columns) == 0:
            # No valid years are selected, fall back to default
            year_columns = _year_range(id_mode)
    filtered_column_names = list(
        filter(lambda column_name: _year_columns_filter(column_name, year_columns), column_names_),
    )
    return filtered_column_names


def _year_range(id_mode):
    min_year = validators.min_year(id_mode)
    max_year = validators.max_year(id_mode)
    year_columns = list(str(el) for el in range(min_year, max_year + 1, 1))
    return year_columns


def _year_columns_filter(column_name, year_columns):
    if column_name.isdigit() and column_name not in year_columns:
        return False
    return True


def table(database, table_name, column_names_=None, where_clause=None):
    if (
        column_names_ is None
        or isinstance(column_names_, str)
        or isinstance(column_names_, list)
        and len(column_names_) == 0
    ):
        column_names_str = "*"
    else:
        column_names_str = ", ".join('"' + name + '"' for name in column_names_)
    query = f"SELECT {column_names_str} FROM {table_name}"
    if where_clause is None:
        where_clause = {}
    table_ = database.query(query, where_clause)
    return table_


def parameter_table(
    database,
    id_mode,
    table_name,
    where_clause,
):
    column_names_ = column_names(database, table_name)
    filtered_column_names = filter_column_names_by_id_mode(column_names_, id_mode)
    parameter_table_ = table(database, table_name, filtered_column_names, where_clause)
    return parameter_table_
