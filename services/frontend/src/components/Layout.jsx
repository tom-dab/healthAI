import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <div style={{
        flex: 1,
        padding: "20px",
        background: "#f4f6f9",
        minHeight: "100vh"
      }}>
        {children}
      </div>
    </div>
  );
}