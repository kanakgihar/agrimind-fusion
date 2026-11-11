export const pct = (x, d = 1) => (x === null || x === undefined ? "-" : `${(x * 100).toFixed(d)}%`);
export const fmtDate = (iso) => (iso ? new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "-");
export const today = () => new Date().toISOString().slice(0, 10);
export const daysAgo = (n) => new Date(Date.now() - n * 864e5).toISOString().slice(0, 10);
export const COLORS = { canopy: "#1d4a38", leaf: "#4c9a6b", marigold: "#e0a21b", sky: "#2f6e92", brick: "#af3b2e", muted: "#9aa89f" };
export const CROPS = ["Tomato", "Potato", "Pepper"];
