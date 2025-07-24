# RentCost Entity 

import pandas as pd
import sqlite3
import os

# Define file paths
folder = 'B25064'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25064-Data.csv')
db_path = 'acs_data.db'

# Load CSV
df = pd.read_csv(data_path, dtype=str)

# Clean columns
df.columns = [col.strip() for col in df.columns]

# Extract and clean tract_id
df['tract_id'] = df['GEO_ID'].str.replace('1400000US', '', regex=False)

# Subset relevant columns
rent_df = df[['tract_id', 'B25064_001E']].copy()
rent_df.columns = ['tract_id', 'median_gross_rent']

# Convert rent to numeric
rent_df['median_gross_rent'] = pd.to_numeric(rent_df['median_gross_rent'], errors='coerce')

# Drop missing values
rent_df = rent_df.dropna()

# Connect to SQLite
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table
c.execute('DROP TABLE IF EXISTS RentCost;') 
c.execute('''
CREATE TABLE IF NOT EXISTS RentCost (
    tract_id TEXT PRIMARY KEY,
    median_gross_rent DECIMAL,
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

# Insert into database
rent_df.to_sql('RentCost', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("RentCost table successfully created and populated.")