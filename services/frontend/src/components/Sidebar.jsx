import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div style={{
      width: "240px",
      background: "#1e293b",
      color: "#fff",
      padding: "20px",
      height: "100vh"
    }}>
      <h2>HealthAI</h2>

      <nav style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <Link to="/">Dashboard</Link>
        <Link to="/users">Users</Link>
        <Link to="/exercises">Exercises</Link>
        <Link to="/nutrition">Nutrition</Link>
        <Link to="/data-quality">Data Quality</Link>
      </nav>
    </div>
  );
}