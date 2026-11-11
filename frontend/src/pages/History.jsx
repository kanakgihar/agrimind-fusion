import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GitCompare, Trash2 } from "lucide-react";
import { api, fileUrl } from "../api";
import { Badge, Confirm, Empty, ErrorBox, Spinner } from "../components/ui";
import { useToast } from "../context/Toast";
import { CROPS, fmtDate, pct } from "../util";

export default function HistoryPage() {
  const toast = useToast();
  const nav = useNavigate();
  const [f, setF] = useState({ q: "", crop: "", status: "", sort: "date_desc" });
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [sel, setSel] = useState([]);
  const [del, setDel] = useState(null);

  const load = useCallback(() => {
    api.scans({ ...f, limit: 100 }).then((r) => { setData(r); setError(""); }).catch((e) => setError(e.message));
  }, [f]);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);

  const toggle = (id) => setSel((s) => (s.includes(id) ? s.filter((x) => x !== id) : s.length >= 2 ? [s[1], id] : [...s, id]));
  async function remove() {
    try { await api.deleteScan(del); toast("Scan deleted", "success"); setSel((s) => s.filter((x) => x !== del)); setDel(null); load(); }
    catch (e) { toast(e.message, "error"); setDel(null); }
  }
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  return (
    <div>
      <div className="page-head"><h1>Scan history</h1><p>Search, filter and open past scans. Tick two scans to compare them side by side.</p></div>
      <div className="card">
        <div className="grid g4">
          <input type="text" placeholder="Search disease or file name" aria-label="Search" value={f.q} onChange={set("q")} />
          <select aria-label="Crop" value={f.crop} onChange={set("crop")}><option value="">All crops</option>{CROPS.map((c) => <option key={c}>{c}</option>)}</select>
          <select aria-label="Status" value={f.status} onChange={set("status")}><option value="">Healthy and diseased</option><option value="healthy">Healthy only</option><option value="diseased">Diseased only</option></select>
          <select aria-label="Sort" value={f.sort} onChange={set("sort")}><option value="date_desc">Newest first</option><option value="date_asc">Oldest first</option><option value="conf_desc">Highest confidence</option><option value="conf_asc">Lowest confidence</option></select>
        </div>
      </div>
      <div className="row" style={{ margin: "1rem 0" }}>
        <button className="btn" disabled={sel.length !== 2} onClick={() => nav(`/compare?a=${sel[0]}&b=${sel[1]}`)}><GitCompare size={16} />Compare selected ({sel.length}/2)</button>
      </div>
      <ErrorBox error={error} />
      {!data && !error && <Spinner label="Loading" />}
      {data && data.items.length === 0 && <div className="card"><Empty title="No scans match">{data.total === 0 ? <>Start with <Link to="/doctor">Crop Doctor</Link>.</> : "Change the filters."}</Empty></div>}
      {data && data.items.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table className="t">
            <thead><tr><th>Pick</th><th>Image</th><th>Prediction</th><th>Confidence</th><th>Risk</th><th>Date</th><th>Delete</th></tr></thead>
            <tbody>
              {data.items.map((s) => (
                <tr key={s.scan_id}>
                  <td><input type="checkbox" aria-label={`Select scan ${s.scan_id}`} checked={sel.includes(s.scan_id)} onChange={() => toggle(s.scan_id)} /></td>
                  <td><img src={fileUrl(s.image_url)} alt="" /></td>
                  <td><Link to={`/scan/${s.scan_id}`}>{s.display_name}</Link> <Badge kind={s.is_healthy ? "ok" : "bad"}>{s.is_healthy ? "healthy" : "diseased"}</Badge></td>
                  <td>{pct(s.confidence)}</td>
                  <td>{s.risk_category ? <Badge kind={s.risk_category}>{s.risk_category}</Badge> : <span className="muted">none</span>}</td>
                  <td>{fmtDate(s.created_at)}</td>
                  <td><button className="btn ghost sm" aria-label={`Delete scan ${s.scan_id}`} onClick={() => setDel(s.scan_id)}><Trash2 size={14} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="small muted">{data.total} scan(s) in total</p>
        </div>
      )}
      {del && <Confirm title="Delete this scan?" text="The image, Grad-CAM files and record are removed permanently." onConfirm={remove} onCancel={() => setDel(null)} />}
    </div>
  );
}
