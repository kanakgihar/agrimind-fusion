import { useEffect, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { Empty, ErrorBox, Field, Spinner } from "../components/ui";
import { COLORS, daysAgo, today } from "../util";

export default function SatellitePage() {
  const [st, setSt] = useState(null);
  const [f, setF] = useState({ latitude: "26.85", longitude: "80.95", start_date: daysAgo(120), end_date: today(), radius_m: 200, max_cloud_pct: 60 });
  const [place, setPlace] = useState({ q: "", results: [] });
  const [out, setOut] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { api.satelliteStatus().then(setSt).catch((e) => setError(e.message)); }, []);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function search() {
    try { const r = await api.geocode(place.q); setPlace({ ...place, results: r.results }); } catch (e) { setError(e.message); }
  }
  async function run(e) {
    e.preventDefault(); setBusy(true); setError(""); setOut(null);
    try {
      setOut(await api.satelliteIndices({ ...f, latitude: Number(f.latitude), longitude: Number(f.longitude), radius_m: Number(f.radius_m), max_cloud_pct: Number(f.max_cloud_pct) }));
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return (
    <div>
      <div className="page-head"><h1>Satellite crop monitor</h1><p>Sentinel-2 surface reflectance (COPERNICUS/S2_SR_HARMONIZED) through Google Earth Engine, cloud-masked with the SCL band. NDVI and NDMI describe vegetation and moisture of a field area; they are not disease diagnoses. Map layers and field drawing are not built yet.</p></div>
      {st && (
        <div className="card" style={{ marginBottom: "1rem" }}>
          <h3>Connection status</h3>
          <ul>
            <li>earthengine-api installed: <strong>{st.earthengine_api_installed ? "yes" : "no"}</strong></li>
            <li>Cloud project configured (EE_PROJECT): <strong>{st.project_configured ? "yes" : "no"}</strong></li>
            <li>Authentication: {st.auth_mode}</li>
          </ul>
          <p className="small muted">This module is untested by the authors until you configure Earth Engine (see docs/SATELLITE_SETUP.md).</p>
        </div>
      )}
      <form className="card" onSubmit={run}>
        <div className="row" style={{ marginBottom: ".6rem" }}>
          <input type="text" placeholder="Find a place (optional)" aria-label="Place" value={place.q} onChange={(e) => setPlace({ ...place, q: e.target.value })} />
          <button type="button" className="btn ghost" onClick={search}>Search</button>
          {place.results.map((r) => <button type="button" key={`${r.latitude}${r.longitude}`} className="btn ghost sm" onClick={() => { setF({ ...f, latitude: r.latitude, longitude: r.longitude }); setPlace({ q: "", results: [] }); }}>{r.name}, {r.country}</button>)}
        </div>
        <div className="grid g3">
          <Field label="Latitude"><input type="number" step="any" value={f.latitude} onChange={set("latitude")} required /></Field>
          <Field label="Longitude"><input type="number" step="any" value={f.longitude} onChange={set("longitude")} required /></Field>
          <Field label="Field radius (m)"><input type="number" min="30" max="2000" value={f.radius_m} onChange={set("radius_m")} /></Field>
          <Field label="From"><input type="date" value={f.start_date} onChange={set("start_date")} required /></Field>
          <Field label="To"><input type="date" value={f.end_date} onChange={set("end_date")} required /></Field>
          <Field label="Max cloud cover (%)"><input type="number" min="0" max="100" value={f.max_cloud_pct} onChange={set("max_cloud_pct")} /></Field>
        </div>
        <div className="row" style={{ marginTop: "1rem" }}><button className="btn" disabled={busy}>Get NDVI and NDMI</button>{busy && <Spinner label="Querying Earth Engine" />}</div>
      </form>
      <div style={{ marginTop: "1rem" }}><ErrorBox error={error} /></div>
      {out && out.count === 0 && <div className="card"><Empty title="No usable imagery">{out.message}</Empty></div>}
      {out && out.count > 0 && (
        <div className="card">
          <h2>{out.count} cloud-masked observations</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={out.observations}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} /><YAxis domain={[-0.2, 1]} /><Tooltip /><Legend />
              <Line dataKey="ndvi" name="NDVI" stroke={COLORS.canopy} strokeWidth={2} /><Line dataKey="ndmi" name="NDMI" stroke={COLORS.sky} strokeWidth={2} /></LineChart>
          </ResponsiveContainer>
          <table className="t"><thead><tr><th>Date</th><th>Scene cloud %</th><th>NDVI</th><th>NDMI</th></tr></thead><tbody>
            {out.observations.map((o) => <tr key={o.date}><td>{o.date}</td><td>{Number(o.cloud_pct).toFixed(0)}</td><td>{o.ndvi?.toFixed(3)}</td><td>{o.ndmi?.toFixed(3)}</td></tr>)}
          </tbody></table>
          <p className="small muted">Legend: NDVI near 0 means bare soil or very sparse vegetation; values above about 0.6 usually mean dense green vegetation. NDMI is higher when canopy water content is higher. {out.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
