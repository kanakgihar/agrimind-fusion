import { useEffect, useRef, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { Badge, ErrorBox } from "../components/ui";
import { COLORS } from "../util";

const BASE = { temperature_c: 26, humidity_pct: 60, rainfall_mm: 0, soil_moisture: 0.25 };
const CONTROLS = [
  ["temperature_c", "Temperature (C)", -5, 50, 0.5], ["humidity_pct", "Relative humidity (%)", 0, 100, 1],
  ["rainfall_mm", "Rainfall (mm per day)", 0, 100, 0.5], ["soil_moisture", "Soil moisture (m3/m3)", 0, 0.6, 0.01],
];

export default function Simulator() {
  const [scenario, setScenario] = useState(BASE);
  const [out, setOut] = useState(null);
  const [error, setError] = useState("");
  const t = useRef(null);

  useEffect(() => {
    clearTimeout(t.current);
    t.current = setTimeout(() => {
      api.simulate(BASE, scenario).then((r) => { setOut(r); setError(""); }).catch((e) => setError(e.message));
    }, 200);
    return () => clearTimeout(t.current);
  }, [scenario]);

  return (
    <div>
      <div className="page-head"><h1>What-if risk simulator</h1><p>Move the sliders to see how the rule-based environmental risk changes against a baseline (26 C, 60% humidity, no rain, moderate soil moisture). This simulates the rules only. It does not re-run the image model or predict disease.</p></div>
      <div className="split">
        <div className="card">
          {CONTROLS.map(([k, label, min, max, step]) => (
            <div key={k} style={{ marginBottom: "1rem" }}>
              <div className="row space"><label className="f" htmlFor={k}>{label}</label><strong>{scenario[k]}</strong></div>
              <input id={k} type="range" min={min} max={max} step={step} value={scenario[k]} onChange={(e) => setScenario({ ...scenario, [k]: Number(e.target.value) })} />
              <div className="small muted">Baseline: {BASE[k]}</div>
            </div>
          ))}
          <button className="btn ghost" onClick={() => setScenario(BASE)}>Reset scenario</button>
        </div>
        <div>
          <ErrorBox error={error} />
          {out && (
            <>
              <section className="panel rule">
                <h3>Result<span className="tag">Rule-based simulation</span></h3>
                <p>Baseline <Badge kind={out.baseline.category}>{out.baseline.category}</Badge> ({out.baseline.score}) to scenario <Badge kind={out.scenario.category}>{out.scenario.category}</Badge> ({out.scenario.score})</p>
                <p>{out.summary}</p>
              </section>
              <div className="card">
                <h3>Points per factor</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={out.factor_changes}><CartesianGrid stroke="#e5e9e0" /><XAxis dataKey="factor" /><YAxis allowDecimals={false} domain={[0, 2]} /><Tooltip /><Legend />
                    <Bar dataKey="baseline_points" name="Baseline" fill={COLORS.muted} /><Bar dataKey="scenario_points" name="Scenario" fill={COLORS.marigold} />
                  </BarChart>
                </ResponsiveContainer>
                <h3>Why</h3>
                <ul>{out.scenario.factors.map((f) => <li key={f.factor}>{f.explanation}</li>)}</ul>
                {out.scenario.stress_flags.map((s) => <p key={s} className="small">{s}</p>)}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
