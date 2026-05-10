"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import "@/app/frontend/styles/buttons.css";
import styles from "@/app/frontend/css/ProfilePage.module.css"
import formStyles from "@/app/frontend/css/NewEvent.module.css"; // Використаємо стилі з іншої форми
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [interests, setInterests] = useState<string[]>([]);
  const [isEditing, setIsEditing] = useState(false); // Чи відкрито вікно
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

// +++ 3. Функція збереження стала простішою +++
  // Вона тепер просто приймає масив тегів від модалки
  const handleSaveInterests = async (selectedTags: string[]) => {
    try {
      const res = await fetch('/api/auth/me', { 
        method: 'PATCH', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interests: selectedTags }),
      });

      if (!res.ok) throw new Error("Не вдалося оновити інтереси");

      // Оновлюємо стан
      setInterests(selectedTags);
      setIsEditing(false); // Закриваємо модалку
      
      // Оновлюємо об'єкт user
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

      <Link href="/frontend/profile/participated" className={styles.linkButton}>
  Я беру участь
</Link>

<div style={{marginTop: '20px'}}>
            <h3 className={styles.eventsTitle}>Мої інтереси</h3>
            
            {/* Відображення тегів (View Mode) */}
            <div className={styles.tagsContainer}>
                {interests.length > 0 ? (
                    interests.map(tag => (
                        <span key={tag} className={styles.tagPill}>#{tag}</span>
                    ))
                ) : (
                    <p style={{color: '#888'}}>Ви ще не обрали інтереси</p>
                )}
            </div>

            {/* Кнопка редагування */}
            <button onClick={() => setIsEditing(true)} className={styles.editButton}>
                ✏️ Редагувати інтереси
            </button>
        </div>
</section>

{/* +++ 4. ПІДКЛЮЧАЄМО МОДАЛКУ +++ */}
      {/* Дивіться, наскільки чистішим став код! */}
      <TagSelectionModal
        isOpen={isEditing}
        onClose={() => setIsEditing(false)}
        onSave={handleSaveInterests}
        initialSelected={interests}
        allTags={ALL_TAGS}
        title="Редагування інтересів"
      />
      {/* +++ КІНЕЦЬ МОДАЛКИ +++ */}

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
