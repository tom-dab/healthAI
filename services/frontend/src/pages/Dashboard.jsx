import { useEffect, useState } from "react";
import { getMetrics } from "../services/api";
import Card from "../components/Card";
import UsersChart from "../charts/UsersChart";

export default function Dashboard() {

  const [metrics, setMetrics] = null;

  const [data, setData] = useState(null);

  useEffect(() => {
    getMetrics()
      .then(res => setData(res.data))
      .catch(() => setData({}));
  }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div>

      <h1>Dashboard</h1>

      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <Card title="Users" value={data.users} />
        <Card title="Avg Calories" value={data.avg_calories} />
        <Card title="Top Goal" value={data.top_goal} />
      </div>

      <div style={{
        background: "#fff",
        padding: "20px",
        borderRadius: "10px"
      }}>
        <UsersChart />
      </div>

    </div>
  );
}