'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from "@/app/frontend/css/EditEventPage.module.css"

export default function EditEventPage({ params }: { params: { id: string } }) {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
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
      body: JSON.stringify({ title, date }),
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
        <button type="submit" className={styles.button}>
          Зберегти
        </button>
      </form>
    </main>
  );
}
