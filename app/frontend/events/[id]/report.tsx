"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ReportEvent({ eventId }: { eventId: string }) {
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch("/api/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        targetType: "Event",
        targetId: eventId,
        reason,
      }),
    });

    const data = await res.json();

    if (res.ok) {
      setMessage("Скаргу подано успішно.");
      setReason("");
    } else {
      setMessage(data.error || "Помилка під час надсилання скарги.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 mt-6">
      <label className="block font-medium">Причина скарги:</label>
      <textarea
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        className="w-full border p-2 rounded"
        required
      />
      <button type="submit" className="bg-red-600 text-white px-4 py-2 rounded">
        Подати скаргу
      </button>
      {message && <p className="text-sm mt-2">{message}</p>}
    </form>
  );
}
