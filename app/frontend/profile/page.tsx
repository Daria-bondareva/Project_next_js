"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import "@/app/frontend/styles/buttons.css";
import styles from "@/app/frontend/css/ProfilePage.module.css"

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/";
  };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await fetch("/api/auth/me");
        const data = await res.json();
        if (res.ok) {
          setUser(data.user);
          setEvents(data.events);
        }
      } catch (err) {
        console.error("Не вдалося завантажити профіль", err);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  if (loading) return <p>Завантаження...</p>;
  if (!user) return <p>Користувача не знайдено або ви не авторизовані</p>;

  return (
    <main className={styles.profileContainer}>
      <section className={styles.userCard}>
      <h1 className={styles.username}>Профіль: {user.username}</h1>
      <p className={styles.email}>Email: {user.email}</p>

      <Link href="/frontend/profile/participated" className={styles.linkButton}>
  Я беру участь
</Link>
</section>

      <section className={styles.eventsSection}>
      <h2 className={styles.eventsTitle}>Події користувача</h2>
      {events.length === 0 ? (
        <p className={styles.noEvents}>Немає подій.</p>
      ) : (
        <ul className={styles.eventsList}>
          {events.map((event: any) => (
            <li
              key={event._id}
              className={styles.eventCard}
            >
              <span className={styles.eventTitle}>{event.title}</span>
              <Link
                href={`/frontend/events/${event._id}`}
                className={styles.viewButton}
              >
                Переглянути
              </Link>
            </li>
          ))}
        </ul>
      )}
</section>

      <button
        onClick={handleLogout}
        className={styles.logoutButton}
      >
        Вийти з профілю
      </button>
    </main>
  );
}
