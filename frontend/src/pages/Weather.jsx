import { useState } from "react";
import { Bar, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Search } from "lucide-react";
import { api } from "../api";
import { Badge, ErrorBox, Spinner } from "../components/ui";
import { useToast } from "../context/Toast";
import { COLORS, daysAgo } from "../util";

export default function Weather() {
  const toast = useToast();
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [place, setPlace] = useState(null);
  const [w, setW] = useState(null);
  const [hist, setHist] = useState(null);
  const [range, setRange] = useState({ start: daysAgo(35), end: daysAgo(5) });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function search() {
    if (q.trim().length < 2) return;
    setError(""); setBusy(true);
    try { const r = await api.geocode(q.trim()); setResults(r.results); if (!r.results.length) setError("No place found. Try a larger town or add the state."); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function choose(r) {
    setPlace(r); setResults([]); setW(null); setHist(null); setBusy(true); setError("");
    try { setW(await api.weather(r.latitude, r.longitude)); } catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function loadHistory() {
    try { setHist(await api.weatherHistory(place.latitude, place.longitude, range.start, range.end)); } catch (e) { toast(e.message, "error"); }
  }
  const c = w?.current;

  return (
    <div>
      <div className="page-head"><h1>Weather intelligence</h1><p>Measured and forecast weather from Open-Meteo. Soil moisture is a model estimate for the 3 to 9 cm layer and can be missing. The risk label is rule-based context, not a disease diagnosis.</p></div>
      <div className="card">
        <div className="row">
          <input type="text" placeholder="Search a town or village, e.g. Lucknow" value={q} aria-label="Place name" onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && search()} style={{ flex: 1, minWidth: 220 }} />
          <button className="btn" onClick={search} disabled={busy}><Search size={16} />Search</button>
        </div>
        <div className="row" style={{ marginTop: ".6rem" }}>
          {results.map((r) => <button key={`${r.latitude}${r.longitude}`} className="btn ghost sm" onClick={() => choose(r)}>{r.name}, {r.admin1 ? `${r.admin1}, ` : ""}{r.country}</button>)}
        </div>
      </div>
      <div style={{ marginTop: "1rem" }}><ErrorBox error={error} />{busy && <Spinner label="Loading" />}</div>

      {w && (
        <>
          <h2 style={{ marginTop: "1rem" }}>{place.name}: current conditions</h2>
          <div className="grid g4">
            <div className="card"><div className="stat">{c.temperature_c ?? "-"}<span className="small"> C</span></div><div className="stat-label">Temperature</div></div>
            <div className="card"><div className="stat">{c.humidity_pct ?? "-"}<span className="small"> %</span></div><div className="stat-label">Relative humidity</div></div>
            <div className="card"><div className="stat">{w.daily[0]?.precipitation_mm ?? "-"}<span className="small"> mm</span></div><div className="stat-label">Rain forecast today</div></div>
            <div className="card"><div className="stat">{c.soil_moisture != null ? c.soil_moisture.toFixed(2) : "n/a"}</div><div className="stat-label">Soil moisture (m3/m3)</div></div>
          </div>
          {w.current_risk && (
            <section className="panel rule" style={{ marginTop: "1rem" }}>
              <h3>Right now<span className="tag">Rule-based</span></h3>
              <p><Badge kind={w.current_risk.category}>{w.current_risk.category}</Badge> score {w.current_risk.score} of {w.current_risk.max_score}. Wind {c.wind_kmh} km/h.</p>
              <ul>{w.current_risk.factors.map((f) => <li key={f.factor}>{f.explanation}</li>)}</ul>
              {w.current_risk.stress_flags.map((s) => <p key={s} className="small">{s}</p>)}
            </section>
          )}
          <div className="card" style={{ marginTop: "1rem" }}>
            <h2>Seven-day forecast</h2>
            <ResponsiveContainer width="100%" height={280}>
              <ComposedChart data={w.daily}>
                <CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} />
                <YAxis yAxisId="t" unit=" C" /><YAxis yAxisId="r" orientation="right" unit=" mm" /><Tooltip /><Legend />
                <Bar yAxisId="r" dataKey="precipitation_mm" name="Rain (mm)" fill={COLORS.sky} />
                <Line yAxisId="t" dataKey="temp_max" name="Max temp" stroke={COLORS.brick} dot={false} strokeWidth={2} />
                <Line yAxisId="t" dataKey="temp_min" name="Min temp" stroke={COLORS.canopy} dot={false} strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
            <table className="t"><thead><tr><th>Day</th><th>Mean humidity</th><th>Rain</th><th>Rule-based risk</th></tr></thead><tbody>
              {w.daily.map((d) => (
                <tr key={d.date}><td>{d.date}</td><td>{d.humidity_mean != null ? `${d.humidity_mean.toFixed(0)}%` : "-"}</td><td>{d.precipitation_mm ?? "-"} mm</td>
                  <td>{d.risk ? <Badge kind={d.risk.category}>{d.risk.category}</Badge> : "-"}</td></tr>
              ))}
            </tbody></table>
          </div>

          <div className="card" style={{ marginTop: "1rem" }}>
            <h2>Historical weather</h2>
            <div className="row">
              <div><label className="f" htmlFor="hs">From</label><input id="hs" type="date" value={range.start} onChange={(e) => setRange({ ...range, start: e.target.value })} /></div>
              <div><label className="f" htmlFor="he">To</label><input id="he" type="date" value={range.end} onChange={(e) => setRange({ ...range, end: e.target.value })} /></div>
              <button className="btn" style={{ alignSelf: "end" }} onClick={loadHistory}>Load history</button>
            </div>
            <p className="small muted">Up to 92 days, ending at least 2 days ago.</p>
            {hist && (
              <ResponsiveContainer width="100%" height={280}>
                <ComposedChart data={hist.daily}>
                  <CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} />
                  <YAxis yAxisId="t" /><YAxis yAxisId="r" orientation="right" unit=" mm" /><Tooltip /><Legend />
                  <Bar yAxisId="r" dataKey="precipitation_mm" name="Rain (mm)" fill={COLORS.sky} />
                  <Line yAxisId="t" dataKey="temp_mean" name="Mean temp (C)" stroke={COLORS.brick} dot={false} strokeWidth={2} />
                  <Line yAxisId="t" dataKey="humidity_mean" name="Mean humidity (%)" stroke={COLORS.canopy} dot={false} strokeWidth={2} />
                </ComposedChart>
              </ResponsiveContainer>
            )}
          </div>
        </>
      )}
    </div>
  );
}
