import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import About from "./pages/About";
import Analytics from "./pages/Analytics";
import Assistant from "./pages/Assistant";
import Compare from "./pages/Compare";
import CropDoctor from "./pages/CropDoctor";
import Dashboard from "./pages/Dashboard";
import HistoryPage from "./pages/History";
import SatellitePage from "./pages/Satellite";
import ScanDetail from "./pages/ScanDetail";
import Simulator from "./pages/Simulator";
import Weather from "./pages/Weather";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="doctor" element={<CropDoctor />} />
        <Route path="weather" element={<Weather />} />
        <Route path="simulator" element={<Simulator />} />
        <Route path="satellite" element={<SatellitePage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="scan/:id" element={<ScanDetail />} />
        <Route path="compare" element={<Compare />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<div className="card">Page not found.</div>} />
      </Route>
    </Routes>
  );
}
