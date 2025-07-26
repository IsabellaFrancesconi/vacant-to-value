# RentBurden Entity (Gross rent as a % of annual household income)

import pandas as pd
import sqlite3
import os

# Define file paths
folder = 'B25140'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25140-Data.csv')
meta_path = os.path.join(folder, 'ACSDT5Y2023.B25140-Column-Metadata.csv')
db_path = 'acs_data.db'

# Load data
df = pd.read_csv(data_path, skiprows=[1])
df = df[df['GEO_ID'].str.startswith('1400000US')]
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
meta = pd.read_csv(meta_path)

# Get relevant estimate columns
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='value')

# Melt to long format
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='value')
df_long['tract_id'] = df_long['GEO_ID'].str[-11:]

# Merge with metadata
meta = meta.rename(columns={'Column Name': 'column_code'})
df_merged = pd.merge(df_long, meta, on='column_code')

# Extract tenure and burden info
def parse_label(label):
    parts = label.split('!!')
    tenure = next((p for p in parts if 'rent' in p.lower() or 'own' in p.lower()), None)
    burden = next((p for p in parts if 'over' in p.lower()), None)
    return pd.Series([tenure, burden])

df_merged[['tenure_type', 'burden_category']] = df_merged['Label'].apply(parse_label)

# Filter for "Over" burden categories
df_filtered = df_merged[df_merged['burden_category'].notna()].copy()

# Map to categories
df_filtered['category'] = df_filtered['burden_category'].apply(lambda x:
    'pct_50_plus' if 'over 50' in x.lower()
    else 'pct_30_plus' if 'over 30' in x.lower() else None
)

df_filtered = df_filtered[df_filtered['category'].notna()]

# Group and pivot
df_grouped = df_filtered.groupby(['tract_id', 'tenure_type', 'category'])['value'].sum().unstack().reset_index()

# Ensure numeric
df_grouped['pct_30_plus'] = pd.to_numeric(df_grouped.get('pct_30_plus'), errors='coerce')
df_grouped['pct_50_plus'] = pd.to_numeric(df_grouped.get('pct_50_plus'), errors='coerce')

# Drop missing
df_clean = df_grouped.dropna(subset=['pct_30_plus', 'pct_50_plus'])

# Insert into DB
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table
c.execute('DROP TABLE IF EXISTS RentBurden;')
c.execute('''
CREATE TABLE IF NOT EXISTS RentBurden (
    tract_id TEXT,
    tenure_type TEXT,
    pct_30_plus REAL,
    pct_50_plus REAL,
    PRIMARY KEY (tract_id, tenure_type),
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

# Insert data 
df_clean.to_sql('RentBurden', conn, if_exists='append', index=False)
df_clean.to_sql('RentBurden', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

print("RentBurden table successfully created and populated.")