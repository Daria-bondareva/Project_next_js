"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import styles from "./Footer.module.css";

export default function Footer() {
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

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/";
  };

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.grid}>

          {/* Column 1 — Brand */}
          <div className={styles.brand}>
            <span className={styles.logo}>Kindred</span>
            <p className={styles.description}>
              Платформа для тих, хто шукає однодумців та нових вражень.
            </p>
          </div>

          {/* Column 2 — Navigation */}
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Навігація</h3>
            <nav className={styles.linkList}>
              <Link href="/" className={styles.link}>Головна</Link>
              <Link href="/frontend/events" className={styles.link}>Події</Link>
              <Link href="/frontend/events/new" className={styles.link}>Додати подію</Link>
            </nav>
          </div>

          {/* Column 3 — Account (auth-aware) */}
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Акаунт</h3>
            <nav className={styles.linkList}>
              {isLoggedIn ? (
                <>
                  <Link href="/frontend/profile" className={styles.link}>Мій профіль</Link>
                  <button onClick={handleLogout} className={styles.linkButton}>
                    Вийти
                  </button>
                </>
              ) : (
                <>
                  <Link href="/frontend/login" className={styles.link}>Увійти</Link>
                  <Link href="/frontend/users/new" className={styles.link}>Реєстрація</Link>
                </>
              )}
            </nav>
          </div>

        </div>

        <div className={styles.bottom}>
          <p className={styles.copyright}>© 2026 Kindred. Дипломний проект.</p>
        </div>
      </div>
    </footer>
  );
}
