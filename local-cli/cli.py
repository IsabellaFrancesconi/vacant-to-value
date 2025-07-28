import sqlite3
from tabulate import tabulate

DB_FILE = "acs_data.db"
LIMIT = 5
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
    cur.execute(f"SELECT tract_id, population FROM Tract WHERE population IS NOT NULL ORDER BY population DESC LIMIT {LIMIT}")
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Population"], tablefmt="grid"))

def show_poverty_status():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, sex, age_group, count_below_pov_line
        FROM PovertyStatus
        
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
        
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Vacancy Type", "Count"], tablefmt="grid"))

def show_median_rent():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"SELECT tract_id, median_gross_rent FROM RentCost  LIMIT {LIMIT}")
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Median Gross Rent"], tablefmt="grid"))

def show_structure_info():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tract_id, structure_type, occupancy_status, structure_count
        FROM StructureInfo
        
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
        
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Bedroom Type", "Occupancy", "Count"], tablefmt="grid"))

def show_high_burdened_tracts():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT 
            r.tract_id,
            t.population,
            r.pct_30_plus + r.pct_50_plus AS total_burdened,
            ROUND((r.pct_30_plus + r.pct_50_plus) * 100.0 / t.population, 2) AS burden_rate_percent
        FROM RentBurden r
        JOIN Tract t ON r.tract_id = t.tract_id
        WHERE r.tract_id IS NOT NULL
          AND r.tract_id NOT IN ('Geography', 'Total', '')
          AND r.tract_id GLOB '39035*'
        ORDER BY burden_rate_percent DESC
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Population", "Total Burdened", "Burden Rate (%)"], tablefmt="grid"))

def show_county_burden_rate():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            (SELECT SUM(pct_30_plus + pct_50_plus) FROM RentBurden) AS total_burdened_households,
            (SELECT SUM(occupied_units) FROM OccupancyStatus) AS total_occupied_households,
            ROUND(
                (SELECT SUM(pct_30_plus + pct_50_plus) FROM RentBurden) * 100.0 / 
                (SELECT SUM(occupied_units) FROM OccupancyStatus), 2
            ) AS burden_rate_percent
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Total Burdened", "Total Occupied", "Burden Rate (%)"], tablefmt="grid"))

def show_vacancy_reasons():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            vacancy_type,
            SUM(count) AS total_units
        FROM VacancyInfo
        GROUP BY vacancy_type
        ORDER BY total_units DESC
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Vacancy Type", "Total Units"], tablefmt="grid"))

def show_high_rent_tracts():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT 
            r.tract_id,
            r.median_gross_rent,
            t.rented_units
        FROM RentCost r
        JOIN Tenure t ON r.tract_id = t.tract_id
        WHERE r.tract_id IS NOT NULL
          AND r.tract_id NOT IN ('Geography', 'Total', '')
          AND r.tract_id GLOB '39035*'
          AND r.median_gross_rent > 2000
        ORDER BY t.rented_units DESC
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Median Gross Rent", "Rented Units"], tablefmt="grid"))

def show_structure_types():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            structure_type,
            SUM(structure_count) AS total_units
        FROM StructureInfo
        GROUP BY structure_type
        ORDER BY total_units DESC
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Structure Type", "Total Units"], tablefmt="grid"))

def show_high_vacancy_tracts():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT 
            o.tract_id,
            o.vacant_units,
            o.total_units,
            ROUND(o.vacant_units * 100.0 / o.total_units, 2) AS vacancy_rate_percent
        FROM OccupancyStatus o
        WHERE o.tract_id IS NOT NULL
          AND o.tract_id NOT IN ('Geography', 'Total', '')
          AND o.tract_id GLOB '39035*'
          AND o.vacant_units * 100.0 / o.total_units > 25
        ORDER BY vacancy_rate_percent DESC
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Vacant Units", "Total Units", "Vacancy Rate (%)"], tablefmt="grid"))

def show_poverty_vs_vacancy():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT 
            o.tract_id,
            o.vacant_units,
            SUM(p.count_below_pov_line) AS total_poverty_count,
            t.rented_units,
            t.owned_units,
            ROUND(t.rented_units * 100.0 / (t.rented_units + t.owned_units), 2) AS pct_renter_occupied
        FROM OccupancyStatus o
        JOIN PovertyStatus p ON o.tract_id = p.tract_id
        JOIN Tenure t ON o.tract_id = t.tract_id
        WHERE o.tract_id IS NOT NULL
          AND o.tract_id NOT IN ('Geography', 'Total', '')
          AND o.tract_id GLOB '39035*'
        GROUP BY o.tract_id, o.vacant_units, t.rented_units, t.owned_units
        ORDER BY o.vacant_units DESC
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Vacant Units", "Poverty Count", "Rented Units", "Owned Units", "% Renter"], tablefmt="grid"))

def show_poverty_rates():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT 
            p.tract_id,
            SUM(p.count_below_pov_line) AS total_poverty_count,
            t.population,
            ROUND(SUM(p.count_below_pov_line) * 100.0 / t.population, 2) AS poverty_rate_percent
        FROM PovertyStatus p
        JOIN Tract t ON p.tract_id = t.tract_id
        WHERE p.tract_id IS NOT NULL
          AND p.tract_id NOT IN ('Geography', 'Total', '')
          AND p.tract_id GLOB '39035*'
        GROUP BY p.tract_id, t.population
        ORDER BY poverty_rate_percent DESC
        LIMIT {LIMIT}
    """)
    rows = cur.fetchall()
    conn.close()
    print(tabulate(rows, headers=["Tract ID", "Poverty Count", "Population", "Poverty Rate (%)"], tablefmt="grid"))


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

    sql = f"SELECT {', '.join(selected_cols)} FROM {table_name} "
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
        print("10. View high rent-burdened tracts")
        print("11. View countywide rent burden rate")
        print("12. View vacant units by reason")
        print("13. View high-rent tracts with many renters")
        print("14. View structure type counts")
        print("15. View tracts with >25% vacancy rate")
        print("16. View tracts with highest poverty and vacancy")
        print("17. View poverty rate per tract")
        print("0. Back to main menu")

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
        elif choice == "10":
            show_high_burdened_tracts()
        elif choice == "11":
            show_county_burden_rate()
        elif choice == "12":
            show_vacancy_reasons()
        elif choice == "13":
            show_high_rent_tracts()
        elif choice == "14":
            show_structure_types()
        elif choice == "15":
            show_high_vacancy_tracts()
        elif choice == "16":
            show_poverty_vs_vacancy()
        elif choice == "17":
            show_poverty_rates()

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
