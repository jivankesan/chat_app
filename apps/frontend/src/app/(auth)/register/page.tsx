"use client";

import React, { FormEvent, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const { registerUser } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await registerUser(email, password);
    alert("Registration successful! You can now log in.");
    router.push("/login");
  }

  return (
    <div className="max-w-md mx-auto mt-16 bg-white p-6 shadow rounded">
      <h2 className="text-2xl font-semibold mb-6">Register</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="email"
          className="border p-2"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          className="border p-2"
          placeholder="Password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="bg-black text-white py-2 rounded hover:bg-gray-800"
          type="submit"
        >
          Register
        </button>
      </form>
    </div>
  );
}
