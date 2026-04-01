import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Exercises from "./pages/Exercises";
import Nutrition from "./pages/Nutrition";
import DataQuality from "./pages/DataQuality";
import Account from "./pages/Account";
import Login from "./pages/Login";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RequireAuth><Layout><Dashboard /></Layout></RequireAuth>} />
        <Route path="/users" element={<RequireAuth><Layout><Users /></Layout></RequireAuth>} />
        <Route path="/exercises" element={<RequireAuth><Layout><Exercises /></Layout></RequireAuth>} />
        <Route path="/nutrition" element={<RequireAuth><Layout><Nutrition /></Layout></RequireAuth>} />
        <Route path="/data-quality" element={<RequireAuth><Layout><DataQuality /></Layout></RequireAuth>} />
        <Route path="/account" element={<RequireAuth><Layout><Account /></Layout></RequireAuth>} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}