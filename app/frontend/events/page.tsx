"use client";

import { useEffect, useState } from "react";
import { fetchEvents } from "@/lib/api";
import Link from "next/link";
import style1 from "@/app/frontend/css/EventCard.module.css";
import styles from "@/app/Home.module.css";
import styles2 from "@/app/frontend/css/PageEvents.module.css"

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
      <h1 className={`${styles2.pageTitle} ${styles.title}`}>Список подій</h1>

  <div className={styles2.filterPanel}>
  <input
    type="text"
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    placeholder="Пошук за назвою..."
    className={styles2.filterInput}
  />
  <button
    onClick={handleSearch}
    className={styles2.filterButton}
  >
    Пошук
  </button>

  <button
    onClick={() => setSortField((prev) => (prev === "title" ? "date" : "title"))}
    className={styles2.filterButton}
  >
    Сортувати за: {sortField === "title" ? "Назвою" : "Датою"}
  </button>

  <button
    onClick={() => setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"))}
    className={styles2.filterButton}
  >
    {sortDirection === "asc" ? "↑" : "↓"}
  </button>
</div>


      {loading ? (
        <p>Завантаження...</p>
      ) : events.length === 0 ? (
        <p>Немає подій.</p>
      ) : (
        <ul className={style1.cardList}>
          {events.map((event) => (
            <li key={event._id} className={style1.card}>
              <h3 className={style1.cardHeader}>{event.title}</h3>
              <p className={style1.cardContent}>Дата: {new Date(event.date).toLocaleDateString()}</p>
              <p className={style1.cardUser}>Автор: {event.userId?.username || "Невідомо"}</p>
              <a href={`/frontend/events/${event._id}`} className={style1.viewButton}>
            Переглянути
            </a>
            </li>
          ))}
        </ul>
      )}

      <Link href="/">
        <button className={style1.viewButton}>
          Назад до головної
        </button>
      </Link>
    </main>
  );
}
