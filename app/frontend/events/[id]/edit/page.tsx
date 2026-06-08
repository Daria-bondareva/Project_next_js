'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from "@/app/frontend/css/EditEventPage.module.css";
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";

export default function EditEventPage({ params }: { params: { id: string } }) {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [description, setDescription] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
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
      setDate(new Date(data.date).toISOString().slice(0, 16));
      setTags(data.tags || []);
      setDescription(data.description || "");
    };

    fetchEvent();
  }, [params.id, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch(`/api/events/${params.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, date, tags, description }),
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
        <Input
          id="edit-title"
          label="Назва"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <Input
          id="edit-date"
          label="Дата"
          type="datetime-local"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />

        <div>
          <label htmlFor="edit-description" className={styles.label}>
            Опис
          </label>
          <textarea
            id="edit-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={styles.textarea}
            rows={5}
            placeholder="Розкажіть детальніше про подію..."
          />
        </div>

        <div>
          <label className={styles.label}>Теги</label>
          <div className={styles.tagRow}>
            {tags.length > 0 ? (
              tags.map((tag) => (
                <Badge key={tag} variant="filled">#{tag}</Badge>
              ))
            ) : (
              <span className={styles.noTags}>Теги не обрано</span>
            )}
          </div>
          <Button
            type="button"
            variant="secondary"
            size="md"
            style={{ width: "100%" }}
            onClick={() => setIsModalOpen(true)}
          >
            Редагувати теги
          </Button>
        </div>

        <TagSelectionModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={(selected) => setTags(selected)}
          initialSelected={tags}
          allTags={ALL_TAGS}
          title="Редагування тегів події"
        />

        <Button type="submit" variant="primary" size="lg" style={{ width: "100%" }}>
          Зберегти
        </Button>
      </form>
    </main>
  );
}
