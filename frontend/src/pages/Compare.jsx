import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, fileUrl } from "../api";
import { Bar, ErrorBox, Spinner } from "../components/ui";
import { fmtDate, pct } from "../util";

function Side({ s, ex }) {
  return (
    <div className="card">
      <h2>{s.display_name}</h2>
      <p className="small muted">Scan {s.scan_id}, {fmtDate(s.created_at)}</p>
      <div className="grid g2">
        <figure style={{ margin: 0 }}><img style={{ width: "100%", borderRadius: 8 }} src={fileUrl(s.image_url)} alt="Original leaf" /><figcaption className="small muted">Original</figcaption></figure>
        <figure style={{ margin: 0 }}>{ex ? <img style={{ width: "100%", borderRadius: 8 }} src={fileUrl(ex.overlay_url)} alt="Grad-CAM overlay" /> : <p className="muted small">Grad-CAM unavailable</p>}<figcaption className="small muted">Grad-CAM</figcaption></figure>
      </div>
      <p>Confidence {pct(s.confidence)}</p><Bar value={s.confidence} />
      <p className="small">Crop: {s.crop}. Risk: {s.risk ? `${s.risk.category} (rule-based)` : "no weather data"}. Urgency: {s.recommendation.urgency}.</p>
    </div>
  );
}

export default function Compare() {
  const [sp] = useSearchParams();
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const ids = [sp.get("a"), sp.get("b")];
    if (ids.some((x) => !x)) { setError("Pick two scans in Scan history first."); return; }
    Promise.all(ids.map(async (id) => {
      const s = await api.scan(id);
      const ex = await api.explain(id).catch(() => null);
      return { s, ex };
    })).then(setItems).catch((e) => setError(e.message));
  }, [sp]);
  return (
    <div>
      <p><Link to="/history">Back to scan history</Link></p>
      <div className="page-head"><h1>Compare scans</h1><p>These are two separate images. Differences are not evidence of disease progression unless both photos show the same plant and you know the dates.</p></div>
      <ErrorBox error={error} />
      {!items && !error && <Spinner label="Loading both scans (Grad-CAM may take a few seconds)" />}
      {items && (
        <>
          <div className="grid g2">{items.map(({ s, ex }) => <Side key={s.scan_id} s={s} ex={ex} />)}</div>
          <div className="card" style={{ marginTop: "1rem" }}>
            <h3>Summary</h3>
            <p>{items[0].s.predicted_class === items[1].s.predicted_class ? "Both scans received the same predicted class." : "The two scans received different predicted classes."} Confidence differs by {pct(Math.abs(items[0].s.confidence - items[1].s.confidence))} points.</p>
            <p className="small muted">Satellite index comparison across dates is not available yet; see the Satellite page.</p>
          </div>
        </>
      )}
    </div>
  );
}
