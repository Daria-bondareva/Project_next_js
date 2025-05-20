"use client";

import { useState, useEffect } from "react";
import { createEvent, fetchUsers } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function NewEventPage() {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [userId, setUserId] = useState("");
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .catch(() => setError("Не вдалося завантажити користувачів"));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createEvent({ title, date, userId });
      router.push("/frontend/events");
    } catch (err) {
      setError("Не вдалося створити подію");
      console.error(err);
    }
  };

  return (
    <main className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold">Створити нову подію</h1>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block mb-1 font-medium">Назва</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full border p-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">Дата</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className="w-full border p-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">Користувач</label>
          <select
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            className="w-full border p-2 rounded"
          >
            <option value="">Оберіть користувача</option>
            {users.map((user: any) => (
              <option key={user._id} value={user._id}>
                {user.username}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-red-600">{error}</p>}

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Створити
        </button>
      </form>

      <Link href="/frontend/events">
        <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mt-4">
          Назад
        </button>
      </Link>
    </main>
  );
}
