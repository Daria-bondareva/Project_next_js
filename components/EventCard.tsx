"use client";

import { useEffect, useState } from "react";
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
    <li className="border p-3 rounded space-y-1">
      <h3 className="font-semibold">{event.title}</h3>
      <p>Дата: {new Date(event.date).toLocaleString()}</p>

      {isAuthor ? (
        <div className="text-green-700 font-medium">Ви є автором події</div>
      ) : (
        <JoinEventButton eventId={event._id} />
      )}

      {participants.length > 0 && (
        <div className="mt-2 text-sm text-gray-700">
          <p>Учасники:</p>
          <ul className="list-disc list-inside">
            {participants.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </div>
      )}
    </li>
  );
}
