import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar as RBar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, fileUrl } from "../api";
import { Empty, ErrorBox, Spinner } from "../components/ui";
import { COLORS, fmtDate, pct } from "../util";

export default function Dashboard() {
  const [s, setS] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.analytics().then(setS).catch((e) => setError(e.message)); }, []);
  if (error) return <ErrorBox error={error} />;
  if (!s) return <Spinner label="Loading dashboard" />;
  const lastEnv = s.environment_trend[s.environment_trend.length - 1];

  return (
    <div>
      <div className="page-head"><h1>Field overview</h1><p>Everything here is computed from the scans stored in your database. Nothing on this page is sample data.</p></div>
      <div className="grid g4">
        <div className="card"><div className="stat">{s.total}</div><div className="stat-label">Leaf scans</div></div>
        <div className="card"><div className="stat">{s.healthy}</div><div className="stat-label">Predicted healthy</div></div>
        <div className="card"><div className="stat">{s.diseased}</div><div className="stat-label">Disease or pest predicted</div></div>
        <div className="card"><div className="stat">{s.avg_confidence == null ? "-" : pct(s.avg_confidence, 0)}</div><div className="stat-label">Average model confidence</div></div>
      </div>

      {s.alerts.length > 0 && (
        <div className="card" style={{ marginTop: "1rem", borderLeft: `5px solid ${COLORS.brick}` }}>
          <h3>Alerts</h3>
          <ul>{s.alerts.map((a) => <li key={a.scan_id}><Link to={`/scan/${a.scan_id}`}>{a.message}</Link></li>)}</ul>
        </div>
      )}

      {s.total === 0 ? (
        <div className="card" style={{ marginTop: "1rem" }}>
          <Empty title="No scans yet">Upload your first leaf photo in <Link to="/doctor">Crop Doctor</Link>. Charts and history will appear here.</Empty>
        </div>
      ) : (
        <div className="grid g2" style={{ marginTop: "1rem" }}>
          <div className="card">
            <h2>Predicted diseases</h2>
            {s.disease_distribution.length ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={s.disease_distribution} layout="vertical" margin={{ left: 40 }}>
                  <CartesianGrid horizontal={false} stroke="#e5e9e0" /><XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={170} tick={{ fontSize: 12 }} /><Tooltip />
                  <RBar dataKey="count" fill={COLORS.canopy} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="muted">Every scan so far was predicted healthy.</p>}
          </div>
          <div className="card">
            <h2>Recent scans</h2>
            <table className="t"><tbody>
              {s.recent.map((r) => (
                <tr key={r.scan_id}>
                  <td><img src={fileUrl(r.image_url)} alt="" /></td>
                  <td><Link to={`/scan/${r.scan_id}`}>{r.display_name}</Link><div className="small muted">{fmtDate(r.created_at)}</div></td>
                  <td>{pct(r.confidence, 0)}</td>
                </tr>
              ))}
            </tbody></table>
          </div>
        </div>
      )}

      <div className="grid g3" style={{ marginTop: "1rem" }}>
        <div className="card"><h3>Latest environment from your scans</h3>
          {lastEnv ? <p>{lastEnv.temperature_c ?? "-"} C, {lastEnv.humidity_pct ?? "-"}% humidity, rule-based score {lastEnv.score}. <Link to="/weather">Open live weather</Link></p>
            : <p className="muted">No scan included weather values yet. <Link to="/weather">Check live weather</Link></p>}</div>
        <div className="card"><h3>Satellite monitoring</h3><p className="muted">Sentinel-2 NDVI and NDMI are available once Earth Engine is configured. <Link to="/satellite">Check status</Link></p></div>
        <div className="card"><h3>Quick actions</h3><div className="row"><Link className="btn sm" to="/doctor">New scan</Link><Link className="btn ghost sm" to="/simulator">Risk simulator</Link><Link className="btn ghost sm" to="/assistant">Ask assistant</Link></div></div>
      </div>
    </div>
  );
}
