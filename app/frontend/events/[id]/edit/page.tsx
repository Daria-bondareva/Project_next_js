'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

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
    <main className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Редагувати подію</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-semibold">Назва</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border px-3 py-2 rounded"
            required
          />
        </div>
        <div>
          <label className="block font-semibold">Дата</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full border px-3 py-2 rounded"
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Зберегти
        </button>
      </form>
    </main>
  );
}
