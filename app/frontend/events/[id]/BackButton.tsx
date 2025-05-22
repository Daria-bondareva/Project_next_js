"use client";

import { useRouter } from "next/navigation";
import styles from "@/app/frontend/css/EventDetails.module.css"; // або будь-який твій css

export default function BackButton() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.back()}
      className={styles.backButton}
      aria-label="Повернутися назад"
      title="Повернутися назад"
    >
      ←
    </button>
  );
}
