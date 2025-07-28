import React from "react";

function TableView({ data, selected }) {
  if (data.length === 0) return <p>No data to display.</p>;

  const keys = Object.keys(data[0]);
  const isTractLevel = keys.includes("tract_id") && !["county-burden-rate", "vacancy-reasons", "structure-types"].includes(selected);
  const reorderedKeys = isTractLevel
    ? ["tract_id", ...keys.filter(k => k !== "tract_id")]
    : keys;

  return (
    <table style={{ borderCollapse: "collapse", width: "100%", marginTop: "3rem" }}>
      <thead>
        <tr>
          {reorderedKeys.map((col) => (
            <th key={col} style={{ border: "1px solid black", padding: "8px" }}>
              {col}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            {reorderedKeys.map((col, j) => (
              <td key={j} style={{ border: "1px solid black", padding: "8px" }}>
                {row[col]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default TableView;
