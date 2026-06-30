import { Link, useNavigate } from "react-router-dom";

export default function Layout({ children }) {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="flex min-h-screen bg-slate-100">
      <aside className="w-64 bg-emerald-700 text-white p-6 flex flex-col">
        <h1 className="text-2xl font-bold mb-8">
          AI Finance
        </h1>

        <nav className="flex flex-col gap-4 flex-1">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/transactions">Transactions</Link>
          <Link to="/budgets">Budgets</Link>
          <Link to="/advisor">AI Advisor</Link>
        </nav>

        <button
          onClick={logout}
          className="bg-red-600 hover:bg-red-700 rounded-xl py-3 mt-10"
        >
          Logout
        </button>
      </aside>

      <main className="flex-1 p-8">
        {children}
      </main>
    </div>
  );
}