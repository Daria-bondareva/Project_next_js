import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import { getCurrentUser } from "@/lib/getCurrentUser";
import Link from "next/link";
import styles from "@/app/frontend/css/ParticipatedEvents.module.css"

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
    <main className={styles.container}>
      <h1 className={styles.title}>Я беру участь</h1>

      {events.length === 0 ? (
        <p className={styles.noEvents}>Ви ще не приєдналися до жодної події.</p>
      ) : (
        <ul className={styles.eventList}>
          {events.map((event) => (
            <li key={String(event._id)} className={styles.eventCard}>
              <div>
              <h2 className={styles.eventTitle}>{event.title}</h2>
              <p className={styles.eventDate}>
                {new Date(event.date).toLocaleString()}
              </p>
              </div>
              <Link
                href={`/frontend/events/${String(event._id)}`}
                className={styles.viewLink}
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
