import React from "react";
import "./App.css";

function TableView({ data, selected }) {
  if (data.length === 0) return <p>No data to display.</p>;

  const keys = Object.keys(data[0]);
  const isTractLevel = keys.includes("tract_id") && !["county-burden-rate", "vacancy-reasons", "structure-types"].includes(selected);
  const reorderedKeys = isTractLevel
    ? ["tract_id", ...keys.filter(k => k !== "tract_id")]
    : keys;

  return (
    <div className="table-wrapper">
      <div className="table-headers">
        {reorderedKeys.map((col, idx) => (
          <div key={idx} className="table-header-cell">{col}</div>
        ))}
      </div>
      <div className="table-body-scroll">
        <table className="custom-table no-header-table">
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {reorderedKeys.map((col, j) => (
                  <td key={j}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TableView;
