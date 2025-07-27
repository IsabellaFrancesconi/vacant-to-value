from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from flask import send_from_directory

app = Flask(__name__, static_folder="../client/build", static_url_path="")
CORS(app)
PRODUCTION_MODE = True 
DB_FILE = os.path.join(os.path.dirname(__file__), "acs_data.db")


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

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if PRODUCTION_MODE:
        full_path = os.path.join(app.static_folder, path)
        if path != "" and os.path.exists(full_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")
    else:
        return "React development server is running separately.", 200

@app.route('/api/<query_type>')
def query_handler(query_type):
    limit = request.args.get("limit", default=5, type=int)
    sql = None

    if query_type == "population":
        sql = f"SELECT tract_id, population FROM Tract WHERE population IS NOT NULL ORDER BY population DESC LIMIT {limit}"
    elif query_type == "poverty":
        sql = f"SELECT tract_id, sex, age_group, count_below_pov_line FROM PovertyStatus WHERE count_below_pov_line IS NOT NULL ORDER BY count_below_pov_line DESC LIMIT {limit}"
    elif query_type == "occupancy":
        sql = f"SELECT tract_id, total_units, occupied_units, vacant_units, CAST(vacant_units AS FLOAT) / NULLIF(total_units, 0) AS pct_vacant FROM OccupancyStatus WHERE total_units IS NOT NULL AND vacant_units IS NOT NULL ORDER BY pct_vacant DESC LIMIT {limit}"
    elif query_type == "rent":
        sql = f"SELECT tract_id, median_gross_rent FROM RentCost WHERE median_gross_rent IS NOT NULL ORDER BY median_gross_rent DESC LIMIT {limit}"
    elif query_type == "rent-burden":
        sql = f"SELECT tract_id, tenure_type, pct_30_plus, pct_50_plus FROM RentBurden WHERE pct_50_plus IS NOT NULL ORDER BY pct_50_plus DESC LIMIT {limit}"
    elif query_type == "tenure":
        sql = f"SELECT tract_id, owned_units, rented_units, CAST(rented_units AS FLOAT) / NULLIF(owned_units + rented_units, 0) AS pct_rented FROM Tenure WHERE owned_units IS NOT NULL AND rented_units IS NOT NULL ORDER BY pct_rented DESC LIMIT {limit}"
    elif query_type == "vacancy":
        sql = f"SELECT tract_id, vacancy_type, count FROM VacancyInfo WHERE count IS NOT NULL ORDER BY count DESC LIMIT {limit}"
    elif query_type == "structure":
        sql = f"SELECT tract_id, structure_type, occupancy_status, structure_count FROM StructureInfo WHERE structure_count IS NOT NULL ORDER BY structure_count DESC LIMIT {limit}"
    elif query_type == "bedroom":
        sql = f"SELECT tract_id, bedroom_type, occupancy_status, bedroom_count FROM BedroomInfo WHERE bedroom_count IS NOT NULL ORDER BY bedroom_count DESC LIMIT {limit}"
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
    app.run(host="0.0.0.0", port=5000, debug=True)
