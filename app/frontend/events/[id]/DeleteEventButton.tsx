'use client';

import { useRouter } from 'next/navigation';
import Button from "@/components/ui/Button";

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
      router.push('/frontend/events');
    } else {
      alert('Помилка при видаленні події');
    }
  };

  return (
    <Button variant="danger" size="md" onClick={handleDelete}>
      Видалити
    </Button>
  );
}
