"use client";

import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import JoinEventButton from "@/app/frontend/events/[id]/JoinEventButton";

type Props = {
  event: any;
  currentUserId: string;
};

export default function EventCard({ event, currentUserId }: Props) {
  const [participants, setParticipants] = useState<string[]>([]);

  useEffect(() => {
    const fetchParticipants = async () => {
      const res = await fetch(`/api/events/${event._id}/participants`);
      const data = await res.json();
      setParticipants(data);
    };

    fetchParticipants();
  }, [event._id]);

  const isAuthor = event.userId === currentUserId;

  return (
    <li style={{
      border: "1px solid var(--color-border)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-4)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-2)",
      background: "var(--color-surface)",
    }}>
      <h3 style={{
        fontWeight: 600,
        fontSize: "var(--text-base)",
        color: "var(--color-text)",
      }}>
        {event.title}
      </h3>

      <p style={{
        display: "flex",
        alignItems: "center",
        gap: "var(--space-1)",
        fontSize: "var(--text-sm)",
        color: "var(--color-text-secondary)",
      }}>
        <Calendar size={14} />
        {new Date(event.date).toLocaleString("uk-UA")}
      </p>

      {isAuthor ? (
        <p style={{
          color: "var(--color-primary-600)",
          fontWeight: 600,
          fontSize: "var(--text-sm)",
        }}>
          Ви є автором події
        </p>
      ) : (
        <JoinEventButton eventId={event._id} />
      )}

      {participants.length > 0 && (
        <div style={{
          marginTop: "var(--space-2)",
          fontSize: "var(--text-sm)",
          color: "var(--color-text-secondary)",
        }}>
          <p style={{ fontWeight: 500, marginBottom: "var(--space-1)" }}>Учасники:</p>
          <ul style={{ listStyle: "disc", paddingLeft: "var(--space-4)" }}>
            {participants.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </div>
      )}
    </li>
  );
}
