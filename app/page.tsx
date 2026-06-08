"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchEvents } from "@/lib/api";
import { Calendar, User, Sparkles } from "lucide-react";
import styles from "./Home.module.css";
import cardStyles from "./frontend/css/EventCard.module.css";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";

type Event = {
  _id: string;
  title: string;
  date: string;
  tags?: string[];
  userId: {
    _id: string;
    username: string;
  };
};

export default function HomePage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [recommendations, setRecommendations] = useState<Event[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        const authStatus = res.ok;
        setIsLoggedIn(authStatus);

        if (authStatus) {
          loadRecommendations();
        }
      } catch {
        setIsLoggedIn(false);
      }
    };

    const loadEvents = async () => {
      try {
        const ev = await fetchEvents("sort=date_desc");
        setEvents(ev.slice(0, 5));
      } catch (e) {
        console.error(e);
      }
    };

    const loadRecommendations = async () => {
      setLoadingRecs(true);
      try {
        const res = await fetch('/api/recommendations');
        if (res.ok) {
          const data = await res.json();
          setRecommendations(data);
        }
      } catch (e) {
        console.error("Failed to load recs", e);
      } finally {
        setLoadingRecs(false);
      }
    };

    loadEvents();
    checkAuth();
  }, []);

  const renderCard = (e: Event) => (
    <li key={e._id} className={cardStyles.card}>
      <div className={cardStyles.cardBody}>
        <h3 className={cardStyles.cardHeader}>{e.title}</h3>

        {e.tags && e.tags.length > 0 && (
          <div className={cardStyles.tagsContainer}>
            {e.tags.slice(0, 3).map((t) => (
              <Badge key={t} variant="filled">#{t}</Badge>
            ))}
            {e.tags.length > 3 && (
              <Badge variant="outline">+{e.tags.length - 3}</Badge>
            )}
          </div>
        )}

        <p className={cardStyles.cardContent}>
          <Calendar size={14} />
          {new Date(e.date).toLocaleDateString("uk-UA", {
            day: "numeric", month: "long", hour: "2-digit", minute: "2-digit",
          })}
        </p>

        <p className={cardStyles.cardUser}>
          <User size={14} />
          {e.userId?.username || "Гість"}
        </p>
      </div>

      <Button
        variant="secondary"
        size="sm"
        href={`/frontend/events/${e._id}`}
        style={{ width: "100%" }}
      >
        Детальніше
      </Button>
    </li>
  );

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-6">

      {/* --- HERO --- */}
      {isLoggedIn === false && (
        <div className={styles.heroSection}>
          <div className={styles.heroCircle1} />
          <div className={styles.heroCircle2} />
          <div className={styles.heroCircle3} />
          <div className={styles.heroContent}>
            <h1 className={styles.heroTitle}>
              Знайдіть своїх людей,<br />відкрийте інтереси...
            </h1>
            <p className={styles.heroSubtitle}>
              Платформа для тих, хто шукає однодумців та нових вражень.
            </p>
            <Link href="/frontend/users/new" className={styles.heroCta}>
              Join to Kindred →
            </Link>
          </div>
        </div>
      )}

      {/* --- РЕКОМЕНДАЦІЇ --- */}
      {isLoggedIn && (
        <section style={{ marginBottom: '40px', marginTop: '20px' }}>
          <h2 className={`${styles.title} ${styles.recsTitle}`}>
            <Sparkles size={18} />
            Рекомендовано для вас
          </h2>
          <p style={{ fontSize: '0.9em', color: 'var(--color-text-muted)', marginBottom: '15px' }}>
            Підібрано на основі ваших інтересів
          </p>

          {loadingRecs ? (
            <p>Завантаження рекомендацій...</p>
          ) : recommendations.length > 0 ? (
            <ul className={cardStyles.cardList}>
              {recommendations.map(renderCard)}
            </ul>
          ) : (
            <div style={{ padding: '20px', background: 'var(--color-surface)', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '1px dashed var(--color-border-strong)' }}>
              <p>Поки що немає персональних рекомендацій.</p>
              <Link href="/frontend/profile" style={{ color: 'var(--color-primary-600)', textDecoration: 'underline' }}>
                Оновіть свої інтереси
              </Link>
            </div>
          )}
        </section>
      )}

      {/* --- ПОПУЛЯРНІ ПОДІЇ --- */}
      <section>
        <div className={styles.headerSection}>
          <h2 className={styles.title}>Популярні події</h2>
          <Button variant="secondary" href="/frontend/events">Більше →</Button>
        </div>

        {events.length === 0 && <p>Подій поки немає.</p>}

        <ul className={cardStyles.cardList}>
          {events.map(renderCard)}
        </ul>
      </section>

      {/* --- CTA БЛОК --- */}
      <section className={styles.createBlock}>
        <div className={styles.textContent}>
          <h2 className={styles.createTitle}>Перетвори свою ідею в подію</h2>
          <p className={styles.createDescription}>
            Створи власну подію, яка надихає...
          </p>
          <Button variant="primary" href="/frontend/events/new">
            Створити подію →
          </Button>
        </div>
      </section>

    </main>
  );
}
