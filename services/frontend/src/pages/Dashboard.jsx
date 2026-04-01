import { useEffect, useState } from "react";
import { usersAPI } from "../services/api";
import Card from "../components/Card";
import UsersChart from "../charts/UsersChart";

export default function Dashboard() {

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Charger les utilisateurs
        const usersRes = await usersAPI.getUsers({ limit: 1000 });
        const users = usersRes.data;

        // Calculer des métriques simples
        const metrics = {
          total_users: users.length,
          users_by_plan: {},
          users_by_gender: {},
          avg_weight: 0,
          avg_height: 0
        };

        // Statistiques par plan
        users.forEach(user => {
          metrics.users_by_plan[user.plan] = (metrics.users_by_plan[user.plan] || 0) + 1;
          metrics.users_by_gender[user.gender] = (metrics.users_by_gender[user.gender] || 0) + 1;

          if (user.weight) metrics.avg_weight += user.weight;
          if (user.height) metrics.avg_height += user.height;
        });

        metrics.avg_weight = users.length > 0 ? (metrics.avg_weight / users.length).toFixed(1) : 0;
        metrics.avg_height = users.length > 0 ? (metrics.avg_height / users.length).toFixed(1) : 0;

        setData(metrics);
        setError(null);
      } catch (err) {
        console.error("Erreur chargement dashboard:", err);
        setError("Failed to load dashboard data");
        setData({
          total_users: 0,
          users_by_plan: {},
          users_by_gender: {},
          avg_weight: 0,
          avg_height: 0
        });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExport = () => {
    if (!data) return;

    const csvContent = [
      ["Metric", "Value"],
      ["Total Users", data.total_users || 0],
      ["Avg Weight (kg)", data.avg_weight || 0],
      ["Avg Height (cm)", data.avg_height || 0],
      ["Export Date", new Date().toISOString()]
    ].map(row => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `health-dashboard-${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p style={{ fontSize: "18px", color: "#666" }}>Loading Dashboard...</p>
    </div>
  );

  if (error) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p style={{ fontSize: "18px", color: "#e74c3c" }}>{error}</p>
    </div>
  );

  return (
    <div style={{ padding: "32px", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
        <div>
          <h1 style={{ margin: "0 0 8px 0", fontSize: "32px", fontWeight: "700", color: "#1a1a1a" }}>
            Dashboard
          </h1>
          <p style={{ margin: "0", color: "#7f8c8d", fontSize: "14px" }}>
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>
        <button 
          onClick={handleExport}
          style={{
            padding: "12px 24px",
            backgroundColor: "#3498db",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: "600",
            transition: "all 0.3s ease",
            boxShadow: "0 2px 6px rgba(52, 152, 219, 0.2)"
          }}
          onMouseOver={(e) => {
            e.target.style.backgroundColor = "#2980b9";
            e.target.style.boxShadow = "0 4px 12px rgba(52, 152, 219, 0.3)";
          }}
          onMouseOut={(e) => {
            e.target.style.backgroundColor = "#3498db";
            e.target.style.boxShadow = "0 2px 6px rgba(52, 152, 219, 0.2)";
          }}
        >
          📊 Export Data (CSV)
        </button>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "20px",
        marginBottom: "32px"
      }}>
        <Card title="Total Users" value={data?.users || 0} />
        <Card title="Avg Calories" value={(data?.avg_calories || 0).toFixed(0)} />
        <Card title="Top Goal" value={data?.top_goal || "—"} />
      </div>

      <div style={{
        background: "white",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
        marginBottom: "32px"
      }}>
        <h2 style={{ margin: "0 0 20px 0", fontSize: "18px", fontWeight: "600", color: "#1a1a1a" }}>
          Users by Age Group
        </h2>
        <UsersChart />
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
        gap: "20px"
      }}>
        <div style={{
          background: "white",
          padding: "20px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
        }}>
          <p style={{ margin: "0", color: "#7f8c8d", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
            Status
          </p>
          <p style={{ margin: "12px 0 0 0", fontSize: "20px", fontWeight: "700", color: "#27ae60" }}>
            ✓ Active
          </p>
        </div>
        <div style={{
          background: "white",
          padding: "20px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
        }}>
          <p style={{ margin: "0", color: "#7f8c8d", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
            System Health
          </p>
          <p style={{ margin: "12px 0 0 0", fontSize: "20px", fontWeight: "700", color: "#2980b9" }}>
            Optimal
          </p>
        </div>
      </div>

    </div>
  );
}