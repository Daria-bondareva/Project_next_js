"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchUsers, fetchEvents } from "@/lib/api";

type User = {
  _id: string;
  username: string;
};

type Event = {
  _id: string;
  title: string;
  date: string;
  userId: {
    _id: string;
    username: string;
  };
};


export default function HomePage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const load = async () => {
      const [ev, us] = await Promise.all([
        fetchEvents("sort=date_desc"),
        fetchUsers(),
      ]);
      setEvents(ev.slice(0, 3)); // Тільки 3 останні
      setUsers(us);
    };

    load();
  }, []);

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-6">
     
      <h1 className="text-2xl font-bold">Ласкаво просимо!</h1>

      <section>
        <h2 className="text-xl font-semibold mt-6 mb-3">Останні події</h2>
        {events.length === 0 && <p>Подій поки немає.</p>}
        <ul className="space-y-3">
          {events.map((e) => (
  <li key={e._id} className="border p-3 rounded shadow-sm">
    <h3 className="font-medium">{e.title}</h3>
    <p>Дата: {new Date(e.date).toLocaleString()}</p>
    <p>Користувач: {e.userId?.username || "Невідомо"}</p>
  </li>
))}

        </ul>
      </section>
    </main>
  );
}
