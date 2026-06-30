import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/client";

export default function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const register = async (e) => {
    e.preventDefault();

    try {
      await api.post("/auth/register", {
        name,
        email,
        password
      });

      alert("Registration successful. Please login.");
      navigate("/");
    } catch (error) {
      alert(error.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <form onSubmit={register} className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h1 className="text-3xl font-bold text-emerald-700 text-center">
          Create Account
        </h1>

        <input
          className="w-full mt-6 px-4 py-3 border rounded-xl"
          placeholder="Full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          className="w-full mt-4 px-4 py-3 border rounded-xl"
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
          Register
        </button>

        <p className="text-center mt-4">
          Already have an account?{" "}
          <Link className="text-emerald-700 font-semibold" to="/">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}