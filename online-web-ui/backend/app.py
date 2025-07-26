from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.abspath("acs_data.db")

def run_query(query):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print("[ERROR] run_query failed:", e)
        raise

@app.route('/')
def index():
    return "<h1>Flask API is running</h1>"

@app.route('/api/<query_type>')
def query_handler(query_type):
    limit = request.args.get("limit", default=5, type=int)
    sql = None

    if query_type == "population":
        sql = f"SELECT tract_id, population FROM Tract LIMIT {limit}"
    elif query_type == "poverty":
        sql = f"SELECT tract_id, sex, age_group, count_below_pov_line FROM PovertyStatus LIMIT {limit}"
    elif query_type == "occupancy":
        sql = f"SELECT tract_id, total_units, occupied_units, vacant_units FROM OccupancyStatus LIMIT {limit}"
    elif query_type == "rent":
        sql = f"SELECT tract_id, median_gross_rent FROM RentCost LIMIT {limit}"
    elif query_type == "rent-burden":
        sql = f"SELECT tract_id, tenure_type, pct_30_plus, pct_50_plus FROM RentBurden LIMIT {limit}"
    elif query_type == "tenure":
        sql = f"SELECT tract_id, owned_units, rented_units FROM Tenure LIMIT {limit}"
    elif query_type == "vacancy":
        sql = f"SELECT tract_id, vacancy_type, count FROM VacancyInfo LIMIT {limit}"
    elif query_type == "structure":
        sql = f"SELECT tract_id, structure_type, occupancy_status, structure_count FROM StructureInfo LIMIT {limit}"
    elif query_type == "bedroom":
        sql = f"SELECT tract_id, bedroom_type, occupancy_status, bedroom_count FROM BedroomInfo LIMIT {limit}"
    else:
        return jsonify({"error": "Invalid query type"}), 400

    try:
        return jsonify(run_query(sql))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def test_all_queries():
    queries = [
        "SELECT tract_id, population FROM Tract LIMIT 1",
        "SELECT tract_id, sex, age_group, count_below_pov_line FROM PovertyStatus LIMIT 1",
        "SELECT tract_id, total_units, occupied_units, vacant_units FROM OccupancyStatus LIMIT 1",
        "SELECT tract_id, median_gross_rent FROM RentCost LIMIT 1",
        "SELECT tract_id, tenure_type, pct_30_plus, pct_50_plus FROM RentBurden LIMIT 1",
        "SELECT tract_id, owned_units, rented_units FROM Tenure LIMIT 1",
        "SELECT tract_id, vacancy_type, count FROM VacancyInfo LIMIT 1",
        "SELECT tract_id, structure_type, occupancy_status, structure_count FROM StructureInfo LIMIT 1",
        "SELECT tract_id, bedroom_type, occupancy_status, bedroom_count FROM BedroomInfo LIMIT 1",
    ]
    for q in queries:
        try:
            print(run_query(q))
        except Exception as e:
            print(f"[FAIL] {q}\n  └─ {e}")

if __name__ == '__main__':
    app.run(debug=True)
