import { useEffect, useState } from "react";
import { FaWallet, FaSave } from "react-icons/fa";
import api from "../api/client";

const categories = [
  "Food",
  "Transport",
  "Shopping",
  "Entertainment",
  "Utilities",
  "Health",
  "Education",
  "Other"
];

export default function Budgets() {
  const [budgets, setBudgets] = useState([]);
  const [category, setCategory] = useState("Food");
  const [monthlyLimit, setMonthlyLimit] = useState("");

  const fetchBudgets = async () => {
    const res = await api.get("/budgets/");
    setBudgets(res.data);
  };

  useEffect(() => {
    fetchBudgets();
  }, []);

  const saveBudget = async (e) => {
    e.preventDefault();

    await api.post("/budgets/", {
      category,
      monthly_limit: Number(monthlyLimit)
    });

    setMonthlyLimit("");
    fetchBudgets();
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Monthly Budgets</h1>
        <p className="text-slate-500 mt-1">
          Set monthly limits and track how much you have used.
        </p>
      </div>

      <form
        onSubmit={saveBudget}
        className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        >
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Monthly limit"
          value={monthlyLimit}
          onChange={(e) => setMonthlyLimit(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        />

        <button
          type="submit"
          className="bg-emerald-700 text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-emerald-800"
        >
          <FaSave />
          Save Budget
        </button>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {budgets.map((b) => {
          const percent = Math.min(b.percent_used, 100);
          const isOver = b.percent_used > 100;

          return (
            <div
              key={b._id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-slate-900">
                    {b.category}
                  </h3>
                  <p className="text-slate-500 text-sm">Monthly budget</p>
                </div>

                <div
                  className={`text-2xl ${
                    isOver ? "text-red-600" : "text-emerald-700"
                  }`}
                >
                  <FaWallet />
                </div>
              </div>

              <div className="mt-5">
                <p className="text-2xl font-bold text-slate-900">
                  ₹{b.current_spend} / ₹{b.monthly_limit}
                </p>

                <p
                  className={`mt-1 text-sm font-semibold ${
                    isOver ? "text-red-600" : "text-emerald-700"
                  }`}
                >
                  {b.percent_used}% used
                </p>
              </div>

              <div className="mt-4 h-4 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    isOver ? "bg-red-500" : "bg-emerald-600"
                  }`}
                  style={{ width: `${percent}%` }}
                ></div>
              </div>

              <div className="mt-4">
                {isOver ? (
                  <p className="text-red-600 font-semibold">
                    Over budget by ₹{Math.abs(b.remaining)}
                  </p>
                ) : (
                  <p className="text-slate-600">
                    Remaining: ₹{b.remaining}
                  </p>
                )}
              </div>
            </div>
          );
        })}

        {budgets.length === 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 text-slate-500">
            No budgets created yet.
          </div>
        )}
      </div>
    </div>
  );
}