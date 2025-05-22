"use client";

import { useState, useEffect } from "react";
import { createEvent, fetchUsers } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from "@/app/frontend/css/NewEvent.module.css"

export default function NewEventPage() {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [userId, setUserId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchCurrentUser = async () => {
  try {
    const res = await fetch("/api/auth/me", {
      credentials: "include", // ✅ дозволяє надсилати кукі з токеном
    });

    if (!res.ok) throw new Error("Not authenticated");

    const { user } = await res.json();
    setUserId(user.userId); // або user._id, залежно від структури
  } catch (err) {
    router.push("/frontend/login");
  } finally {
    setLoading(false);
  }
};


    fetchCurrentUser();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

if (!userId) {
    setError("Користувач не авторизований");
    return;
  }

    try {
      await createEvent({ title, date, userId });
      router.push("/frontend/events");
    } catch (err) {
      setError("Не вдалося створити подію");
      console.error(err);
    }
  };

  if (loading) return <p>Завантаження...</p>;

  return (
    <main className={styles.mainWrapper}>
      <h1 className={styles.header}>Створити нову подію</h1>

      <form onSubmit={handleSubmit} className={styles.formContainer}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Назва</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className={styles.input}
          />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Дата</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className={styles.input}
          />
        </div>
        {/* <div className={styles.formGroup}>
          <label className={styles.label}>Користувач</label>
          <select
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            className={styles.select}
          >
            <option value="">Оберіть користувача</option>
            {users.map((user: any) => (
              <option key={user._id} value={user._id}>
                {user.username}
              </option>
            ))}
          </select>
        </div> */}

        {error && <p className={styles.error}>{error}</p>}

      <div className={styles.buttonGroup}>
        <button
          type="submit"
          className={styles.buttonPrimary}
        >
          Створити
        </button>
      
      <Link href="/frontend/events">
        <button className={styles.buttonSecondary}>
          Назад
        </button>
      </Link>
      </div>
      </form>
    </main>
  );
}
