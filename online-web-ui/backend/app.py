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
        sql = f"""
            SELECT 
                tract_id, 
                total_units, 
                occupied_units, 
                vacant_units, 
                CAST(vacant_units AS FLOAT) * 100.0 / NULLIF(total_units, 0) AS pct_vacant 
            FROM OccupancyStatus 
            WHERE total_units IS NOT NULL AND vacant_units IS NOT NULL 
            ORDER BY pct_vacant DESC 
            LIMIT {limit}
        """
    elif query_type == "rent":
        sql = f"SELECT tract_id, median_gross_rent FROM RentCost WHERE median_gross_rent IS NOT NULL ORDER BY median_gross_rent DESC LIMIT {limit}"
    elif query_type == "rent-burden":
        sql = f"SELECT tract_id, tenure_type, pct_30_plus, pct_50_plus FROM RentBurden WHERE pct_50_plus IS NOT NULL ORDER BY pct_50_plus DESC LIMIT {limit}"
    elif query_type == "tenure":
        sql = f"""
            SELECT 
                tract_id, 
                100.0 * CAST(rented_units AS FLOAT) / NULLIF(owned_units + rented_units, 0) AS pct_rented 
            FROM Tenure 
            WHERE owned_units IS NOT NULL AND rented_units IS NOT NULL 
            ORDER BY pct_rented DESC 
            LIMIT {limit}
        """
    elif query_type == "vacancy":
        sql = f"SELECT tract_id, vacancy_type, count FROM VacancyInfo WHERE count IS NOT NULL ORDER BY count DESC LIMIT {limit}"
    elif query_type == "structure":
        sql = f"SELECT tract_id, structure_type, occupancy_status, structure_count FROM StructureInfo WHERE structure_count IS NOT NULL ORDER BY structure_count DESC LIMIT {limit}"
    elif query_type == "bedroom":
        sql = f"SELECT tract_id, bedroom_type, occupancy_status, bedroom_count FROM BedroomInfo WHERE bedroom_count IS NOT NULL ORDER BY bedroom_count DESC LIMIT {limit}"
    elif query_type == "high-burdened-tracts":
        sql = f"""
            SELECT 
                r.tract_id,
                t.population,
                r.pct_30_plus + r.pct_50_plus AS total_burdened,
                ROUND((r.pct_30_plus + r.pct_50_plus) * 100.0 / t.population, 2) AS burden_rate_percent
            FROM RentBurden r
            JOIN Tract t ON r.tract_id = t.tract_id
            WHERE r.tract_id IS NOT NULL
            AND r.tract_id NOT IN ('Geography', 'Total', '')
            AND r.tract_id GLOB '39035*'
            ORDER BY burden_rate_percent DESC
            LIMIT {limit}
        """
    elif query_type == "county-burden-rate":
        sql = f"""
            SELECT 
                (SELECT SUM(pct_30_plus + pct_50_plus) FROM RentBurden) AS total_burdened_households,
                (SELECT SUM(occupied_units) FROM OccupancyStatus) AS total_occupied_households,
                ROUND(
                    (SELECT SUM(pct_30_plus + pct_50_plus) FROM RentBurden) * 100.0 / 
                    (SELECT SUM(occupied_units) FROM OccupancyStatus), 2
                ) AS burden_rate_percent
        """
    elif query_type == "vacancy-reasons":
        sql = f"""
            SELECT 
                '' AS tract_id,
                vacancy_type,
                SUM(count) AS total_units
            FROM VacancyInfo
            GROUP BY vacancy_type
            ORDER BY total_units DESC
        """
    elif query_type == "high-rent-tracts":
        sql = f"""
            SELECT 
                r.tract_id,
                r.median_gross_rent
            FROM RentCost r
            JOIN Tenure t ON r.tract_id = t.tract_id
            WHERE r.tract_id IS NOT NULL
            AND r.tract_id NOT IN ('Geography', 'Total', '')
            AND r.tract_id GLOB '39035*'
            AND r.median_gross_rent > 2000
            ORDER BY r.median_gross_rent DESC
            LIMIT {limit}
        """

    elif query_type == "structure-types":
        sql = f"""
            SELECT 
                '' AS tract_id,
                structure_type,
                SUM(structure_count) AS total_units
            FROM StructureInfo
            GROUP BY structure_type
            ORDER BY total_units DESC
        """
    elif query_type == "high-vacancy-tracts":
        sql = f"""
            SELECT 
                o.tract_id,
                ROUND(o.vacant_units * 100.0 / o.total_units, 2) AS vacancy_rate_percent
            FROM OccupancyStatus o
            WHERE o.tract_id IS NOT NULL
            AND o.tract_id NOT IN ('Geography', 'Total', '')
            AND o.tract_id GLOB '39035*'
            AND o.vacant_units * 100.0 / o.total_units > 25
            ORDER BY vacancy_rate_percent DESC
            LIMIT {limit}
        """
    elif query_type == "poverty-vs-vacancy":
        sql = f"""
            SELECT 
                o.tract_id,
                ROUND(t.rented_units * 100.0 / (t.rented_units + t.owned_units), 2) AS pct_renter_occupied
            FROM OccupancyStatus o
            JOIN Tenure t ON o.tract_id = t.tract_id
            WHERE o.tract_id IS NOT NULL
            AND o.tract_id NOT IN ('Geography', 'Total', '')
            AND o.tract_id GLOB '39035*'
            GROUP BY o.tract_id, t.rented_units, t.owned_units
            ORDER BY pct_renter_occupied DESC
            LIMIT {limit}
        """

    elif query_type == "poverty-rates":
        sql = f"""
            SELECT 
                p.tract_id,
                SUM(p.count_below_pov_line) AS total_poverty_count,
                t.population,
                ROUND(SUM(p.count_below_pov_line) * 100.0 / t.population, 2) AS poverty_rate_percent
            FROM PovertyStatus p
            JOIN Tract t ON p.tract_id = t.tract_id
            WHERE p.tract_id IS NOT NULL
            AND p.tract_id NOT IN ('Geography', 'Total', '')
            AND p.tract_id GLOB '39035*'
            GROUP BY p.tract_id, t.population
            ORDER BY poverty_rate_percent DESC
            LIMIT {limit}
        """
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
