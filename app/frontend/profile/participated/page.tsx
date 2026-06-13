import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import { getCurrentUser } from "@/lib/getCurrentUser";
import styles from "@/app/frontend/css/ParticipatedEvents.module.css";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

const partitionUpcomingFirst = <T extends { date: string | Date }>(list: T[]): T[] => {
  const isPast = (e: T) => new Date(e.date).getTime() - Date.now() < 0;
  return [...list.filter((e) => !isPast(e)), ...list.filter(isPast)];
};

export default async function ParticipatedEventsPage() {
  await connectDB();

  const currentUser = await getCurrentUser();
  if (!currentUser) {
    return <p className="p-4 text-red-500">Будь ласка, увійдіть у систему.</p>;
  }

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
          {partitionUpcomingFirst(events).map((event) => {
            const daysUntil = (new Date(event.date).getTime() - Date.now()) / 86_400_000;
            const isSoon = daysUntil >= 0 && daysUntil <= 7;
            const isPast = daysUntil < 0;

            return (
              <li key={String(event._id)} className={styles.eventCard}>
                <div>
                  <div className={styles.eventTitleRow}>
                    <h2 className={styles.eventTitle}>{event.title}</h2>

                    {(isSoon || isPast) && (
                      <div className={styles.eventBadges}>
                        {isSoon && <Badge variant="accent">Скоро</Badge>}
                        {isPast && <Badge variant="muted">Завершено</Badge>}
                      </div>
                    )}
                  </div>
                  <p className={styles.eventDate}>
                    {new Date(event.date).toLocaleString()}
                  </p>
                </div>
                <Button variant="ghost" size="sm" href={`/frontend/events/${String(event._id)}`}>
                  Переглянути
                </Button>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
