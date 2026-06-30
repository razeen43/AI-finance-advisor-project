import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div style={{
      padding: "15px 25px",
      background: "#0F6E56",
      display: "flex",
      gap: "20px"
    }}>
      <Link style={{ color: "white" }} to="/dashboard">Dashboard</Link>
      <Link style={{ color: "white" }} to="/transactions">Transactions</Link>
      <Link style={{ color: "white" }} to="/advisor">AI Advisor</Link>
    </div>
  );
}