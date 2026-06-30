import { useEffect, useState } from "react";
import { FaPlus, FaExclamationTriangle } from "react-icons/fa";
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

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [merchant, setMerchant] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");

  const fetchTransactions = async () => {
    const res = await api.get("/transactions/");
    setTransactions(res.data);
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const addTransaction = async (e) => {
    e.preventDefault();

    await api.post("/transactions/", {
      merchant,
      amount: Number(amount),
      category
    });

    setMerchant("");
    setAmount("");
    setCategory("Food");
    fetchTransactions();
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Transactions</h1>
        <p className="text-slate-500 mt-1">
          Add, track, and analyze your spending data.
        </p>
      </div>

      <form
        onSubmit={addTransaction}
        className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <input
          placeholder="Merchant"
          value={merchant}
          onChange={(e) => setMerchant(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        />

        <input
          placeholder="Amount"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        />

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        >
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>

        <button
          type="submit"
          className="bg-emerald-700 text-white rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-emerald-800"
        >
          <FaPlus />
          Add
        </button>
      </form>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200">
          <h2 className="text-xl font-bold">Recent Transactions</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-600 text-sm">
              <tr>
                <th className="p-4">Merchant</th>
                <th className="p-4">Category</th>
                <th className="p-4">Amount</th>
                <th className="p-4">AI Status</th>
              </tr>
            </thead>

            <tbody>
              {transactions.map((t) => (
                <tr key={t._id} className="border-t border-slate-100">
                  <td className="p-4 font-semibold text-slate-900">
                    {t.merchant}
                  </td>

                  <td className="p-4">
                    <span className="px-3 py-1 rounded-full text-sm bg-emerald-100 text-emerald-700">
                      {t.category}
                    </span>
                  </td>

                  <td className="p-4 font-bold">₹{t.amount}</td>

                  <td className="p-4">
                    {t.is_anomaly ? (
                      <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-red-100 text-red-700">
                        <FaExclamationTriangle />
                        Anomaly
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full text-sm bg-slate-100 text-slate-600">
                        Normal
                      </span>
                    )}
                  </td>
                </tr>
              ))}

              {transactions.length === 0 && (
                <tr>
                  <td className="p-5 text-slate-500" colSpan="4">
                    No transactions found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}