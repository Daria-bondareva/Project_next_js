"use client";

import { useState } from "react";
import { createUser } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function NewUserPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      // 1. Створюємо користувача
      const res = await createUser({ username, email, password });

      if (!res || !res.user) {
        throw new Error("Не вдалося створити користувача");
      }

      // 2. Вхід автоматично
      const loginRes = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!loginRes.ok) {
        throw new Error("Не вдалося увійти після реєстрації");
      }

      // 3. Редірект на профіль
      router.push("/frontend/profile");
    } catch (err: any) {
      setError(err.message || "Помилка при створенні користувача");
      console.error(err);
    }
  };

  return (
    <main className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold">Створити нового користувача</h1>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block mb-1 font-medium">Ім'я</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full border p-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border p-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">Пароль</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border p-2 rounded"
          />
        </div>

        {error && <p className="text-red-600">{error}</p>}

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Створити
        </button>
      </form>

      <Link href="/frontend/users">
        <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mt-4">
          Назад
        </button>
      </Link>
    </main>
  );
}
