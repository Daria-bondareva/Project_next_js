import { notFound } from "next/navigation";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import JoinEventButton from "./JoinEventButton"; // ✅ ЗАЛИШАЄМО ЦЕЙ
import DeleteEventButton from "./DeleteEventButton";
import { getCurrentUser } from "@/lib/getCurrentUser"; 

type EventType = {
  _id: string;
  title: string;
  date: string;
  userId: {
    _id: string;
    username: string;
  };
  participants: string[]; // ← додай оце!
};


export default async function EventDetailsPage({ params }: { params: { id: string } }) {
  await connectDB();

  const event = await Event.findById(params.id)
    .populate("userId", "username")
    .lean() as EventType | null;

  if (!event) return notFound();

  const currentUser = await getCurrentUser();
  const isAuthor = currentUser && currentUser.userId === String(event.userId._id);

  return (
    <main className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{event.title}</h1>
      <p><strong>Дата:</strong> {new Date(event.date).toLocaleString()}</p>

      {!isAuthor && (
        <p className="mt-4">
          <strong>Автор:</strong> {event.userId.username}
        </p>
      )}
      <JoinEventButton eventId={String(event._id)} />

{isAuthor && (
  <div className="mt-6 flex space-x-4">
    <a
      href={`/frontend/events/${event._id}/edit`}
      className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
    >
      Редагувати
    </a>
    <DeleteEventButton eventId={String(event._id)} />
  </div>
)}


    </main>
  );
}
