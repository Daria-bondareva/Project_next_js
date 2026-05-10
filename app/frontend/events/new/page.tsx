"use client";

import { useState, useEffect } from "react";
import { createEvent, fetchUsers } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from "@/app/frontend/css/NewEvent.module.css"
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";

export default function NewEventPage() {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState<string[]>([]); // +++ Додаємо стан для тегів
  const [userId, setUserId] = useState("");
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchCurrentUser = async () => {
  try {
    const res = await fetch("/api/auth/me", {
      credentials: "include", // ✅ дозволяє надсилати кукі з токеном
    });

    if (!res.ok) throw new Error("Not authenticated");

    const { user } = await res.json();
    setUserId(user._id); // або user._id, залежно від структури
  } catch (err) {
    router.push("/frontend/login");
  } finally {
    setLoading(false);
  }
};

    fetchCurrentUser();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

if (!userId) {
    setError("Користувач не авторизований");
    return;
  }

    try {
      await createEvent({ title, date, userId, tags: tags, description });
      router.push("/frontend/events");
    } catch (err) {
      setError("Не вдалося створити подію");
      console.error(err);
    }
  };

  if (loading) return <p>Завантаження...</p>;

  return (
    <main className={styles.mainWrapper}>
      <h1 className={styles.header}>Створити нову подію</h1>

      <form onSubmit={handleSubmit} className={styles.formContainer}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Назва</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className={styles.input}
          />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Дата</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className={styles.input}
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Опис події</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={styles.input} // Використайте той самий клас, що і для input
            rows={4} // Висота поля
            placeholder="Розкажіть детальніше, про що буде ця подія..."
          />
        </div>

        {/* +++ 3. НОВИЙ БЛОК ВИБОРУ ТЕГІВ +++ */}
        <div className={styles.formGroup}>
          <label className={styles.label}>Теги події</label>
          
          {/* Відображаємо вибрані теги як красиві пігулки */}
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px', marginTop: '5px'}}>
            {tags.length > 0 ? tags.map(tag => (
                <span key={tag} style={{
                    background: '#e0e7ff', color: '#3730a3', 
                    padding: '6px 12px', borderRadius: '20px', fontSize: '0.9rem', fontWeight: '500'
                }}>
                    #{tag}
                </span>
            )) : <span style={{color:'#888', fontStyle:'italic'}}>Теги не обрано</span>}
          </div>

          {/* Кнопка відкриття модалки */}
          <button 
            type="button" // Важливо: type="button", щоб не сабмітити форму при кліку
            onClick={() => setIsModalOpen(true)}
            className={styles.buttonSecondary} 
            style={{width: '100%', marginTop: '5px'}}
          >
            ✏️ Обрати теги
          </button>
        </div>
        {/* +++ 4. ПІДКЛЮЧАЄМО МОДАЛКУ +++ */}
        <TagSelectionModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onSave={(selected) => setTags(selected)} // Зберігаємо вибір у стан tags
            initialSelected={tags} // Передаємо поточні теги, щоб вони вже були вибрані у вікні
            allTags={ALL_TAGS}
            title="Оберіть теги для події"
        />
        {/* +++ КІНЕЦЬ +++ */}
        {/* +++ Кінець нового блоку +++ */}

        {/* <div className={styles.formGroup}>
          <label className={styles.label}>Користувач</label>
          <select
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            className={styles.select}
          >
            <option value="">Оберіть користувача</option>
            {users.map((user: any) => (
              <option key={user._id} value={user._id}>
                {user.username}
              </option>
            ))}
          </select>
        </div> */}

        {error && <p className={styles.error}>{error}</p>}

      <div className={styles.buttonGroup}>
        <button
          type="submit"
          className={styles.buttonPrimary}
        >
          Створити
        </button>
      
      <Link href="/frontend/events">
        <button className={styles.buttonSecondary}>
          Назад
        </button>
      </Link>
      </div>
      </form>
    </main>
  );
}
