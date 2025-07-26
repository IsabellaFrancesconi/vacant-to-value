# StructureInfo Entity 

import pandas as pd
import sqlite3
import os

# Define file paths
folder = 'B25136'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25136-Data.csv')
metadata_path = os.path.join(folder, 'ACSDT5Y2023.B25136-Column-Metadata.csv')
db_path = 'acs_data.db'

# Load data
df = pd.read_csv(data_path, dtype=str)
meta = pd.read_csv(metadata_path)

# Drop first row if it's a header accidentally read as data
if df.iloc[0]['GEO_ID'] == 'Geography':
    df = df.iloc[1:]

# Keep only census tract-level rows (starts with 1400000US)
df = df[df['GEO_ID'].str.startswith('1400000US')]

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Extract only estimate columns
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]

# Melt the dataframe
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='structure_count')

# Join with metadata
meta = meta.rename(columns={'Column Name': 'column_code'})
df_merged = pd.merge(df_long, meta, on='column_code')

# Extract structure type and occupancy status from label
def parse_structure_label(label):
    try:
        parts = label.split('!!')
        occupancy_status = parts[2] if len(parts) > 2 else None
        structure_type = parts[3] if len(parts) > 3 else None
        return pd.Series([structure_type, occupancy_status])
    except:
        return pd.Series([None, None])

df_merged[['structure_type', 'occupancy_status']] = df_merged['Label'].apply(parse_structure_label)
df_merged['tract_id'] = df_merged['GEO_ID'].str[-11:]

# Clean and format final dataframe
df_final = df_merged[['tract_id', 'structure_type', 'occupancy_status', 'structure_count']].dropna()
df_final['structure_count'] = pd.to_numeric(df_final['structure_count'], errors='coerce').fillna(0).astype(int)
df_final = df_final.drop_duplicates()

# Connect to SQLite and insert
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table
c.execute('DROP TABLE IF EXISTS StructureInfo;')
c.execute('''
CREATE TABLE IF NOT EXISTS StructureInfo (
    tract_id TEXT,
    structure_type TEXT,
    occupancy_status TEXT,
    structure_count INTEGER,
    PRIMARY KEY (tract_id, structure_type, occupancy_status),
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

df_final.to_sql('StructureInfo', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("StructureInfo table created and populated.")