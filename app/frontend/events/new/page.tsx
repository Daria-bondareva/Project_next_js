"use client";

import { useState, useEffect } from "react";
import { createEvent } from "@/lib/api";
import { useRouter } from "next/navigation";
import styles from "@/app/frontend/css/EditEventPage.module.css";
import { ALL_TAGS } from "@/lib/constants";
import TagSelectionModal from "@/components/TagSelectionModal";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";

export default function NewEventPage() {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState<string[]>([]); // +++ Додаємо стан для тегів
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchCurrentUser = async () => {
  try {
    const res = await fetch("/api/auth/me", {
      credentials: "include", // ✅ дозволяє надсилати кукі з токеном
    });

    if (!res.ok) throw new Error("Not authenticated");

    const { user } = await res.json();
  } catch (err) {
    router.push("/frontend/login");
  } finally {
    setLoading(false);
  }
};

    fetchCurrentUser();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await createEvent({ title, date, tags: tags, description });
      router.push("/frontend/events");
    } catch (err) {
      setError("Не вдалося створити подію");
      console.error(err);
    }
  };

  if (loading) return <p>Завантаження...</p>;

  return (
    <main className={styles.container}>
      <h1 className={styles.title}>Створити нову подію</h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        <Input
          id="new-title"
          label="Назва"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <Input
          id="new-date"
          label="Дата"
          type="datetime-local"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />

        <div>
          <label htmlFor="new-description" className={styles.label}>
            Опис події
          </label>
          <textarea
            id="new-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={styles.textarea}
            rows={5}
            placeholder="Розкажіть детальніше, про що буде ця подія..."
          />
        </div>

        <div>
          <label className={styles.label}>Теги події</label>
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
            Обрати теги
          </Button>
        </div>

        <TagSelectionModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={(selected) => setTags(selected)}
          initialSelected={tags}
          allTags={ALL_TAGS}
          title="Оберіть теги для події"
        />

        {error && (
          <p style={{ color: "var(--color-danger-dark)", fontSize: "var(--text-sm)" }}>
            {error}
          </p>
        )}

        <Button type="submit" variant="primary" size="lg" style={{ width: "100%" }}>
          Створити
        </Button>

        <Button href="/frontend/events" variant="secondary" size="lg" style={{ width: "100%" }}>
          Назад
        </Button>
      </form>
    </main>
  );
}
