import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        background: "linear-gradient(135deg, #f5f6fa 0%, #f8f9fa 100%)"
      }}>
        <header style={{
          background: "white",
          padding: "16px 32px",
          boxShadow: "0 2px 4px rgba(0, 0, 0, 0.06)",
          borderBottom: "1px solid rgba(0, 0, 0, 0.05)"
        }}>
          <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
            <p style={{ margin: "0", color: "#7f8c8d", fontSize: "12px" }}>
              HealthAI Platform
            </p>
          </div>
        </header>
        <main style={{
          flex: 1,
          overflow: "auto"
        }}>
          {children}
        </main>
      </div>
    </div>
  );
}