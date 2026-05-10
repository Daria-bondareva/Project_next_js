'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from "@/app/frontend/css/EditEventPage.module.css"
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";

export default function EditEventPage({ params }: { params: { id: string } }) {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [description, setDescription] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchEvent = async () => {
      const res = await fetch(`/api/events/${params.id}`);
      if (!res.ok) {
        alert('Подію не знайдено');
        router.push('/frontend/events');
        return;
      }

      const data = await res.json();
      setTitle(data.title);
      setDate(new Date(data.date).toISOString().slice(0, 16)); // Для input type="datetime-local"
      setTags(data.tags || []);
      setDescription(data.description || "");
    };

    fetchEvent();
  }, [params.id, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch(`/api/events/${params.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, date, tags, description }),
    });

    if (res.ok) {
      router.push(`/frontend/events/${params.id}`);
    } else {
      alert('Помилка при збереженні змін');
    }
  };

 return (
    <main className={styles.container}>
      <h1 className={styles.title}>Редагувати подію</h1>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div>
          <label className={styles.label}>Назва</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={styles.input}
            required
          />
        </div>
        <div>
          <label className={styles.label}>Дата</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className={styles.input}
            required
          />
        </div>

        <div>
          <label className={styles.label}>Опис</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={styles.input} // Використовуємо той самий клас, щоб стиль рамок був однаковим
            rows={5} // Висота у рядках
            placeholder="Розкажіть детальніше про подію..."
            style={{
                height: 'auto', 
                minHeight: '100px', 
                resize: 'vertical', 
                padding: '10px',
                fontFamily: 'inherit' // Щоб шрифт не відрізнявся
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
            <label className={styles.label}>Теги</label>
            
            {/* Відображення пігулок */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px', marginTop: '5px' }}>
                {tags.length > 0 ? tags.map(tag => (
                    <span key={tag} style={{
                        background: '#e0e7ff', color: '#3730a3', 
                        padding: '6px 12px', borderRadius: '20px', 
                        fontSize: '0.9rem', fontWeight: '500'
                    }}>
                        #{tag}
                    </span>
                )) : <span style={{ color: '#888', fontStyle: 'italic' }}>Теги не обрано</span>}
            </div>

            {/* Кнопка відкриття модалки */}
            <button 
                type="button" 
                onClick={() => setIsModalOpen(true)}
                // Використовуємо стиль інпуту або кнопки, або інлайн для простоти
                style={{
                    padding: '8px 16px', borderRadius: '8px', border: '1px solid #ccc',
                    background: 'white', cursor: 'pointer', width: '100%'
                }}
            >
                 Редагувати теги
            </button>
        </div>

          <TagSelectionModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onSave={(selected) => setTags(selected)}
            initialSelected={tags}
            allTags={ALL_TAGS}
            title="Редагування тегів події"
        />

        <button type="submit" className={styles.button}>
          Зберегти
        </button>
      </form>
    </main>
  );
}
