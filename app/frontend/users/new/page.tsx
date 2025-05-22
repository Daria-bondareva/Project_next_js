"use client";

import { useState } from "react";
import { createUser } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from "@/app/frontend/css/NewUserPage.module.css"

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
    <main className={styles.container}>
      <h1 className={styles.title}>Реєстрація</h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div>
          <label className={styles.label}>Ім'я</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className={styles.input}
          />
        </div>
        <div>
          <label className={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={styles.input}
          />
        </div>
        <div>
          <label className={styles.label}>Пароль</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className={styles.input}
          />
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button type="submit" className={styles.submit}
        >
          Створити
        </button>
      </form>

    </main>
  );
}
