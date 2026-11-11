import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Download } from "lucide-react";
import { api } from "../api";
import { Empty, ErrorBox, Spinner } from "../components/ui";
import { useToast } from "../context/Toast";
import { COLORS, CROPS } from "../util";

export default function Analytics() {
  const toast = useToast();
  const [f, setF] = useState({ date_from: "", date_to: "", crop: "" });
  const [s, setS] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.analytics(f).then((r) => { setS(r); setError(""); }).catch((e) => setError(e.message)); }, [f]);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  return (
    <div>
      <div className="page-head"><h1>Farm analytics</h1><p>Charts use your stored scans only. Filter by date and crop, or export the rows as CSV.</p></div>
      <div className="card row">
        <div><label className="f" htmlFor="df">From</label><input id="df" type="date" value={f.date_from} onChange={set("date_from")} /></div>
        <div><label className="f" htmlFor="dt">To</label><input id="dt" type="date" value={f.date_to} onChange={set("date_to")} /></div>
        <div><label className="f" htmlFor="cr">Crop</label><select id="cr" value={f.crop} onChange={set("crop")}><option value="">All crops</option>{CROPS.map((c) => <option key={c}>{c}</option>)}</select></div>
        <button className="btn ghost" style={{ alignSelf: "end" }} onClick={() => setF({ date_from: "", date_to: "", crop: "" })}>Reset filters</button>
        <button className="btn" style={{ alignSelf: "end" }} onClick={() => api.exportCsv(f).then(() => toast("CSV downloaded", "success")).catch((e) => toast(e.message, "error"))}><Download size={16} />Export CSV</button>
      </div>
      <div style={{ marginTop: "1rem" }}><ErrorBox error={error} />{!s && !error && <Spinner label="Loading" />}</div>
      {s && s.total === 0 && <div className="card"><Empty title="No data for these filters">Scan some leaves first, or widen the filters.</Empty></div>}
      {s && s.total > 0 && (
        <div className="grid g2">
          <div className="card"><h3>Healthy vs diseased</h3>
            <ResponsiveContainer width="100%" height={240}><PieChart><Pie data={[{ name: "Healthy", value: s.healthy }, { name: "Diseased", value: s.diseased }]} dataKey="value" nameKey="name" outerRadius={85} label>
              <Cell fill={COLORS.leaf} /><Cell fill={COLORS.brick} /></Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer></div>
          <div className="card"><h3>By crop</h3>
            <ResponsiveContainer width="100%" height={240}><BarChart data={s.crop_stats}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="crop" /><YAxis allowDecimals={false} /><Tooltip /><Legend />
              <Bar dataKey="healthy" stackId="a" fill={COLORS.leaf} /><Bar dataKey="diseased" stackId="a" fill={COLORS.brick} /></BarChart></ResponsiveContainer></div>
          <div className="card"><h3>Predicted diseases</h3>
            <ResponsiveContainer width="100%" height={260}><BarChart data={s.disease_distribution} layout="vertical" margin={{ left: 40 }}><CartesianGrid horizontal={false} stroke="#e5e9e0" /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="name" width={170} tick={{ fontSize: 12 }} /><Tooltip /><Bar dataKey="count" fill={COLORS.canopy} /></BarChart></ResponsiveContainer></div>
          <div className="card"><h3>Scans per day</h3>
            <ResponsiveContainer width="100%" height={260}><LineChart data={s.scans_per_day}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} /><YAxis allowDecimals={false} /><Tooltip /><Line dataKey="count" stroke={COLORS.sky} strokeWidth={2} /></LineChart></ResponsiveContainer></div>
          <div className="card"><h3>Environmental risk (rule-based) across scans</h3>
            <ResponsiveContainer width="100%" height={240}><BarChart data={s.risk_distribution}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="category" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" fill={COLORS.marigold} /></BarChart></ResponsiveContainer></div>
          <div className="card"><h3>Weather values entered with scans</h3>
            {s.environment_trend.length ? <ResponsiveContainer width="100%" height={240}><LineChart data={s.environment_trend.map((e, i) => ({ ...e, n: i + 1 }))}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="n" /><YAxis /><Tooltip /><Legend />
              <Line dataKey="temperature_c" name="Temp (C)" stroke={COLORS.brick} /><Line dataKey="humidity_pct" name="Humidity (%)" stroke={COLORS.canopy} /></LineChart></ResponsiveContainer>
              : <p className="muted">No scans in this range included weather values.</p>}</div>
          <div className="card"><h3>Satellite index trends</h3><p className="muted">{s.satellite_trend.note}</p></div>
        </div>
      )}
    </div>
  );
}
