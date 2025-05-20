"use client";

import { useEffect, useState } from "react";
import { fetchUsers } from "@/lib/api";
import Link from "next/link";

type User = {
  _id: string;
  username: string;
  email: string;
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const usersData = await fetchUsers(`${query}&sort=${sortOrder}`);
        setUsers(usersData);
      } catch (error) {
        console.error("Помилка при завантаженні користувачів", error);
      }
    };

    loadUsers();
  }, [query, sortOrder]);

  const handleSearch = () => {
    setQuery(`search=${searchTerm}`);
  };

  const toggleSort = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  return (
    <main className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Список користувачів</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Пошук за ім'ям..."
          className="border p-2 rounded flex-grow"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Пошук
        </button>
        <button
          onClick={toggleSort}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          {sortOrder === "asc" ? "↑ За іменем" : "↓ За іменем"}
        </button>
      </div>

      {users.length === 0 ? (
        <p>Немає користувачів.</p>
      ) : (
        <ul className="space-y-3">
          {users.map((user) => (
            <li key={user._id} className="border p-3 rounded shadow-sm">
              <h2 className="font-semibold">{user.username}</h2>
              <p>Email: {user.email}</p>
            </li>
          ))}
        </ul>
      )}

      <Link href="/">
        <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mt-4">
          Назад до головної
        </button>
      </Link>
    </main>
  );
}
