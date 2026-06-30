import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import {
  FaWallet,
  FaReceipt,
  FaExclamationTriangle,
  FaBrain,
  FaFileDownload
} from "react-icons/fa";
import api from "../api/client";

const COLORS = ["#0F6E56", "#1D9E75", "#BA7517", "#E24B4A", "#8884d8"];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [insights, setInsights] = useState(null);
  const [healthScore, setHealthScore] = useState(null);

  useEffect(() => {
    fetchSummary();
    fetchAnomalies();
    fetchInsights();
    fetchHealthScore();
  }, []);

  const fetchSummary = async () => {
    const res = await api.get("/transactions/summary");
    setSummary(res.data);
  };

  const fetchAnomalies = async () => {
    const res = await api.get("/transactions/anomalies");
    setAnomalies(res.data);
  };

  const fetchInsights = async () => {
    const res = await api.get("/insights");
    setInsights(res.data);
  };

  const fetchHealthScore = async () => {
    const res = await api.get("/health-score/");
    setHealthScore(res.data);
  };

  const downloadReport = async () => {
    const res = await api.get("/reports/monthly", {
      responseType: "blob"
    });

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");

    link.href = url;
    link.setAttribute("download", "AI_Finance_Monthly_Report.pdf");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  if (!summary || !insights || !healthScore) {
    return <h2 className="text-xl font-semibold">Loading...</h2>;
  }

  const chartData = Object.entries(summary.by_category).map(([category, amount]) => ({
    name: category,
    value: amount,
  }));

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            AI Finance Advisor
          </h1>
          <p className="text-slate-500 mt-1">
            Smart insights powered by ML, RAG, and budget analytics.
          </p>
        </div>

        <button
          onClick={downloadReport}
          className="bg-emerald-700 text-white px-5 py-3 rounded-xl font-semibold hover:bg-emerald-800 flex items-center gap-2"
        >
          <FaFileDownload />
          Download AI Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <Card icon={<FaWallet />} title="Total Spending" value={`₹${summary.total_spent}`} />
        <Card icon={<FaReceipt />} title="Transactions" value={summary.count} />
        <Card icon={<FaExclamationTriangle />} title="Anomalies" value={summary.anomalies_count} danger />
        <Card icon={<FaBrain />} title="Health Score" value={`${healthScore.score}/100`} />
      </div>

      <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5">
          <div>
            <h2 className="text-xl font-bold">Financial Health Score</h2>
            <p className="text-slate-500 mt-1">
              Overall financial status based on budgets, anomalies, and spending behavior.
            </p>
          </div>

          <div className="text-center">
            <div className="text-5xl font-bold text-emerald-700">
              {healthScore.score}
            </div>
            <p className="font-semibold text-slate-700">{healthScore.status}</p>
          </div>
        </div>

        <div className="mt-5 w-full bg-slate-100 rounded-full h-4 overflow-hidden">
          <div
            className={`h-full ${
              healthScore.score >= 70
                ? "bg-emerald-600"
                : healthScore.score >= 50
                ? "bg-amber-500"
                : "bg-red-500"
            }`}
            style={{ width: `${healthScore.score}%` }}
          ></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
          <div>
            <h3 className="font-bold mb-2">Reasons</h3>
            <ul className="space-y-2">
              {healthScore.reasons.map((r, index) => (
                <li key={index} className="bg-slate-50 p-3 rounded-xl text-slate-700">
                  {r}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-bold mb-2">Health Recommendations</h3>
            <ul className="space-y-2">
              {healthScore.recommendations.map((r, index) => (
                <li key={index} className="bg-emerald-50 p-3 rounded-xl text-emerald-800">
                  {r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold mb-4">Category Breakdown</h2>

          <PieChart width={520} height={320}>
            <Pie data={chartData} dataKey="value" outerRadius={110} label>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </section>

        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold mb-4">AI Financial Insights</h2>

          <div className="space-y-4">
            <Insight label="Total Spending" value={`₹${insights.total_spent}`} />
            <Insight
              label="Highest Spending Category"
              value={`${insights.top_category.name} — ₹${insights.top_category.amount}`}
            />
            <Insight
              label="Highest Merchant"
              value={`${insights.top_merchant.name} — ₹${insights.top_merchant.amount}`}
            />
          </div>
        </section>
      </div>

      <section className="bg-amber-50 rounded-2xl border border-amber-200 p-6">
        <h2 className="text-xl font-bold text-amber-800 mb-4">Budget Alerts</h2>

        {insights.budget_alerts.length === 0 ? (
          <p className="text-slate-600">No budget alerts.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {insights.budget_alerts.map((alert, index) => (
              <div key={index} className="bg-white p-4 rounded-xl border border-amber-200">
                <h3 className="font-bold">{alert.category}</h3>
                <p>Budget: ₹{alert.limit}</p>
                <p>Spent: ₹{alert.spent}</p>
                <p className="text-red-600 font-semibold">Exceeded by ₹{alert.over_by}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="bg-red-50 rounded-2xl border border-red-200 p-6">
        <h2 className="text-xl font-bold text-red-700 mb-4">ML Anomaly Detection</h2>

        {anomalies.length === 0 ? (
          <p className="text-slate-600">No anomalies detected.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {anomalies.map((a) => (
              <div key={a._id} className="bg-white p-4 rounded-xl border border-red-200">
                <h3 className="font-bold">{a.merchant}</h3>
                <p>Amount: ₹{a.amount}</p>
                <p className="text-slate-600 text-sm mt-2">{a.anomaly_reason}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="bg-emerald-50 rounded-2xl border border-emerald-200 p-6">
        <h2 className="text-xl font-bold text-emerald-800 mb-4">AI Recommendations</h2>

        <ul className="space-y-2">
          {insights.recommendations.map((r, index) => (
            <li key={index} className="bg-white p-3 rounded-xl border border-emerald-100">
              {r}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function Card({ icon, title, value, danger }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
      <div className={`${danger ? "text-red-600" : "text-emerald-700"} text-2xl mb-3`}>
        {icon}
      </div>
      <p className="text-slate-500 text-sm">{title}</p>
      <h2 className="text-2xl font-bold text-slate-900 mt-1">{value}</h2>
    </div>
  );
}

function Insight({ label, value }) {
  return (
    <div className="border-b border-slate-100 pb-3">
      <p className="text-slate-500 text-sm">{label}</p>
      <p className="font-bold text-slate-900">{value}</p>
    </div>
  );
}