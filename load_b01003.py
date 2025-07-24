# Tract Entity

import pandas as pd
import sqlite3
import os

# Define file paths
DATA_PATH = "B01003/ACSDT5Y2023.B01003-Data.csv"
DB_PATH = "acs_data.db"

# Load CSV
df = pd.read_csv(DATA_PATH, dtype=str)

# Clean up column names
df.columns = [col.strip() for col in df.columns]

# Strip "1400000US" from GEO_ID
df["tract_id"] = df["GEO_ID"].str.replace("1400000US", "", regex=False)

# Extract relevant columns
tract_df = df[["tract_id", "NAME", "B01003_001E"]].copy()
tract_df.columns = ["tract_id", "tract_name", "population"]

# Convert population to integer
tract_df["population"] = pd.to_numeric(tract_df["population"], errors="coerce").fillna(0).astype(int)

# Create SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# Create Tract table
cursor.execute("DROP TABLE IF EXISTS Tract;")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tract (
        tract_id TEXT PRIMARY KEY,
        tract_name TEXT,
        population INTEGER
    )
""")

# Insert data
tract_df.to_sql("Tract", conn, if_exists="replace", index=False)

# Commit and close
conn.commit()
conn.close()

print("db created and tract table loaded.")