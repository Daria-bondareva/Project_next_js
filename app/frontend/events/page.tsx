"use client";

import { useEffect, useState } from "react";
import { fetchEvents } from "@/lib/api";
import Link from "next/link";
import "@/app/frontend/styles/buttons.css";

type Event = {
  _id: string;
  title: string;
  date: string;
  userId: {
    _id: string;
    username: string;
  };
};

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [query, setQuery] = useState("");
  const [sortField, setSortField] = useState<"title" | "date">("title");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [loading, setLoading] = useState(true);
  const sortOrder = `${sortField}_${sortDirection}`; // наприклад title_asc або date_desc


  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await fetchEvents(`${query}${query ? "&" : ""}sort=${sortOrder}`);
        setEvents(data);
      } catch (error) {
        console.error("Помилка при завантаженні подій", error);
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, [query, sortOrder]);

  const handleSearch = () => {
    setQuery(`search=${searchTerm}`);
  };

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Список подій</h1>

      <div className="flex gap-2 mb-4">
  <input
    type="text"
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    placeholder="Пошук за назвою..."
    className="border p-2 rounded flex-grow"
  />
  <button
    onClick={handleSearch}
    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
  >
    Пошук
  </button>

  <button
    onClick={() => setSortField((prev) => (prev === "title" ? "date" : "title"))}
    className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
  >
    Сортувати за: {sortField === "title" ? "Назвою" : "Датою"}
  </button>

  <button
    onClick={() => setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"))}
    className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
  >
    {sortDirection === "asc" ? "↑" : "↓"}
  </button>
</div>


      {loading ? (
        <p>Завантаження...</p>
      ) : events.length === 0 ? (
        <p>Немає подій.</p>
      ) : (
        <ul className="space-y-3">
          {events.map((event) => (
            <li key={event._id} className="border p-3 rounded shadow-sm">
              <h2 className="font-semibold">{event.title}</h2>
              <p>Дата: {new Date(event.date).toLocaleDateString()}</p>
              <p className="text-gray-600">Автор: {event.userId?.username || "Невідомо"}</p>
              <a href={`/frontend/events/${event._id}`} className="view-button">
            Переглянути
            </a>
            </li>
          ))}
        </ul>
      )}

      <Link href="/">
        <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mt-4">
          Назад до головної
        </button>
      </Link>
    </main>
  );
}
