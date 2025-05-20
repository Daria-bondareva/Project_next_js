"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      router.push("/frontend/profile");
    } else {
      const data = await res.json();
      setError(data.error || "Помилка входу");
    }
  };

  return (
    <main className="max-w-md mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Вхід</h1>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="text"
          placeholder="Ім'я користувача"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full border p-2 rounded"
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border p-2 rounded"
        />
        {error && <p className="text-red-600">{error}</p>}
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Увійти
        </button>
      </form>
      
      <p className="text-sm mt-4">
  Не маєте акаунта?{" "}
  <Link href="/frontend/users/new" className="text-blue-600 hover:underline">
    Зареєструватися
  </Link>
</p>

    </main>
  );
}
