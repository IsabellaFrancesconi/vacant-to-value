import React, { useState, useEffect } from "react";

const options = [
  { label: "Total Population", endpoint: "population" },
  { label: "Poverty Status", endpoint: "poverty" },
  { label: "Occupancy", endpoint: "occupancy" },
  { label: "Median Rent", endpoint: "rent" },
  { label: "Rent Burden", endpoint: "rent-burden" },
  { label: "Tenure", endpoint: "tenure" },
  { label: "Vacancy", endpoint: "vacancy" },
  { label: "Structure Info", endpoint: "structure" },
  { label: "Bedroom Info", endpoint: "bedroom" },
];

function App() {
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState("population");
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`/api/${selected}?limit=${limit}`);
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
  }, [selected, limit]);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>ACS Data Viewer</h1>

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

        <label style={{ marginLeft: "1rem" }}>
          Rows:&nbsp;
          <input
            type="number"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            min="1"
            max="100"
          />
        </label>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : data.length === 0 ? (
        <p>No data to display.</p>
      ) : (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              {Object.keys(data[0]).map((col) => (
                <th key={col} style={{ border: "1px solid black", padding: "8px" }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((cell, j) => (
                  <td key={j} style={{ border: "1px solid black", padding: "8px" }}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
