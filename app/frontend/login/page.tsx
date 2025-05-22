"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from "@/app/frontend/css/LoginPage.module.css"

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
    <main className={styles.container}>
      <h1 className={styles.title}>Вхід</h1>
      <form onSubmit={handleLogin} className={styles.form}>
        <input
          type="text"
          placeholder="Ім'я користувача"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={styles.input}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
        />
        {error && <p className={styles.error}>{error}</p>}
        <button type="submit" className={styles.button}>
          Увійти
        </button>
      </form>
      
      <p className={styles.registerLink}>
  Не маєте акаунта?{" "}
  <Link href="/frontend/users/new" className={styles.link}>
    Зареєструватися
  </Link>
</p>

    </main>
  );
}
