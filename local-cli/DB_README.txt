ACS_SQL_DB Project ReadMe
==========================

Overview:
---------
This project uses tract-level data from the U.S. Census Bureau’s 2023 American Community Survey (ACS) 5-Year Estimates for Cuyahoga County, Ohio. The data has been transformed into a normalized SQLite database designed to support queries related to housing, poverty, and occupancy characteristics in the region.

The database is populated using raw CSV data files downloaded from data.census.gov, organized by ACS table code (e.g., B01003, B25002, etc.). Each table has its own data-loading Python script and folder containing:
- The original ACS data CSV
- The associated column metadata CSV (when needed)
- A Python script (e.g., `load_b25002.py`) to process and insert cleaned data into `acs_data.db`

Database Schema:
----------------
All data is centered around the `Tract` entity (with `tract_id` as the primary key). Every other table links to it via foreign keys. Table names and contents:

1. **Tract** (`B01003`)
   - Total population per census tract

2. **PovertyStatus** (`B17001`)
   - Poverty status by sex and age group

3. **OccupancyStatus** (`B25002`)
   - Number of occupied and vacant housing units

4. **Tenure** (`B25003`)
   - Number of renter-occupied and owner-occupied units

5. **VacancyInfo** (`B25004`)
   - Number of vacant units by vacancy reason (e.g., for rent, for sale)

6. **RentCost** (`B25064`)
   - Median gross rent

7. **StructureInfo** (`B25136`)
   - Housing structure types (e.g., detached, 2-unit, 5+ unit) by occupancy

8. **BedroomInfo** (`B25137`)
   - Number of bedrooms in occupied units

9. **RentBurden** (`B25140`)
   - Percent of households (owners and renters) spending 30%+ or 50%+ of income on housing costs 

File Naming Convention:
-----------------------
- `load_bXXXXX.py`: Loads data from ACS table `BXXXXX` into a corresponding table in the SQLite database.
- Each data-loading script assumes its input files are located in a folder named `BXXXXX` in the project root.
- All scripts load data into the same shared database file: `acs_data.db`.

Data Use Notes:
---------------
- The `tract_id` corresponds to the 11-digit census tract FIPS code, used as the key to link all data.
- Tract names are not included in this database; users can look up tract geography externally via shapefiles or data.census.gov if needed.
- All data reflects estimates from 2019–2023 and is scoped to Cuyahoga County, OH.

Maintainer Notes:
-----------------
- Scripts can be rerun safely; most drop and recreate tables before inserting.
- The final database can now be used as a backend for building queries and powering front-end interfaces (e.g., for mapping or neighborhood dashboards).
