import React, { useEffect, useState } from "react";
import Map, { Source, Layer } from "react-map-gl/maplibre";
import 'maplibre-gl/dist/maplibre-gl.css';

const MAPBOX_TOKEN = "pk.eyJ1IjoibHNwNTQiLCJhIjoiY21kbHgwY3JxMWFmZDJqcTd0eHlvMHpuMSJ9.fcVtWm85GXatIEp-frEBhQ";

function MapView({ data, valueKey }) {
  const [viewState, setViewState] = useState({
    longitude: -81.7,
    latitude: 41.45,
    zoom: 10,
    pitch: 50,
    bearing: -20,
  });

  const [geojson, setGeojson] = useState(null);
  const [hoverInfo, setHoverInfo] = useState(null);
  const [activeKey, setActiveKey] = useState(null);
  const [sexFilter, setSexFilter] = useState("All");
  const [ageGroupFilter, setAgeGroupFilter] = useState("All");
  const [vacancyTypeFilter, setVacancyTypeFilter] = useState("All");
  const [structureTypeFilter, setStructureTypeFilter] = useState("All");
  const [bedroomTypeFilter, setBedroomTypeFilter] = useState("All");
  const [selectedOpacity] = useState(0.6);
  const [unselectedOpacity] = useState(0.1);
  const [show3D, setShow3D] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const mapStyleUrl = darkMode
    ? "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    : "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";




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
    features: geojson.features
      .filter((f) => {
        const tractId = f.properties.GEOID;
        return typeof valueMap[tractId] === "number";
      })
      .map((f) => {
        const tractId = f.properties.GEOID;
        const value = valueMap[tractId];
        const scaledHeight = ((value - min) / (max - min || 1)) * 5000;

        return {
          ...f,
          properties: {
            ...f.properties,
            fill: getColor(value),
            value,
            height: scaledHeight
          }
        };
      }),
  };

  const numericKeys = data.length > 0
  ? (() => {
      let keys = Object.keys(data[0]).filter(
        k => k !== "tract_id" && typeof data[0][k] === "number"
      );

      if (keys.includes("poverty_rate_percent")) {
        return ["poverty_rate_percent"];
      }

      const occupancyOrder = ["total_units", "vacant_units", "occupied_units", "pct_vacant"];
      if (occupancyOrder.some(k => keys.includes(k))) {
        return occupancyOrder.filter(k => keys.includes(k));
      }

      return keys;
    })()
  : [];


  const colorScale = [];

  if (values.length > 0) {
    const thresholds = [];

    const getBreakpoint = (factor, low = true) =>
      Math.round(low
        ? min + (median - min) * factor
        : median + (max - median) * factor);

    thresholds.push({ label: `> ${getBreakpoint(0.25)}`, color: "#00441b" });
    thresholds.push({ label: `< ${getBreakpoint(0.5)}`, color: "#238b45" });
    thresholds.push({ label: `< ${getBreakpoint(0.75)}`, color: "#66c2a4" });
    thresholds.push({ label: `< ${Math.round(median)}`, color: "#def576" });
    thresholds.push({ label: `~ ${Math.round(median)}`, color: "#ffffb2" });
    thresholds.push({ label: `< ${getBreakpoint(0.25, false)}`, color: "#fdae61" });
    thresholds.push({ label: `< ${getBreakpoint(0.5, false)}`, color: "#f46d43" });
    thresholds.push({ label: `< ${getBreakpoint(0.75, false)}`, color: "#d73027" });
    thresholds.push({ label: `≥ ${getBreakpoint(0.75, false)}`, color: "#99000d" });

    colorScale.push(...thresholds);
  }


  return (
    <div style={{ height: "calc(100vh - 200px)", position: "relative", overflow: "hidden" }}>
      {numericKeys.length > 1 && activeKey !== "burden_rate_percent" && (
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
              {key === "pct_vacant"
                ? "Vacant %"
                : key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      )}

      {data.length > 0 && activeKey !== "burden_rate_percent" && (
        <div style={{ marginBottom: "1rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {activeKey && activeKey.includes("poverty") && activeKey !== "poverty_rate_percent" && (
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


            {activeKey && activeKey.includes("vacancy") && activeKey !== "vacancy_rate_percent" && (
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

      <button
        onClick={() => setDarkMode(prev => !prev)}
        style={{
          position: "absolute",
          top: "65px",
          right: "10px",
          zIndex: 1000,
          padding: "6px 10px",
          borderRadius: "5px",
          border: "1px solid #ccc",
          backgroundColor: darkMode ? "#333" : "#f0f0f0",
          color: darkMode ? "#fff" : "#000",
          cursor: "pointer"
        }}
      >
        {darkMode ? "Light Mode" : "Dark Mode"}
      </button>

      <button
        onClick={() => {
          setShow3D(prev => {
            const next = !prev;
            if (!next) {
              setViewState(v => ({
                ...v,
                pitch: 0,
                bearing: 0
              }));
            } else {
              setViewState(v => ({
                ...v,
                pitch: 50,
                bearing: -20
              }));
            }
            return next;
          });
        }}
        style={{
          position: "absolute",
          top: "130px",
          right: "10px",
          zIndex: 1000,
          padding: "6px 10px",
          borderRadius: "5px",
          border: "1px solid #ccc",
          backgroundColor: show3D ? "#007cbf" : "#f0f0f0",
          color: show3D ? "#fff" : "#000",
          cursor: "pointer",
          transform: "translateY(-100%)" // optionally push it above the scale box
        }}
      >
        {show3D ? "Disable 3D" : "Enable 3D"}
      </button>

      {values.length > 0 && (
        <div style={{
          position: "absolute",
          top: "140px",
          right: "10px",
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          padding: "10px",
          border: "1px solid #ccc",
          borderRadius: "6px",
          fontSize: "12px",
          zIndex: 1000,
          maxHeight: "80vh",
          overflowY: "auto"
        }}>
          <div style={{ fontWeight: "bold", marginBottom: "6px" }}>Color Scale</div>
          {colorScale.map((step, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: "4px" }}>
              <div style={{
                width: "14px",
                height: "14px",
                backgroundColor: step.color,
                border: "1px solid #ccc",
                marginRight: "6px"
              }} />
              <span>{step.label}</span>
            </div>
          ))}
        </div>
      )}
      



      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{ width: "100%", height: "100%" }}
        mapStyle={mapStyleUrl}
        mapboxAccessToken={MAPBOX_TOKEN}
        interactiveLayerIds={["tract-fill"]}
        dragRotate={true}
        pitchWithRotate={true}
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
                "fill-opacity": [
                  "case",
                  ["==", ["get", "value"], null],
                  unselectedOpacity,
                  selectedOpacity
                ],
              }}
            />
            <Layer
              id="tract-outline"
              type="line"
              paint={{
                "line-color": "#888",
                "line-width": 0.2,
              }}
            />
            {show3D && (
              <Layer
                id="tract-3d"
                type="fill-extrusion"
                paint={{
                  "fill-extrusion-color": ["get", "fill"],
                  "fill-extrusion-height": ["coalesce", ["get", "height"], 0],
                  "fill-extrusion-base": 0,
                  "fill-extrusion-opacity": 0.8
                }}
              />
            )}

          </Source>
        )}

        <Source id="cwru-pillar" type="geojson" data={{
          type: "FeatureCollection",
          features: [{
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [[
                [-81.6086, 41.5043],  // Bottom-left
                [-81.6082, 41.5043],  // Bottom-right
                [-81.6082, 41.5047],  // Top-right
                [-81.6086, 41.5047],  // Top-left
                [-81.6086, 41.5043]
              ]]
            },
            properties: {
              height: 20000,
              color: "#007cbf"
            }
          }]
        }}>
          <Layer
            id="cwru-pillar"
            type="fill-extrusion"
            paint={{
              "fill-extrusion-color": ["get", "color"],
              "fill-extrusion-height": ["get", "height"],
              "fill-extrusion-base": 0,
              "fill-extrusion-opacity": 0.95
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
