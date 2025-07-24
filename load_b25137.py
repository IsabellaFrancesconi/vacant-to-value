# BedroomInfo Entity 

import pandas as pd
import sqlite3
import os

# Paths
folder = 'B25137'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25137-Data.csv')
meta_path = os.path.join(folder, 'ACSDT5Y2023.B25137-Column-Metadata.csv')
db_path = 'acs_data.db'

# Load data
df = pd.read_csv(data_path, dtype=str)
meta = pd.read_csv(meta_path)

# Clean columns
df.columns = [col.strip() for col in df.columns]
meta.columns = [col.strip() for col in meta.columns]

# Keep only estimate columns
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='bedroom_count')

# Join with metadata
meta = meta.rename(columns={'Column Name': 'column_code'})
df_merged = pd.merge(df_long, meta, on='column_code')

# Extract variables from label
def parse_label(label):
    try:
        parts = label.split("!!")
        occupancy_status = parts[2] if len(parts) > 2 else None
        bedroom_type = parts[3] if len(parts) > 3 else None
        return pd.Series([occupancy_status, bedroom_type])
    except:
        return pd.Series([None, None])

df_merged[['occupancy_status', 'bedroom_type']] = df_merged['Label'].apply(parse_label)
df_merged['tract_id'] = df_merged['GEO_ID'].str[-11:]
df_merged['bedroom_count'] = pd.to_numeric(df_merged['bedroom_count'], errors='coerce')

# Final selection and deduplication
df_clean = df_merged[['tract_id', 'bedroom_type', 'occupancy_status', 'bedroom_count']].dropna()
df_clean = df_clean.drop_duplicates(subset=['tract_id', 'bedroom_type', 'occupancy_status'])

# Load to DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
cursor.execute('DROP TABLE IF EXISTS BedroomInfo;')
cursor.execute('''
CREATE TABLE IF NOT EXISTS BedroomInfo (
    tract_id TEXT,
    bedroom_type TEXT,
    occupancy_status TEXT,
    bedroom_count INTEGER,
    PRIMARY KEY (tract_id, bedroom_type, occupancy_status),
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

df_clean.to_sql('BedroomInfo', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("BedroomInfo table successfully created and populated.")
