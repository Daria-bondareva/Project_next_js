"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type Event = {
  _id: string;
  title: string;
  date: string;
};

type User = {
  _id: string;
  username: string;
  email: string;
};

export default function UserProfilePage() {
  const { id } = useParams();
  const [user, setUser] = useState<User | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        // окремий запит на користувача
        const userRes = await fetch(`/api/users/${id}`);
        const userData = await userRes.json();
        setUser(userData);

        // окремий запит на події цього користувача
        const eventsRes = await fetch(`/api/events?userId=${id}`);
        const eventsData = await eventsRes.json();
        setEvents(eventsData);
      } catch (err) {
        console.error("Помилка при завантаженні профілю", err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadProfile();
    }
  }, [id]);

  if (loading) return <p>Завантаження...</p>;
  if (!user) return <p>Користувача не знайдено</p>;

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">Профіль: {user.username}</h1>
      <p>Email: {user.email}</p>

      <h2 className="text-xl font-semibold mt-6">Події користувача</h2>
      {events.length === 0 ? (
        <p>Цей користувач ще не створив жодної події.</p>
      ) : (
        <ul className="space-y-3">
          {events.map((event) => (
            <li key={event._id} className="border p-3 rounded">
              <h3 className="font-semibold">{event.title}</h3>
              <p>Дата: {new Date(event.date).toLocaleString()}</p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
