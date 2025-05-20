"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        setIsLoggedIn(res.ok);
      } catch {
        setIsLoggedIn(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoggedIn === null) {
    return null; // або показати прелоадер/заглушку
  }

  return (
    <header className="w-full bg-gray-100 p-4 flex justify-between items-center">
      <Link href="/" className="text-xl font-bold">
        🏠 Головна
      </Link>

      <div className="flex space-x-3">
        <Link href="/frontend/users">
          <button className="bg-gray-700 text-white px-3 py-2 rounded hover:bg-gray-800">
            👤 Користувачі
          </button>
        </Link>
        <Link href="/frontend/events">
          <button className="bg-gray-700 text-white px-3 py-2 rounded hover:bg-gray-800">
            📅 Події
          </button>
        </Link>
        <Link href="/frontend/users/new">
          <button className="bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700">
            ➕ Користувач
          </button>
        </Link>
        <Link href="/frontend/events/new">
          <button className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700">
            ➕ Подія
          </button>
        </Link>

        {isLoggedIn ? (
          <Link href="/frontend/profile">
            <button className="bg-indigo-600 text-white px-3 py-2 rounded hover:bg-indigo-700">
              👤 Профіль
            </button>
          </Link>
        ) : (
          <Link href="/frontend/login">
            <button className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700">
              Увійти
            </button>
          </Link>
        )}
      </div>
    </header>
  );
}
