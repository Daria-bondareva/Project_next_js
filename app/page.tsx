"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchUsers, fetchEvents } from "@/lib/api";
import styles from "./Home.module.css";
import style1 from "./frontend/css/EventCard.module.css";
import Image from "next/image";

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
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    const load = async () => {
      const [ev, us] = await Promise.all([
        fetchEvents("sort=date_desc"),
        fetchUsers(),
      ]);
      setEvents(ev.slice(0, 5)); // Тільки 3 останні
      setUsers(us);
    };

    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        setIsLoggedIn(res.ok);
      } catch {
        setIsLoggedIn(false);
      }
    };

    load();
    checkAuth();
  }, []);

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-6">
     
      {isLoggedIn === false && (
        <div className={styles.heroSection}>
          <Image
            src="/ban_1_5.png"
            alt="Background"
            fill
            className={styles.heroImage}
          />
          <div className={styles.heroContent}>
            <h1>Знайдіть своїх людей, відкрийте інтереси, та приєднуйтесь до надихаючих заходів</h1>
            <Link href="/frontend/users/new">
              <button className={styles.heroButton}>Join to Kindred</button>
            </Link>
          </div>
        </div>
      )}


<section>
      <section className={styles.headerSection}>
  <h2 className={styles.title}>Популярні події</h2>
  <Link href="/frontend/events">
    <button className={styles.heroButton}>Більше →</button>
  </Link>
</section>
      {events.length === 0 && <p>Подій поки немає.</p>}
      <ul className={style1.cardList}>
        {events.map((e) => (
          <li key={e._id} className={style1.card}>
            <h3 className={style1.cardHeader}>{e.title}</h3>
            <p className={style1.cardContent}>
              📅 Дата: {new Date(e.date).toLocaleString()}
            </p>
            <p className={style1.cardUser}>
              👤 Користувач: {e.userId?.username || 'Невідомо'}
            </p>
            <a href={`/frontend/events/${e._id}`} className={style1.viewButton}>
            Переглянути
            </a>
          </li>
        ))}
        
      </ul>
    </section>

    <section className={styles.createBlock}>
  <div className={styles.textContent}>
    <h2 className={styles.createTitle}>Перетвори свою ідею в подію</h2>
    <p className={styles.createDescription}>
      Створи власну подію, яка надихає, об'єднує та розвиває твою спільноту. Це може бути хобі, професійна зустріч або просто крута ініціатива!
    </p>
    <Link href="/frontend/events/new">
      <button className={`${styles.button} ${styles.red}`}>Створити подію →</button>
    </Link>
  </div>
</section>



      {/* <section>
        <h2 className="text-xl font-semibold mt-6 mb-3">Популярні події</h2>
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
      </section> */}

    </main>
  );
}
