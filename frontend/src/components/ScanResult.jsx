import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Download, MessageCircle } from "lucide-react";
import { api, fileUrl } from "../api";
import { useToast } from "../context/Toast";
import { pct } from "../util";
import { Badge, Bar, ErrorBox, Spinner } from "./ui";

const SECTIONS = ["Next step", "Management", "Prevention", "Monitoring", "Irrigation", "Environmental precaution"];
const ENV_LABELS = { temperature_c: "Temperature (C)", humidity_pct: "Humidity (%)", rainfall_mm: "Rainfall (mm/day)", soil_moisture: "Soil moisture (m3/m3)" };

/** Original photo with the Grad-CAM overlay revealed from the left as the slider moves. */
export function LeafReveal({ original, overlay }) {
  const [pos, setPos] = useState(55);
  return (
    <div>
      <div className="leaf">
        <img src={fileUrl(original)} alt="Uploaded leaf" />
        {overlay && (
          <>
            <img className="over" style={{ height: "100%", clipPath: `inset(0 ${100 - pos}% 0 0)` }} src={fileUrl(overlay)} alt="Grad-CAM heatmap overlay on the leaf" />
            <div className="edge" style={{ left: `${pos}%` }} />
          </>
        )}
      </div>
      {overlay && (
        <div style={{ marginTop: ".6rem" }}>
          <label className="f" htmlFor="reveal">Slide to reveal where the model looked</label>
          <input id="reveal" type="range" min="0" max="100" value={pos} onChange={(e) => setPos(Number(e.target.value))} />
        </div>
      )}
    </div>
  );
}

export default function ScanResult({ data }) {
  const toast = useToast();
  const [ex, setEx] = useState(data.gradcam_overlay_url ? { overlay_url: data.gradcam_overlay_url, gradcam_info: data.gradcam_info } : null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    let on = true;
    if (!ex) {
      setLoading(true);
      api.explain(data.scan_id).then((r) => on && setEx(r)).catch((e) => on && setErr(e.message)).finally(() => on && setLoading(false));
    }
    return () => { on = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data.scan_id]);

  const rec = data.recommendation;
  const risk = data.risk;
  const env = data.environment;

  async function report() {
    try { await api.downloadReport(data.scan_id); toast("Report downloaded", "success"); } catch (e) { toast(e.message, "error"); }
  }

  return (
    <div>
      <div className="row space" style={{ marginBottom: ".8rem" }}>
        <div>
          <h2 style={{ marginBottom: ".2rem" }}>{data.display_name}</h2>
          <Badge kind={data.is_healthy ? "ok" : "bad"}>{data.is_healthy ? "Healthy per model" : "Disease or pest class predicted"}</Badge>
        </div>
        <div className="row">
          <button className="btn ghost" onClick={report}><Download size={16} />Download PDF report</button>
          <Link className="btn ghost" to={`/assistant?scan=${data.scan_id}`}><MessageCircle size={16} />Ask the assistant</Link>
        </div>
      </div>
      {data.warnings?.map((w) => <div key={w} className="warn">{w}</div>)}

      <div className="split">
        <div>
          {loading && <div className="card"><Spinner label="Computing Grad-CAM (a few seconds on CPU)" /></div>}
          {!loading && <LeafReveal original={data.image_url} overlay={ex?.overlay_url} />}
          <ErrorBox error={err && `Grad-CAM unavailable: ${err}`} />
        </div>
        <div>
          <section className="panel">
            <h3>Prediction<span className="tag">Model output</span></h3>
            <div className="row space"><strong>Confidence score</strong><span>{pct(data.confidence)}</span></div>
            <Bar value={data.confidence} />
            <p className="small muted" style={{ marginTop: ".4rem" }}>{data.note}. Trained only on 15 PlantVillage classes (tomato, potato, bell pepper).</p>
            <h3 style={{ marginTop: ".8rem" }}>Top three</h3>
            {data.top3.map((t) => (
              <div key={t.class} style={{ marginBottom: ".4rem" }}>
                <div className="row space small"><span>{t.display_name}</span><span>{pct(t.confidence)}</span></div>
                <Bar value={t.confidence} />
              </div>
            ))}
          </section>

          <section className="panel">
            <h3>Explanation<span className="tag">Grad-CAM</span></h3>
            {ex?.gradcam_info ? (
              <p>The model paid most attention to the <strong>{ex.gradcam_info.main_region}</strong> area, covering about {ex.gradcam_info.coverage_pct}% of the image. Red areas pushed the score toward this class most. If red sits on the background rather than the leaf, treat the result with suspicion. Grad-CAM shows where the model looked; it does not prove the biological cause.</p>
            ) : <p className="muted">Heatmap not available yet.</p>}
          </section>

          <section className="panel env">
            <h3>Environment you provided<span className="tag">Your inputs</span></h3>
            {env ? (
              <p className="small">{Object.entries(ENV_LABELS).map(([k, label]) => env[k] !== null && env[k] !== undefined && <span key={k}>{label}: <strong>{env[k]}</strong>{"  "}</span>)}</p>
            ) : <p className="muted">No weather values were entered for this scan. They are optional and never change the image prediction.</p>}
          </section>

          {risk && (
            <section className="panel rule">
              <h3>Environmental risk<span className="tag">Rule-based</span></h3>
              <p><Badge kind={risk.category}>{risk.category}</Badge> score {risk.score} of {risk.max_score}. This is a fixed set of rules ({risk.rule_version}), not a trained model.</p>
              <ul>{risk.factors.map((f) => <li key={f.factor}><strong>{f.factor}</strong> (+{f.points}): {f.explanation}</li>)}</ul>
              {risk.stress_flags.map((s) => <p key={s} className="small">{s}</p>)}
            </section>
          )}
        </div>
      </div>

      <section className="panel guide rec">
        <h3>What to do next<span className="tag">General guidance</span></h3>
        <p><Badge kind={rec.urgency}>{`Urgency: ${rec.urgency}`}</Badge> {rec.summary}</p>
        {rec.warnings?.map((w) => <div key={w} className="warn">{w}</div>)}
        {SECTIONS.map((s) => {
          const items = rec.items.filter((i) => i.section === s);
          return items.length ? (
            <div key={s}><h4>{s}</h4>
              <ul>{items.map((i, k) => <li key={k}>{i.text}<span className="src">Based on: {i.source}. Why: {i.why}</span></li>)}</ul>
            </div>
          ) : null;
        })}
        <p className="small muted">{rec.knowledge_source}</p>
      </section>
      <p className="small muted">{rec.disclaimer}</p>
    </div>
  );
}
