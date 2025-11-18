"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import "@/app/frontend/styles/buttons.css";
import styles from "@/app/frontend/css/ProfilePage.module.css"
import formStyles from "@/app/frontend/css/NewEvent.module.css"; // Використаємо стилі з іншої форми
import { ALL_TAGS } from "@/lib/constants";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [interests, setInterests] = useState<string[]>([]);
  const [isEditing, setIsEditing] = useState(false); // Чи відкрито вікно
  const [tempInterests, setTempInterests] = useState<string[]>([]); // Тимчасовий вибір поки не натиснули "Зберегти"
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

  // 1. Відкрити модальне вікно
  const openEditModal = () => {
    setTempInterests([...interests]); // Копіюємо поточні інтереси в тимчасовий стан
    setIsEditing(true);
    setMessage("");
  };

  // 2. Логіка кліку на тег (переміщення між списками)
  const toggleTempInterest = (tag: string) => {
    setTempInterests(prev => 
      prev.includes(tag)
        ? prev.filter(t => t !== tag) // Якщо є -> видаляємо (переміщаємо вниз)
        : [...prev, tag]              // Якщо нема -> додаємо (переміщаємо вверх)
    );
  };

  // 3. Зберегти зміни на сервер
  const handleSaveChanges = async () => {
    try {
      const res = await fetch('/api/auth/me', { 
        method: 'PATCH', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interests: tempInterests }), // Відправляємо тимчасовий вибір
      });

      if (!res.ok) throw new Error("Не вдалося оновити інтереси");

      // Оновлюємо основний стан і закриваємо вікно
      setInterests(tempInterests);
      setIsEditing(false);
      
      // Можна оновити і об'єкт user для повноти картини
      setUser((prev: any) => ({ ...prev, interests: tempInterests }));

    } catch (err: any) {
      alert(`Помилка: ${err.message}`);
    }
  };

  if (loading) return <p>Завантаження...</p>;
  if (!user) return <p>Користувача не знайдено або ви не авторизовані</p>;
  // Обчислюємо списки для модального вікна
  // "Обрані" = tempInterests
  // "Доступні" = Всі теги МІНУС Обрані
  const availableTags = ALL_TAGS.filter(tag => !tempInterests.includes(tag));

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
            
            {/* Відображення збережених тегів (View Mode) */}
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
            <button onClick={openEditModal} className={styles.editButton}>
                ✏️ Редагувати інтереси
            </button>
        </div>
</section>

{/* --- МОДАЛЬНЕ ВІКНО (Відкривається тільки якщо isEditing === true) --- */}
      {isEditing && (
        <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
                <h2 className={styles.modalHeader}>Редагування інтересів</h2>
                
                <div className={styles.selectionArea}>
                    
                    {/* Ячейка 1: Вже вибрані */}
                    <div className={styles.sectionBox} style={{backgroundColor: '#f0fdf4', borderColor: '#86efac'}}>
                        <p className={styles.sectionTitle}>✅ Вибрані (Клікніть, щоб видалити)</p>
                        <div className={styles.tagList}>
                            {tempInterests.length === 0 && <span style={{color:'#aaa', fontSize:'0.9em'}}>Поки нічого не вибрано...</span>}
                            {tempInterests.map(tag => (
                                <span 
                                    key={tag} 
                                    onClick={() => toggleTempInterest(tag)}
                                    className={`${styles.interactiveTag} ${styles.selectedTag}`}
                                >
                                    {tag} ✕
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Ячейка 2: Всі доступні */}
                    <div className={styles.sectionBox}>
                        <p className={styles.sectionTitle}>➕ Доступні (Клікніть, щоб додати)</p>
                        <div className={styles.tagList}>
                            {availableTags.map(tag => (
                                <span 
                                    key={tag} 
                                    onClick={() => toggleTempInterest(tag)}
                                    className={`${styles.interactiveTag} ${styles.availableTag}`}
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>

                </div>

                <div className={styles.modalActions}>
                    <button onClick={() => setIsEditing(false)} className={styles.cancelBtn}>
                        Відмінити
                    </button>
                    <button onClick={handleSaveChanges} className={styles.saveBtn}>
                        Зберегти зміни
                    </button>
                </div>
            </div>
        </div>
      )}

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
