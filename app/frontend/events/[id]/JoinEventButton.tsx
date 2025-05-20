"use client";

import { useEffect, useState } from "react";

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
      <div className="mt-4">
        <p className="text-blue-600 font-semibold">Ви є автором цієї події.</p>
        {participants.length > 0 ? (
          <div className="mt-2">
            <p className="font-medium">Учасники події:</p>
            <ul className="list-disc list-inside">
              {participants.map((name, idx) => (
                <li key={idx}>{name}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="mt-2 text-sm">Поки що немає учасників.</p>
        )}
      </div>
    );
  }

  return (
    <div className="mt-4">
      {joined ? (
        <button
          onClick={handleLeave}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Вийти з події
        </button>
      ) : (
        <button
          onClick={handleJoin}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Прийняти участь
        </button>
      )}
      {message && <p className="mt-2 text-sm">{message}</p>}
    </div>
  );
}
