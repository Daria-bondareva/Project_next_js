'use client';

import { useRouter } from 'next/navigation';
import styles from "@/app/frontend/css/EventButtons.module.css"

export default function DeleteEventButton({ eventId }: { eventId: string }) {
  const router = useRouter();

  const handleDelete = async () => {
    const confirmed = confirm('Ви впевнені, що хочете видалити цю подію?');
    if (!confirmed) return;

    const res = await fetch(`/api/events/${eventId}`, {
      method: 'DELETE',
    });

    if (res.ok) {
      alert('Подію видалено');
      router.push('/frontend/events'); // зміни шлях, якщо список подій в іншому місці
    } else {
      alert('Помилка при видаленні події');
    }
  };

  return (
    <button
      onClick={handleDelete}
      className={`${styles.button} ${styles.leave}`}
    >
      Видалити
    </button>
  );
}
