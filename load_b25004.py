#VacancyInfo Entity 

import pandas as pd
import sqlite3
import os

# File paths
folder = 'B25004'
data_path = os.path.join(folder, 'ACSDT5Y2023.B25004-Data.csv')
meta_path = os.path.join(folder, 'ACSDT5Y2023.B25004-Column-Metadata.csv')
db_path = 'acs_data.db'

# Load CSVs
df = pd.read_csv(data_path)
meta = pd.read_csv(meta_path)

# Extract estimate columns only
estimate_cols = [col for col in df.columns if col.endswith('E') and col not in ['GEO_ID', 'NAME']]
df_long = df.melt(id_vars=['GEO_ID'], value_vars=estimate_cols,
                  var_name='column_code', value_name='count')

# Merge with metadata to get vacancy_type
meta = meta.rename(columns={'Column Name': 'column_code'})
df_merged = pd.merge(df_long, meta, on='column_code')

# Extract vacancy_type
def extract_vacancy_type(label):
    try:
        parts = label.split('!!')
        return parts[2] if len(parts) > 2 else None
    except:
        return None

df_merged['vacancy_type'] = df_merged['Label'].apply(extract_vacancy_type)
df_merged['tract_id'] = df_merged['GEO_ID'].str[-11:]
df_merged = df_merged[['tract_id', 'vacancy_type', 'count']]
df_merged = df_merged.dropna()

# Deduplicate (in case of overlap)
df_clean = df_merged.drop_duplicates(subset=['tract_id', 'vacancy_type'])

# Convert count to integer
df_clean['count'] = pd.to_numeric(df_clean['count'], errors='coerce').fillna(0).astype(int)

# Connect to DB and create table
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table 
c.execute('DROP TABLE IF EXISTS VacancyInfo;')
c.execute('''
CREATE TABLE IF NOT EXISTS VacancyInfo (
    tract_id TEXT,
    vacancy_type TEXT,
    count INTEGER,
    PRIMARY KEY (tract_id, vacancy_type),
    FOREIGN KEY (tract_id) REFERENCES Tract(tract_id)
);
''')

# Insert data
df_clean.to_sql('VacancyInfo', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("VacancyInfo table successfully created and populated.")