# Tenure Entity

import pandas as pd
import sqlite3
import os

# File paths
folder = 'B25003'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25003-Data.csv')
db_path = 'acs_data.db'

# Load data
df = pd.read_csv(data_path, dtype=str)

# Clean up column names
df.columns = [col.strip() for col in df.columns]

# Create tract_id by removing prefix
df['tract_id'] = df['GEO_ID'].str.replace("1400000US", "", regex=False)

# Extract and rename relevant columns
tenure_df = df[['tract_id', 'B25003_002E', 'B25003_003E']].copy()
tenure_df.columns = ['tract_id', 'owned_units', 'rented_units']

# Convert to numeric types
tenure_df['owned_units'] = pd.to_numeric(tenure_df['owned_units'], errors='coerce').fillna(0).astype(int)
tenure_df['rented_units'] = pd.to_numeric(tenure_df['rented_units'], errors='coerce').fillna(0).astype(int)

# Connect to DB
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Drop existing table
c.execute('DROP TABLE IF EXISTS Tenure;')
# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS Tenure (
    tract_id TEXT PRIMARY KEY,
    owned_units INTEGER,
    rented_units INTEGER,
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

# Insert data
tenure_df.to_sql('Tenure', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("Tenure table successfully created and populated.")