import { useRef, useState } from "react";
import { UploadCloud, Search } from "lucide-react";
import { api } from "../api";
import ScanResult from "../components/ScanResult";
import { ErrorBox, Field, Spinner } from "../components/ui";
import { useToast } from "../context/Toast";
import { CROPS } from "../util";

const EMPTY_ENV = { temperature_c: "", humidity_pct: "", rainfall_mm: "", soil_moisture: "" };

export default function CropDoctor() {
  const toast = useToast();
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [over, setOver] = useState(false);
  const [crop, setCrop] = useState("");
  const [env, setEnv] = useState(EMPTY_ENV);
  const [place, setPlace] = useState({ q: "", results: [], chosen: null, busy: false });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function pick(f) {
    if (!f) return;
    if (!["image/jpeg", "image/png"].includes(f.type)) { toast("Choose a JPEG or PNG image.", "error"); return; }
    if (f.size > 8 * 1024 * 1024) { toast("Image is larger than 8 MB.", "error"); return; }
    setFile(f); setResult(null); setError("");
    setPreview(URL.createObjectURL(f));
  }

  async function searchPlace() {
    if (place.q.trim().length < 2) return;
    setPlace((p) => ({ ...p, busy: true, results: [] }));
    try { const r = await api.geocode(place.q.trim()); setPlace((p) => ({ ...p, results: r.results, busy: false })); if (!r.results.length) toast("No place found.", "error"); }
    catch (e) { toast(e.message, "error"); setPlace((p) => ({ ...p, busy: false })); }
  }

  async function useWeather(r) {
    try {
      const w = await api.weather(r.latitude, r.longitude);
      const c = w.current;
      setEnv({
        temperature_c: c.temperature_c ?? "", humidity_pct: c.humidity_pct ?? "",
        rainfall_mm: w.daily[0]?.precipitation_mm ?? "", soil_moisture: c.soil_moisture != null ? Number(c.soil_moisture.toFixed(3)) : "",
      });
      setPlace((p) => ({ ...p, chosen: r, results: [] }));
      toast(`Filled from Open-Meteo for ${r.name}. Edit any value you know better.`, "success");
    } catch (e) { toast(e.message, "error"); }
  }

  async function submit(e) {
    e.preventDefault();
    if (!file) { setError("Choose a leaf image first."); return; }
    setBusy(true); setError(""); setResult(null);
    const fd = new FormData();
    fd.append("file", file);
    if (crop) fd.append("crop", crop);
    Object.entries(env).forEach(([k, v]) => { if (v !== "") fd.append(k, v); });
    if (place.chosen) { fd.append("latitude", place.chosen.latitude); fd.append("longitude", place.chosen.longitude); }
    try { setResult(await api.predict(fd)); toast("Scan saved to history", "success"); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  const setE = (k) => (e) => setEnv({ ...env, [k]: e.target.value });

  return (
    <div>
      <div className="page-head"><h1>Crop Doctor</h1><p>Upload one clear photo of a single tomato, potato or bell pepper leaf. Weather values are optional and only feed the rule-based risk panel, never the image model.</p></div>
      <form className="split" onSubmit={submit}>
        <div className="card">
          <div className={`drop ${over ? "over" : ""}`} onClick={() => inputRef.current?.click()} role="button" tabIndex={0}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
            onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0]); }}>
            {preview ? <img src={preview} alt="Selected leaf preview" /> : <><UploadCloud size={34} aria-hidden="true" /><p><strong>Drop a leaf photo here</strong> or click to browse</p><p className="small muted">JPEG or PNG, up to 8 MB</p></>}
          </div>
          <input ref={inputRef} type="file" accept="image/jpeg,image/png" hidden onChange={(e) => pick(e.target.files[0])} />
          <div style={{ marginTop: ".8rem" }}>
            <Field label="Crop (optional, used to warn about mismatches)">
              <select value={crop} onChange={(e) => setCrop(e.target.value)}>
                <option value="">Auto (let the model decide)</option>{CROPS.map((c) => <option key={c}>{c}</option>)}
              </select>
            </Field>
          </div>
        </div>

        <div className="card">
          <h3>Weather context (optional)</h3>
          <div className="row" style={{ marginBottom: ".6rem" }}>
            <input type="text" placeholder="Find a place to fetch current weather" value={place.q} aria-label="Place name"
              onChange={(e) => setPlace({ ...place, q: e.target.value })} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), searchPlace())} style={{ flex: 1 }} />
            <button type="button" className="btn ghost" onClick={searchPlace} disabled={place.busy}><Search size={16} />Search</button>
          </div>
          {place.results.map((r) => (
            <div key={`${r.latitude}${r.longitude}`}><button type="button" className="btn ghost sm" style={{ marginBottom: ".3rem" }} onClick={() => useWeather(r)}>{r.name}, {r.admin1 ? `${r.admin1}, ` : ""}{r.country}</button></div>
          ))}
          {place.chosen && <p className="small muted">Weather source: Open-Meteo, {place.chosen.name}. These are model/forecast values for the area, not readings from your field.</p>}
          <div className="grid g2">
            <Field label="Temperature (C)"><input type="number" step="0.1" min="-30" max="60" value={env.temperature_c} onChange={setE("temperature_c")} /></Field>
            <Field label="Humidity (%)"><input type="number" step="1" min="0" max="100" value={env.humidity_pct} onChange={setE("humidity_pct")} /></Field>
            <Field label="Rainfall (mm per day)"><input type="number" step="0.1" min="0" value={env.rainfall_mm} onChange={setE("rainfall_mm")} /></Field>
            <Field label="Soil moisture (m3/m3, 0 to 1)"><input type="number" step="0.01" min="0" max="1" value={env.soil_moisture} onChange={setE("soil_moisture")} /></Field>
          </div>
          <div className="row" style={{ marginTop: "1rem" }}>
            <button className="btn" disabled={busy || !file}>{busy ? "Analysing" : "Analyse leaf"}</button>
            <button type="button" className="btn ghost" onClick={() => setEnv(EMPTY_ENV)}>Clear weather values</button>
            {busy && <Spinner />}
          </div>
        </div>
      </form>
      <div style={{ marginTop: "1rem" }}><ErrorBox error={error} /></div>
      {result && <div style={{ marginTop: "1.2rem" }}><ScanResult key={result.scan_id} data={result} /></div>}
    </div>
  );
}
