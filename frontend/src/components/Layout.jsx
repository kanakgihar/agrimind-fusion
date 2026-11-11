import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { BarChart3, CloudSun, History, Info, Leaf, LayoutDashboard, MessageCircle, Satellite, SlidersHorizontal } from "lucide-react";
import { api } from "../api";

const NAV = [
  ["/", "Dashboard", LayoutDashboard], ["/doctor", "Crop Doctor", Leaf], ["/weather", "Weather", CloudSun],
  ["/simulator", "Risk Simulator", SlidersHorizontal], ["/satellite", "Satellite", Satellite], ["/history", "Scan history", History],
  ["/analytics", "Analytics", BarChart3], ["/assistant", "Assistant", MessageCircle], ["/about", "About and limits", Info],
];

export default function Layout() {
  const [health, setHealth] = useState(null);
  const [down, setDown] = useState(false);
  useEffect(() => { api.health().then(setHealth).catch(() => setDown(true)); }, []);
  return (
    <div className="app">
      <nav className="rail" aria-label="Main">
        <div className="brand">AgriMind Fusion<small>Crop stress detection and decision support</small></div>
        {NAV.map(([to, label, Icon]) => (
          <NavLink key={to} to={to} end={to === "/"}><Icon size={18} aria-hidden="true" />{label}</NavLink>
        ))}
      </nav>
      <main className="main">
        {down && <div className="banner err">Cannot reach the backend. Start it with <code>scripts\run_backend.ps1</code> and reload this page.</div>}
        {health && !health.model_ready && (
          <div className="banner">The disease model has not been trained yet, so predictions are unavailable. Run <code>python scripts/prepare_data.py</code> then <code>python scripts/train.py --model mobilenet</code>. Weather, simulator and assistant already work.</div>
        )}
        <Outlet />
      </main>
    </div>
  );
}
