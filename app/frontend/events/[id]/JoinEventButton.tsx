"use client";

import { useEffect, useState } from "react";
import Button from "@/components/ui/Button";
import styles from "@/app/frontend/css/EventButtons.module.css";

export default function JoinEventButton({ eventId }: { eventId: string }) {
  const [joined, setJoined] = useState(false);
  const [isAuthor, setIsAuthor] = useState(false);
  const [participants, setParticipants] = useState<string[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const checkStatus = async () => {
      const res = await fetch(`/api/events/${eventId}/isJoined`);
      const data = await res.json();
      setJoined(data.joined);
      setIsAuthor(data.isAuthor);

      if (data.isAuthor) {
        const usersRes = await fetch(`/api/events/${eventId}/participants`);
        const users = await usersRes.json();
        setParticipants(users);
      }
    };

    checkStatus();
  }, [eventId]);

  const handleJoin = async () => {
    const res = await fetch(`/api/events/${eventId}/join`, { method: "POST" });
    const data = await res.json();
    setMessage(data.message || data.error);
    setJoined(true);
  };

  const handleLeave = async () => {
    const res = await fetch(`/api/events/${eventId}/participants`, { method: "PATCH" });
    const data = await res.json();
    setMessage(data.message || data.error);
    setJoined(false);
  };

  if (isAuthor) {
    return (
      <div className={styles.container}>
        <p className={styles.authorNote}>Ви є автором цієї події.</p>
        {participants.length > 0 ? (
          <div>
            <p className={styles.participantsTitle}>Учасники події:</p>
            <ul className={styles.participantsList}>
              {participants.map((name, idx) => (
                <li key={idx} className={styles.participantItem}>{name}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className={styles.noParticipants}>Поки що немає учасників.</p>
        )}
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {joined ? (
        <Button variant="danger" size="md" onClick={handleLeave}>
          Вийти з події
        </Button>
      ) : (
        <Button variant="primary" size="md" onClick={handleJoin}>
          Прийняти участь
        </Button>
      )}
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
}
