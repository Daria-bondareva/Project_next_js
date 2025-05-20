"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import "@/app/frontend/styles/buttons.css";

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
    <main className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">Профіль: {user.username}</h1>
      <p>Email: {user.email}</p>

      <Link href="/frontend/profile/participated">
  Я беру участь
</Link>


      <h2 className="text-xl font-semibold mt-6">Події користувача</h2>
      {events.length === 0 ? (
        <p>Немає подій.</p>
      ) : (
        <ul className="space-y-3">
          {events.map((event: any) => (
            <li
              key={event._id}
              className="border p-3 rounded flex justify-between items-center"
            >
              <span className="font-semibold">{event.title}</span>
              <Link
                href={`/frontend/events/${event._id}`}
                className="view-button"
              >
                Переглянути
              </Link>
            </li>
          ))}
        </ul>
      )}

      <button
        onClick={handleLogout}
        className="mt-6 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Вийти
      </button>
    </main>
  );
}
