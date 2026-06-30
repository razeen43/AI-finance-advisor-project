import { useState } from "react";
import { FaRobot, FaUser, FaPaperPlane } from "react-icons/fa";
import api from "../api/client";

export default function AIAdvisor() {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hi! Ask me about your spending, budgets, anomalies, or transactions."
    }
  ]);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const currentQuestion = question;

    setMessages((prev) => [
      ...prev,
      { sender: "user", text: currentQuestion }
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const res = await api.post("/ai/chat", {
        question: currentQuestion
      });

      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: res.data.answer }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Sorry, I could not process your question." }
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="h-[85vh] flex flex-col">
      <div className="mb-5">
        <h1 className="text-3xl font-bold text-slate-900">AI Financial Advisor</h1>
        <p className="text-slate-500 mt-1">
          Ask questions powered by RAG, FAISS retrieval, and ML insights.
        </p>
      </div>

      <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm p-5 overflow-y-auto space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-5 py-4 ${
                msg.sender === "user"
                  ? "bg-emerald-700 text-white"
                  : "bg-slate-100 text-slate-900"
              }`}
            >
              <div className="flex items-center gap-2 mb-2 text-sm opacity-80">
                {msg.sender === "user" ? <FaUser /> : <FaRobot />}
                <span>{msg.sender === "user" ? "You" : "AI Advisor"}</span>
              </div>

              <p className="leading-relaxed whitespace-pre-line">{msg.text}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-5 py-4 text-slate-600">
              AI is thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="mt-5 flex gap-3">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask: Did I exceed my food budget?"
          className="flex-1 px-5 py-4 rounded-2xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-600"
        />

        <button
          type="submit"
          className="px-6 py-4 rounded-2xl bg-emerald-700 text-white font-semibold flex items-center gap-2 hover:bg-emerald-800"
        >
          <FaPaperPlane />
          Send
        </button>
      </form>
    </div>
  );
}