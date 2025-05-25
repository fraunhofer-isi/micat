import sqlite3
import csv

from config import import_config


def main():
    public_database_path, raw_data_path = import_config.get_paths()
    conn = sqlite3.connect(public_database_path)
    cursor = conn.cursor()

    # Ensure table exists (optional if already created)
    # fmt: off
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS measurement_specific_parameters_fuel_switch (
        id INTEGER PRIMARY KEY,
        id_parameter REAL,
        id_sector REAL,
        id_final_energy_carrier REAL,
        label VARCHAR(255),
        unit VARCHAR(255),
        importance VARCHAR(255),
        "2010" REAL,
        "2015" REAL,
        "2020" REAL,
        "2025" REAL,
        "2030" REAL,
        "2040" REAL,
        "2050" REAL
    )
    ''')

    with open("./raw_data/measurement_specific_parameters_fuel_switch_export.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = next(reader)  # Header row from CSV

        # Quote column names that are numeric or reserved words
        quoted_columns = [f'"{col}"' if col.isdigit() else col for col in columns]
        placeholders = ','.join('?' * len(columns))
        insert_sql = f'INSERT INTO measurement_specific_parameters_fuel_switch ({", ".join(quoted_columns)}) VALUES ({placeholders})'
        cursor.executemany(insert_sql, reader)
    # fmt: on

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
