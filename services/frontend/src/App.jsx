import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Exercises from "./pages/Exercises";
import Nutrition from "./pages/Nutrition";
import DataQuality from "./pages/DataQuality";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/users" element={<Users />} />
          <Route path="/exercises" element={<Exercises />} />
          <Route path="/nutrition" element={<Nutrition />} />
          <Route path="/data-quality" element={<DataQuality />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}