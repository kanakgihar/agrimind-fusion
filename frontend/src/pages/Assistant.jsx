import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { ErrorBox } from "../components/ui";

const IDEAS = ["What is NDVI?", "Explain Grad-CAM", "How sure is the model?", "How do I prevent it?", "What should I do?", "How reliable is this on field photos?"];

export default function Assistant() {
  const [sp] = useSearchParams();
  const [scans, setScans] = useState([]);
  const [scanId, setScanId] = useState(sp.get("scan") || "");
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "Hi. I answer from this project's knowledge base (15 crop classes, Grad-CAM, weather rules, NDVI and NDMI). I run in rule-based mode and cannot answer outside that. Pick a scan for follow-up questions." }]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const end = useRef(null);
  useEffect(() => { api.scans({ limit: 30 }).then((r) => setScans(r.items)).catch(() => {}); }, []);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  async function send(message) {
    const m = (message ?? text).trim();
    if (!m || busy) return;
    const history = msgs.slice(-10);
    setMsgs((x) => [...x, { role: "user", content: m }]); setText(""); setBusy(true); setError("");
    try {
      const r = await api.chat({ message: m, scan_id: scanId ? Number(scanId) : null, history });
      setMsgs((x) => [...x, { role: "assistant", content: r.reply }]);
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  return (
    <div>
      <div className="page-head"><h1>AgriAI assistant</h1><p>Rule-based helper. It will say so when it does not know something, and it never promises outcomes.</p></div>
      <div className="card">
        <label className="f" htmlFor="sc">Scan context</label>
        <select id="sc" value={scanId} onChange={(e) => setScanId(e.target.value)} style={{ maxWidth: 420 }}>
          <option value="">No scan selected</option>
          {scans.map((s) => <option key={s.scan_id} value={s.scan_id}>#{s.scan_id} {s.display_name}</option>)}
        </select>
        <div className="chat" aria-live="polite" style={{ marginTop: ".8rem" }}>
          {msgs.map((m, i) => <div key={i} className={`msg ${m.role === "user" ? "user" : "bot"}`}>{m.content}</div>)}
          {busy && <div className="msg bot">Thinking...</div>}
          <div ref={end} />
        </div>
        <ErrorBox error={error} />
        <div className="row" style={{ margin: ".6rem 0" }}>{IDEAS.map((i) => <button key={i} className="btn ghost sm" onClick={() => send(i)}>{i}</button>)}</div>
        <form className="row" onSubmit={(e) => { e.preventDefault(); send(); }}>
          <input type="text" aria-label="Your question" placeholder="Ask about a disease, Grad-CAM, weather risk, NDVI..." value={text} onChange={(e) => setText(e.target.value)} maxLength={1000} style={{ flex: 1 }} />
          <button className="btn" disabled={busy || !text.trim()}>Send</button>
        </form>
      </div>
    </div>
  );
}
