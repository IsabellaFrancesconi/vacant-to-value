import React, { useState, useEffect } from "react";
import MapView from "./MapView";
import TableView from "./TableView";
import SummaryTile from "./SummaryTile";


const options = [
  { label: "Total Population", endpoint: "population" },
  { label: "Occupancy", endpoint: "occupancy" },
  { label: "Median Rent", endpoint: "rent" },
  { label: "Tenure", endpoint: "tenure" },
  { label: "Vacancy", endpoint: "vacancy" },
  { label: "Structure Info", endpoint: "structure" },
  { label: "Bedroom Info", endpoint: "bedroom" },
  { label: "High Burdened Tracts", endpoint: "high-burdened-tracts" },
  { label: "High Rent Tracts", endpoint: "high-rent-tracts" },
  { label: "High Vacancy Tracts", endpoint: "high-vacancy-tracts" },
  { label: "Poverty vs Vacancy", endpoint: "poverty-vs-vacancy" },
  { label: "Poverty Rates", endpoint: "poverty-rates" },
];

const descriptions = {
  population: "Shows the total population in each census tract.",
  occupancy: "Displays the number of housing units: total, occupied, and vacant.",
  rent: "Shows the median gross rent per tract.",
  "rent-burden": "Displays the percentage of households spending over 30% and 50% of income on rent.",
  tenure: "Breaks down units by owner-occupied vs. renter-occupied.",
  vacancy: "Displays vacant units categorized by vacancy type.",
  structure: "Shows housing unit counts by structure type and occupancy.",
  bedroom: "Breaks down bedroom counts by type and occupancy status.",
  "high-burdened-tracts": "Identifies Cuyahoga County tracts with the highest rent burden rate.",
  "county-burden-rate": "Summarizes the overall rent burden rate for the entire county.",
  "vacancy-reasons": "Breaks down total vacant units by vacancy reason (e.g., seasonal, for sale).",
  "high-rent-tracts": "Shows Cuyahoga tracts where median rent exceeds $2000.",
  "structure-types": "Summarizes total housing units by structure type across all tracts.",
  "high-vacancy-tracts": "Identifies tracts in Cuyahoga with more than 25% vacancy rate.",
  "poverty-vs-vacancy": "Displays the percentage of renter-occupied units per tract in Cuyahoga County.",
  "poverty-rates": "Ranks Cuyahoga tracts by percent of population living in poverty."
};

function App() {
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState("population");
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState("map"); 

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const effectiveLimit = viewMode === "map" ? 1000 : limit;
        const res = await fetch(`/api/${selected}?limit=${effectiveLimit}`);
        const json = await res.json();
        if (Array.isArray(json)) {
          setData(json);
        } else {
          console.error("Unexpected response format:", json);
          setData([]);
          setError("Unexpected response from server.");
        }
      } catch (err) {
        console.error("Fetch error:", err);
        setData([]);
        setError("Failed to fetch data from backend.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selected, limit, viewMode]);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Vacant to Value</h1>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          Choose a query:&nbsp;
          <select onChange={(e) => setSelected(e.target.value)} value={selected}>
            {options.map((opt) => (
              <option key={opt.endpoint} value={opt.endpoint}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>

        {selected && (
          <div style={{ marginTop: "1rem", fontStyle: "italic", color: "#444" }}>
            {descriptions[selected]}
          </div>
        )}

        {viewMode === "table" && (
          <label style={{ marginLeft: "1rem" }}>
            Rows:&nbsp;
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              min="1"
              max="1000"
            />
          </label>
        )}

        <div style={{ marginTop: "1rem" }}>
          <button
            onClick={() => setViewMode("map")}
            disabled={viewMode === "map"}
          >
            Map View
          </button>
          <button
            onClick={() => setViewMode("table")}
            disabled={viewMode === "table"}
            style={{ marginLeft: "1rem" }}
          >
            Table View
          </button>
        </div>
      </div>

      <SummaryTile selected={selected} />

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : data.length === 0 ? (
        <p>No data to display.</p>
      ) : viewMode === "table" ? (
        <TableView data={data} selected={selected} />
      ) : (
        <div style={{ height: "70vh", display: "flex", flexDirection: "column", marginTop:"5vh" }}>
          <MapView data={data} valueKey={selected} />
        </div>        
      )}
    </div>
  );
}

export default App;
