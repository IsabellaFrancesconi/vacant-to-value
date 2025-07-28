import React, { useEffect, useState } from "react";

function SummaryTile({ selected }) {
  const [summaryData, setSummaryData] = useState([]);
  const [summaryTitle, setSummaryTitle] = useState("County Summary");

  useEffect(() => {
    const loadSummary = async () => {
      let endpoint = null;
      let title = "County Summary";

      if (selected === "vacancy") {
        endpoint = "vacancy-reasons";
        title = "Vacancy Reasons (All Tracts)";
      } else if (selected === "structure-types") {
        endpoint = "structure-types";
        title = "Structure Types Summary";
      } else if (selected === "county-burden-rate") {
        endpoint = "county-burden-rate";
        title = "County Rent Burden Rate";
      } else {
        try {
          const [burden, poverty, occupancy] = await Promise.all([
            fetch("/api/county-burden-rate").then(res => res.json()),
            fetch("/api/poverty-rates?limit=10000").then(res => res.json()),
            fetch("/api/occupancy?limit=10000").then(res => res.json())
          ]);

          const totalPoverty = poverty.reduce((sum, row) => sum + (row.total_poverty_count || 0), 0);
          const totalPop = poverty.reduce((sum, row) => sum + (row.population || 0), 0);
          const povertyRate = totalPop > 0 ? ((totalPoverty / totalPop) * 100).toFixed(2) : "N/A";

          const totalVacant = occupancy.reduce((sum, row) => sum + (row.vacant_units || 0), 0);
          const totalUnits = occupancy.reduce((sum, row) => sum + (row.total_units || 0), 0);
          const vacancyRate = totalUnits > 0 ? ((totalVacant / totalUnits) * 100).toFixed(2) : "N/A";

          setSummaryData([
            { label: "County Rent Burden (%)", value: burden[0]?.burden_rate_percent ?? "N/A" },
            { label: "Avg Poverty Rate (%)", value: povertyRate },
            { label: "Avg Vacancy Rate (%)", value: vacancyRate },
          ]);
          setSummaryTitle("Countywide Summary");
          return;
        } catch (err) {
          console.error("Summary fallback failed:", err);
          setSummaryData([]);
        }
      }

      if (endpoint) {
        try {
          const res = await fetch(`/api/${endpoint}`);
          const json = await res.json();
          if (Array.isArray(json)) setSummaryData(json);
          else setSummaryData([json]);
          setSummaryTitle(title);
        } catch (err) {
          console.error("Summary fetch error:", err);
          setSummaryData([]);
        }
      }
    };

    loadSummary();
  }, [selected]);

  if (summaryData.length === 0) return null;

  return (
    <div style={{
      position: "absolute",
      top: "2rem",
      right: "2rem",
      background: "#f8f8f8",
      border: "1px solid #ccc",
      padding: "1rem",
      borderRadius: "8px",
      maxWidth: "300px",
      boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
      fontSize: "0.9rem"
    }}>
      <strong>{summaryTitle}</strong>
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        rowGap: "0.4rem",
        columnGap: "1rem",
        marginTop: "0.5rem"
        }}>
        {summaryData.map((item, idx) => (
            <React.Fragment key={idx}>
            <div>
                {item.label || item.vacancy_type || item.structure_type || "Unknown"}
            </div>
            <div style={{ textAlign: "right", fontWeight: 500 }}>
                {item.value || item.total_units || "—"}
            </div>
            </React.Fragment>
        ))}
        </div>
    </div>
  );
}

export default SummaryTile;
