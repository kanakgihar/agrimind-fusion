// One place for every backend call. Endpoints match backend/app/routes/*.
const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export function sessionId() {
  let id = null;
  try { id = localStorage.getItem("agrimind_session"); } catch { /* storage blocked */ }
  if (!id) {
    id = (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2)).replace(/[^A-Za-z0-9_-]/g, "");
    try { localStorage.setItem("agrimind_session", id); } catch { /* ignore */ }
  }
  return id;
}

export const fileUrl = (p) => (p ? BASE + p : null);

async function req(path, { method = "GET", json, form, raw } = {}) {
  const headers = { "X-Session-Id": sessionId() };
  let body;
  if (json !== undefined) { headers["Content-Type"] = "application/json"; body = JSON.stringify(json); }
  if (form) body = form;
  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body });
  } catch {
    throw new Error("Cannot reach the backend. Is it running on port 8000?");
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const d = await res.json();
      if (typeof d.detail === "string") msg = d.detail;
      else if (Array.isArray(d.detail)) msg = d.detail.map((x) => `${(x.loc || []).slice(1).join(".")}: ${x.msg}`).join("; ");
    } catch { /* not json */ }
    throw new Error(msg);
  }
  if (raw) return res;
  if (res.status === 204) return null;
  return res.json();
}

const qs = (o) => {
  const p = new URLSearchParams();
  Object.entries(o || {}).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== "") p.set(k, v); });
  const s = p.toString();
  return s ? `?${s}` : "";
};

async function download(path, filename) {
  const res = await req(path, { raw: true });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export const api = {
  health: () => req("/api/health"),
  predict: (form) => req("/api/predict", { method: "POST", form }),
  explain: (id) => req(`/api/explain/${id}`),
  scans: (params) => req(`/api/scans${qs(params)}`),
  scan: (id) => req(`/api/scans/${id}`),
  deleteScan: (id) => req(`/api/scans/${id}`, { method: "DELETE" }),
  geocode: (q) => req(`/api/weather/geocode${qs({ q })}`),
  weather: (lat, lon) => req(`/api/weather${qs({ lat, lon })}`),
  weatherHistory: (lat, lon, start, end) => req(`/api/weather/history${qs({ lat, lon, start, end })}`),
  simulate: (baseline, scenario) => req("/api/simulator", { method: "POST", json: { baseline, scenario } }),
  analytics: (params) => req(`/api/analytics/summary${qs(params)}`),
  exportCsv: (params) => download(`/api/analytics/export${qs(params)}`, "agrimind_scans.csv"),
  chat: (body) => req("/api/chat", { method: "POST", json: body }),
  satelliteStatus: () => req("/api/satellite/status"),
  satelliteIndices: (body) => req("/api/satellite/indices", { method: "POST", json: body }),
  downloadReport: (id) => download(`/api/reports/${id}`, `agrimind_scan_${id}.pdf`),
};
