"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import styles from "./Header.module.css";

export default function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const router = useRouter();

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

  const handleAddEvent = async () => {
    try {
      const res = await fetch("/api/auth/me");
      if (res.ok) {
        router.push("/frontend/events/new");
      } else {
        router.push("/frontend/login");
      }
    } catch {
      router.push("/frontend/login");
    }
  };

  if (isLoggedIn === null) {
    return null; // або показати прелоадер/заглушку
  }

  return (
    <header className={styles.header}>
      <Link href="/" className={styles.logo}>
        Kindred
      </Link>

      <div className={styles.navButtons}>
        {/* <Link href="/frontend/users">
          <button className={styles.button}>
            Користувачі
          </button>
        </Link> */}
        <Link href="/">
          <button className={`${styles.button} ${styles.linkButton}`}>
            Головна
          </button>
        </Link>
        <Link href="/frontend/events">
          <button className={`${styles.button} ${styles.linkButton}`}>
            Події
          </button>
        </Link>
        {/* <Link href="/frontend/users/new">
          <button className={styles.button}>
            Користувач
          </button>
        </Link> */}
        
          <button onClick={handleAddEvent} className={`${styles.linkButton}`}>
            Додати подію
          </button>
        

        {isLoggedIn ? (
          <Link href="/frontend/profile">
            <button className={`${styles.linkButton} ${styles.indigo}`}>
              Мій профіль
            </button>
          </Link>
        ) : (
          <Link href="/frontend/login">
            <button className={`${styles.button} ${styles.yellow}`}>
              Увійти
            </button>
          </Link>
        )}
      </div>
    </header>
  );
}
