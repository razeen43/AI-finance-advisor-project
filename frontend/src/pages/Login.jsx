import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/client";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = async (e) => {
    e.preventDefault();

    try {
      const res = await api.post("/auth/login", {
        email,
        password
      });

      localStorage.setItem("token", res.data.access_token);

      navigate("/dashboard");
    } catch (error) {
      alert(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form onSubmit={login} className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h1 className="text-3xl font-bold text-emerald-700 text-center">
          AI Finance Advisor
        </h1>

        <input
          className="w-full mt-6 px-4 py-3 border rounded-xl"
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full mt-4 px-4 py-3 border rounded-xl"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="w-full mt-6 bg-emerald-700 text-white py-3 rounded-xl font-semibold">
          Login
        </button>

        <p className="text-center mt-4">
          Don't have an account?{" "}
          <Link className="text-emerald-700 font-semibold" to="/register">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}