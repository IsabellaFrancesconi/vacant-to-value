# Poverty Status Entity

import pandas as pd
import sqlite3
import os

# Define file paths 
folder = 'B17001'
data_path = os.path.join(folder, 'ACSDT5Y2023.B17001-Data.csv')
metadata_path = os.path.join(folder, 'ACSDT5Y2023.B17001-Column-Metadata.csv')
db_path = 'acs_data.db' 

# Load data
df = pd.read_csv(data_path)
meta = pd.read_csv(metadata_path)

# Remove header row appearing as data 
if df.iloc[0]['GEO_ID'] == 'Geography':
    df = df.iloc[1:]
# Keep only tract-level rows 
df = df[df['GEO_ID'].str.startswith('1400000US')]
# Clean up columns
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Extract relevant estimate columns only (ending in 'E') that are not GEO_ID or NAME
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='count_below_pov_line')

# Join with metadata to get labels
meta = meta.rename(columns={'Column Name': 'column_code'})
df_merged = pd.merge(df_long, meta, on='column_code')

# Extract sex and age group from label
def parse_label(label):
    try:
        parts = label.split('!!')
        sex = parts[3].strip(':') if len(parts) > 3 else None
        age_group = parts[4].strip(':') if len(parts) > 4 else None
        return pd.Series([sex, age_group])
    except:
        return pd.Series([None, None])


df_merged[['sex', 'age_group']] = df_merged['Label'].apply(parse_label)
df_merged['tract_id'] = df_merged['GEO_ID'].str[-11:]  # Last 11 chars = tract FIPS code
df_merged = df_merged[['tract_id', 'sex', 'age_group', 'count_below_pov_line']]

# Connect to DB and insert
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table
c.execute('DROP TABLE IF EXISTS PovertyStatus;')
c.execute('''
CREATE TABLE IF NOT EXISTS PovertyStatus (
    tract_id TEXT,
    sex TEXT,
    age_group TEXT,
    count_below_pov_line INTEGER,
    PRIMARY KEY (tract_id, age_group, sex),
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

# Drop rows with missing sex/age (if any)
df_clean = df_merged.dropna(subset=['sex', 'age_group'])

# Deduplicate the df 
df_clean = df_clean.drop_duplicates(subset=['tract_id', 'sex', 'age_group'])

# Insert data
df_clean.to_sql('PovertyStatus', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("PovertyStatus table successfully created and populated.")