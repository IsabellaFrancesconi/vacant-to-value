import React, { useEffect, useState } from "react";
import Map, { Source, Layer } from "react-map-gl/maplibre";
import 'maplibre-gl/dist/maplibre-gl.css';

const MAPBOX_TOKEN = "pk.eyJ1IjoibHNwNTQiLCJhIjoiY21kbHgwY3JxMWFmZDJqcTd0eHlvMHpuMSJ9.fcVtWm85GXatIEp-frEBhQ";

function MapView({ data, valueKey }) {
  const [viewState, setViewState] = useState({
    longitude: -81.7,
    latitude: 41.45,
    zoom: 10,
  });

  const [geojson, setGeojson] = useState(null);
  const [hoverInfo, setHoverInfo] = useState(null);
  const [activeKey, setActiveKey] = useState(null);
  const [sexFilter, setSexFilter] = useState("All");
  const [ageGroupFilter, setAgeGroupFilter] = useState("All");
  const [vacancyTypeFilter, setVacancyTypeFilter] = useState("All");
  const [structureTypeFilter, setStructureTypeFilter] = useState("All");
  const [bedroomTypeFilter, setBedroomTypeFilter] = useState("All");

  useEffect(() => {
    if (data.length > 0) {
      const sample = data[0];
      const numericKeys = Object.keys(sample).filter(
        k => k !== "tract_id" && typeof sample[k] === "number"
      );
      setActiveKey(numericKeys[0]);
    }
  }, [data]);

  useEffect(() => {
    fetch("/ohio_tracts.json")
      .then(res => res.json())
      .then(setGeojson)
      .catch(err => console.error("Failed to load GeoJSON", err));
  }, []);

  const filteredData = data.filter(row => {
    if (row.sex && sexFilter !== "All" && row.sex !== sexFilter) return false;
    if (row.age_group && ageGroupFilter !== "All" && row.age_group !== ageGroupFilter) return false;
    if (row.vacancy_type && vacancyTypeFilter !== "All" && row.vacancy_type !== vacancyTypeFilter) return false;
    if (row.structure_type && structureTypeFilter !== "All" && row.structure_type !== structureTypeFilter) return false;
    if (row.bedroom_type && bedroomTypeFilter !== "All" && row.bedroom_type !== bedroomTypeFilter) return false;
    return true;
  });

  const grouped = {};
  for (const row of filteredData) {
    const key = row.tract_id;
    const val = row[activeKey];
    if (typeof val === "number" && val !== 0) {
      grouped[key] = (grouped[key] || 0) + val;
    }
  }
  const valueMap = grouped;

  const values = Object.values(valueMap).sort((a, b) => a - b);
  const min = values[0];
  const max = values[values.length - 1];
  const median = values[Math.floor(values.length / 2)];

  const getColor = (val) => {
    if (typeof val !== "number" || val === 0) return "#eee";
    if (val === median) return "#ffffb2";

    const scale = val < median
      ? (val - min) / (median - min || 1e-9)
      : (val - median) / (max - median || 1e-9);

    if (val < median) {
      return scale > 0.75 ? "#66c2a4"
           : scale > 0.5  ? "#238b45"
           : scale > 0.25 ? "#00441b"
                          : "#00441b";
    } else {
      return scale > 0.75 ? "#99000d"
           : scale > 0.5  ? "#d73027"
           : scale > 0.25 ? "#f46d43"
                          : "#fdae61";
    }
  };

  const styledGeojson = geojson && {
    ...geojson,
    features: geojson.features.map((f) => {
      const tractId = f.properties.GEOID;
      const value = valueMap[tractId];
      return {
        ...f,
        properties: {
          ...f.properties,
          fill: getColor(value),
          value: value ?? null
        }
      };
    }),
  };

  const numericKeys = data.length > 0
    ? Object.keys(data[0]).filter(k => k !== "tract_id" && typeof data[0][k] === "number")
    : [];

  const colorScale = values.length > 0 ? [
    { label: `< ${Math.round(min + (median - min) * 0.25)}`, color: "#00441b" },
    { label: `< ${Math.round(min + (median - min) * 0.5)}`, color: "#238b45" },
    { label: `< ${Math.round(min + (median - min) * 0.75)}`, color: "#66c2a4" },
    { label: `< ${Math.round(median)}`, color: "#def576" },
    { label: `~ ${Math.round(median)}`, color: "#ffffb2" },
    { label: `< ${Math.round(median + (max - median) * 0.25)}`, color: "#fdae61" },
    { label: `< ${Math.round(median + (max - median) * 0.5)}`, color: "#f46d43" },
    { label: `< ${Math.round(median + (max - median) * 0.75)}`, color: "#d73027" },
    { label: `≥ ${Math.round(median + (max - median) * 0.75)}`, color: "#99000d" }
  ] : [];

  return (
    <div style={{ height: "700px", marginTop: "2rem", position: "relative" }}>
      {numericKeys.length > 1 && (
        <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {numericKeys.map((key) => (
            <button
              key={key}
              onClick={() => setActiveKey(key)}
              disabled={key === activeKey}
              style={{
                padding: "6px 10px",
                borderRadius: "5px",
                border: "1px solid #ccc",
                background: key === activeKey ? "#007cbf" : "#f0f0f0",
                color: key === activeKey ? "#fff" : "#000",
                cursor: "pointer"
              }}
            >
              {key.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      )}

      {data.length > 0 && (
        <div style={{ marginBottom: "1rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {activeKey && activeKey.includes("poverty") && (
            <>
                <div>
                <label style={{ fontSize: "13px", display: "block" }}>Sex</label>
                <select
                    value={sexFilter}
                    onChange={(e) => setSexFilter(e.target.value)}
                    style={{ padding: "4px 6px", borderRadius: "4px", fontSize: "13px" }}
                >
                    <option value="All">All</option>
                    {[...new Set(data.map(row => row.sex).filter(Boolean))].map(v => (
                    <option key={v} value={v}>{v}</option>
                    ))}
                </select>
                </div>
                <div>
                <label style={{ fontSize: "13px", display: "block" }}>Age Group</label>
                <select
                    value={ageGroupFilter}
                    onChange={(e) => setAgeGroupFilter(e.target.value)}
                    style={{ padding: "4px 6px", borderRadius: "4px", fontSize: "13px" }}
                >
                    <option value="All">All</option>
                    {[...new Set(data.map(row => row.age_group).filter(Boolean))].map(v => (
                    <option key={v} value={v}>{v}</option>
                    ))}
                </select>
                </div>
            </>
            )}

            {activeKey && activeKey.includes("vacancy") && (
            <div>
                <label style={{ fontSize: "13px", display: "block" }}>Vacancy Type</label>
                <select
                value={vacancyTypeFilter}
                onChange={(e) => setVacancyTypeFilter(e.target.value)}
                style={{ padding: "4px 6px", borderRadius: "4px", fontSize: "13px" }}
                >
                <option value="All">All</option>
                {[...new Set(data.map(row => row.vacancy_type).filter(Boolean))].map(v => (
                    <option key={v} value={v}>{v}</option>
                ))}
                </select>
            </div>
            )}

            {activeKey && activeKey.includes("structure") && (
            <div>
                <label style={{ fontSize: "13px", display: "block" }}>Structure Type</label>
                <select
                value={structureTypeFilter}
                onChange={(e) => setStructureTypeFilter(e.target.value)}
                style={{ padding: "4px 6px", borderRadius: "4px", fontSize: "13px" }}
                >
                <option value="All">All</option>
                {[...new Set(data.map(row => row.structure_type).filter(Boolean))].map(v => (
                    <option key={v} value={v}>{v}</option>
                ))}
                </select>
            </div>
            )}

            {activeKey && activeKey.includes("bedroom") && (
            <div>
                <label style={{ fontSize: "13px", display: "block" }}>Bedroom Type</label>
                <select
                value={bedroomTypeFilter}
                onChange={(e) => setBedroomTypeFilter(e.target.value)}
                style={{ padding: "4px 6px", borderRadius: "4px", fontSize: "13px" }}
                >
                <option value="All">All</option>
                {[...new Set(data.map(row => row.bedroom_type).filter(Boolean))].map(v => (
                    <option key={v} value={v}>{v}</option>
                ))}
                </select>
            </div>
            )}
        </div>
        )}


      {values.length > 0 && (
        <div style={{ marginBottom: "0.5rem" }}>
          <strong>Color Scale ({activeKey}):</strong>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginTop: "0.3rem" }}>
            {colorScale.map((step, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", fontSize: "12px" }}>
                <div style={{
                  width: "14px",
                  height: "14px",
                  backgroundColor: step.color,
                  border: "1px solid #ccc",
                  marginRight: "4px"
                }} />
                {step.label}
              </div>
            ))}
          </div>
        </div>
      )}

      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{ width: "100%", height: "100%" }}
        mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
        mapboxAccessToken={MAPBOX_TOKEN}
        interactiveLayerIds={["tract-fill"]}
        onMouseMove={(event) => {
          const feature = event.features && event.features[0];
          if (feature) {
            setHoverInfo({
              x: event.point.x,
              y: event.point.y,
              GEOID: feature.properties.GEOID,
              value: feature.properties.value,
            });
          } else {
            setHoverInfo(null);
          }
        }}
        onMouseLeave={() => setHoverInfo(null)}
      >
        {styledGeojson && (
          <Source id="tracts" type="geojson" data={styledGeojson}>
            <Layer
              id="tract-fill"
              type="fill"
              paint={{
                "fill-color": ["get", "fill"],
                "fill-opacity": 0.4,
              }}
            />
            <Layer
              id="tract-outline"
              type="line"
              paint={{
                "line-color": "#888",
                "line-width": 0.5,
              }}
            />
          </Source>
        )}

        <Source id="cwru-point" type="geojson" data={{
          type: "FeatureCollection",
          features: [{
            type: "Feature",
            geometry: {
              type: "Point",
              coordinates: [-81.6084, 41.5045],
            },
            properties: { name: "Case Western Reserve University" }
          }]
        }}>
          <Layer
            id="cwru-dot"
            type="circle"
            paint={{
              "circle-radius": 6,
              "circle-color": "#007cbf",
              "circle-stroke-color": "#fff",
              "circle-stroke-width": 2,
            }}
          />
        </Source>
      </Map>

      {hoverInfo && (
        <div
          style={{
            position: "absolute",
            left: hoverInfo.x + 10,
            top: hoverInfo.y + 10,
            backgroundColor: "white",
            padding: "5px 8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            pointerEvents: "none",
            fontSize: "13px",
            boxShadow: "0px 2px 5px rgba(0,0,0,0.2)",
            zIndex: 1000,
          }}
        >
          <div><strong>Tract:</strong> {hoverInfo.GEOID}</div>
          <div><strong>{activeKey}:</strong> {hoverInfo.value}</div>
        </div>
      )}
    </div>
  );
}

export default MapView;
