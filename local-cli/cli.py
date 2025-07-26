import sqlite3
from tabulate import tabulate

DB_FILE = "acs_data.db"
LIMIT = 5
FILTER = "WHERE tract_id IS NOT NULL AND tract_id NOT IN ('Geography', 'Total', '') AND tract_id GLOB '39035*'"
TABLES = {
    "Tract": ["tract_id", "population"],
    "PovertyStatus": ["tract_id", "sex", "age_group", "count_below_pov_line"],
    "OccupancyStatus": ["tract_id", "total_units", "occupied_units", "vacant_units"],
    "RentCost": ["tract_id", "median_gross_rent"],
    "Tenure": ["tract_id", "owned_units", "rented_units"],
    "VacancyInfo": ["tract_id", "vacancy_type", "count"],
    "StructureInfo": ["tract_id", "structure_type", "occupancy_status", "structure_count"],
    "BedroomInfo": ["tract_id", "bedroom_type", "occupancy_status", "bedroom_count"],
    "RentBurden": ["tract_id", "tenure_type", "pct_30_plus", "pct_50_plus"]
}

## ---------------------------------------------------------------------------------------------------------------- ##


def show_total_population():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT tract_id, population FROM Tract {FILTER} LIMIT {LIMIT}")
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Population"], tablefmt="grid"))

def show_poverty_status():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, sex, age_group, count_below_pov_line
        FROM PovertyStatus
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Sex", "Age Group", "Below Poverty Line"], tablefmt="grid"))

def show_occupancy_status():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, total_units, occupied_units, vacant_units
        FROM OccupancyStatus
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Total Units", "Occupied", "Vacant"], tablefmt="grid"))

def show_tenure():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, owned_units, rented_units
        FROM Tenure
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Owner-Occupied", "Renter-Occupied"], tablefmt="grid"))

def show_vacancy_info():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, vacancy_type, count
        FROM VacancyInfo
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Vacancy Type", "Count"], tablefmt="grid"))

def show_median_rent():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT tract_id, median_gross_rent FROM RentCost {FILTER} LIMIT {LIMIT}")
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Median Gross Rent"], tablefmt="grid"))

def show_structure_info():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, structure_type, occupancy_status, structure_count
        FROM StructureInfo
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Structure Type", "Occupancy", "Count"], tablefmt="grid"))

def show_bedroom_info():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, bedroom_type, occupancy_status, bedroom_count
        FROM BedroomInfo
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Bedroom Type", "Occupancy", "Count"], tablefmt="grid"))

def modular_query():
    print("\nAvailable Tables:")
    for i, table in enumerate(TABLES.keys(), start=1):
        print(f"{i}. {table}")
    try:
        table_choice = int(input("Choose a table number: ").strip())
        table_name = list(TABLES.keys())[table_choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    columns = TABLES[table_name]
    print("\nAvailable Columns:")
    for i, col in enumerate(columns, start=1):
        print(f"{i}. {col}")
    print("Enter column numbers separated by commas (e.g., 1,3,4) or press Enter for all:")
    col_input = input("Columns: ").strip()

    if col_input:
        try:
            selected_cols = [columns[int(i.strip()) - 1] for i in col_input.split(",")]
        except (ValueError, IndexError):
            print("Invalid column selection.")
            return
    else:
        selected_cols = columns

    where_clause = input("Optional WHERE clause (e.g., sex='Male' AND age_group='18-24'): ").strip()
    limit_clause = f"LIMIT {LIMIT}"

    sql = f"SELECT {', '.join(selected_cols)} FROM {table_name} {FILTER}"
    if where_clause:
        sql += f" AND {where_clause}"
    sql += f" {limit_clause}"

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        print(tabulate(rows, headers=selected_cols, tablefmt="grid"))
    except Exception as e:
        print(f"Query failed: {e}")


def show_rent_burden():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, tenure_type, pct_30_plus, pct_50_plus
        FROM RentBurden
        {FILTER}
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Tenure Type", "% ≥ 30% Income", "% ≥ 50% Income"], tablefmt="grid"))

def sample_query():
    while True:
        print("\n--- ACS Data CLI: Cuyahoga County ---")
        print("1. View total population per tract")
        print("2. View poverty status by age group")
        print("3. View housing occupancy (vacant vs occupied)")
        print("4. View median gross rent by tract")
        print("5. View % of rent-burdened households")
        print("6. View tenure (owner vs renter)")
        print("7. View vacancy reasons")
        print("8. View structure types")
        print("9. View bedroom counts")
        print("0. Exit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            show_total_population()
        elif choice == "2":
            show_poverty_status()
        elif choice == "3":
            show_occupancy_status()
        elif choice == "4":
            show_median_rent()
        elif choice == "5":
            show_rent_burden()
        elif choice == "6":
            show_tenure()
        elif choice == "7":
            show_vacancy_info()
        elif choice == "8":
            show_structure_info()
        elif choice == "9":
            show_bedroom_info()
        elif choice == "0":
            break
        else:
            print("Invalid selection. Try again.")

def set_limit():
    global LIMIT
    while True:
        try:
            print("\n--- ACS Data CLI: Cuyahoga County ---")
            new_limit = int(input("Enter the number of rows to display (default is 5): ").strip())
            if new_limit > 0:
                LIMIT = new_limit
                print(f"Row limit set to {LIMIT}.")
                break
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Using default limit of 5.")


def main():
    while True:
        print("\n--- ACS Data CLI: Cuyahoga County ---")
        print("1. Set number of rows to display (default is 5)")
        print("2. View Sample Queries")
        print("3. Modular Query (build your own)")
        print("0. Exit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            set_limit()
        elif choice == "2":
            sample_query()
        elif choice == "3":
            modular_query()
        elif choice == "0":
            print("Exiting the CLI.")
            break


        

if __name__ == "__main__":
    main()
