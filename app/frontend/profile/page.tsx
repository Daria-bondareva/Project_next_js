"use client";

import { useEffect, useState } from "react";
import styles from "@/app/frontend/css/ProfilePage.module.css";
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [interests, setInterests] = useState<string[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState("");

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
          if (data.user.interests) {
            setInterests(data.user.interests);
          }
        }
      } catch (err) {
        console.error("Не вдалося завантажити профіль", err);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleSaveInterests = async (selectedTags: string[]) => {
    try {
      const res = await fetch('/api/auth/me', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interests: selectedTags }),
      });

      if (!res.ok) throw new Error("Не вдалося оновити інтереси");

      setInterests(selectedTags);
      setIsEditing(false);
      setUser((prev: any) => ({ ...prev, interests: selectedTags }));
    } catch (err: any) {
      alert(`Помилка: ${err.message}`);
    }
  };

  if (loading) return <p>Завантаження...</p>;
  if (!user) return <p>Користувача не знайдено або ви не авторизовані</p>;

  return (
    <main className={styles.profileContainer}>
      <section className={styles.userCard}>
        <h1 className={styles.username}>Профіль: {user.username}</h1>
        <p className={styles.email}>Email: {user.email}</p>

        <Button variant="primary" href="/frontend/profile/participated">
          Я беру участь
        </Button>

        <div style={{ marginTop: '20px' }}>
          <h3 className={styles.eventsTitle}>Мої інтереси</h3>

          <div className={styles.tagsContainer}>
            {interests.length > 0 ? (
              interests.map(tag => (
                <Badge key={tag} variant="filled">#{tag}</Badge>
              ))
            ) : (
              <p style={{ color: 'var(--color-text-muted)' }}>Ви ще не обрали інтереси</p>
            )}
          </div>

          <Button variant="secondary" onClick={() => setIsEditing(true)}>
            ✏️ Редагувати інтереси
          </Button>
        </div>
      </section>

      <TagSelectionModal
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        onSave={handleSaveInterests}
        initialSelected={interests}
        allTags={ALL_TAGS}
        title="Редагування інтересів"
      />

      <section className={styles.eventsSection}>
        <h2 className={styles.eventsTitle}>Події користувача</h2>
        {events.length === 0 ? (
          <p className={styles.noEvents}>Немає подій.</p>
        ) : (
          <ul className={styles.eventsList}>
            {events.map((event: any) => (
              <li key={event._id} className={styles.eventCard}>
                <span className={styles.eventTitle}>{event.title}</span>
                <Button variant="ghost" size="sm" href={`/frontend/events/${event._id}`}>
                  Переглянути
                </Button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Button variant="danger" onClick={handleLogout}>
        Вийти з профілю
      </Button>
    </main>
  );
}
