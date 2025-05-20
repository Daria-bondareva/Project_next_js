import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import { getCurrentUser } from "@/lib/getCurrentUser";
import Link from "next/link";

export default async function ParticipatedEventsPage() {
  await connectDB();

  const currentUser = await getCurrentUser();
  if (!currentUser) {
    return <p className="p-4 text-red-500">Будь ласка, увійдіть у систему.</p>;
  }

  // Знаходимо події, де userId є серед participants
  const events = await Event.find({ participants: currentUser.userId })
    .sort({ date: 1 })
    .lean();

  return (
    <main className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Я беру участь</h1>

      {events.length === 0 ? (
        <p>Ви ще не приєдналися до жодної події.</p>
      ) : (
        <ul className="space-y-4">
          {events.map((event) => (
            <li key={String(event._id)} className="border p-4 rounded shadow">
              <h2 className="text-xl font-semibold">{event.title}</h2>
              <p className="text-sm text-gray-600">
                {new Date(event.date).toLocaleString()}
              </p>
              <Link
                href={`/frontend/events/${String(event._id)}`}
                className="inline-block mt-2 text-blue-600 hover:underline"
              >
                Переглянути
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
