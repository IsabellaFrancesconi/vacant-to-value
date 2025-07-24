# OccupancyStatus Entity 

import pandas as pd
import sqlite3
import os

# Define file paths
folder = 'B25002'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25002-Data.csv')
db_path = 'acs_data.db'

# Load CSV data
df = pd.read_csv(data_path)

# Strip and clean column names
df.columns = [col.strip() for col in df.columns]

# Add tract_id
df["tract_id"] = df["GEO_ID"].str.replace("1400000US", "", regex=False)

# Extract relevant columns
# B25002_001E = Total housing units
# B25002_002E = Occupied units
# B25002_003E = Vacant units

occupancy_df = df[["tract_id", "B25002_001E", "B25002_002E", "B25002_003E"]].copy()
occupancy_df.columns = ["tract_id", "total_units", "occupied_units", "vacant_units"]

# Convert to numeric (handle missing or invalid values)
for col in ["total_units", "occupied_units", "vacant_units"]:
    occupancy_df[col] = pd.to_numeric(occupancy_df[col], errors="coerce").fillna(0).astype(int)

# Connect to SQLite DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create OccupancyStatus table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS OccupancyStatus (
        tract_id TEXT PRIMARY KEY,
        total_units INTEGER,
        occupied_units INTEGER,
        vacant_units INTEGER,
        FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
    );
""")

# Insert data
occupancy_df.to_sql("OccupancyStatus", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("OccupancyStatus table created and loaded.")