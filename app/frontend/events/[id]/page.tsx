import { notFound } from "next/navigation";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import JoinEventButton from "./JoinEventButton"; 
import DeleteEventButton from "./DeleteEventButton";
import { getCurrentUser } from "@/lib/getCurrentUser"; 
import styles from "@/app/frontend/css/EventDetails.module.css"
import BackButton from "./BackButton";

type EventType = {
  _id: string;
  title: string;
  date: string;
  userId: {
    _id: string;
    username: string;
  };
  participants: string[]; 
  tags: string[];
  description?: string;
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
    <div className={styles.pageWrapper}>
  <BackButton />
    <main className={styles.wrapper}>
      
      <h1 className={styles.title}>{event.title}</h1>
      <p className={styles.text}><strong>Дата:</strong> {new Date(event.date).toLocaleString()}</p>

      {!isAuthor && (
        <p className={styles.text}>
          <strong>Автор:</strong> {event.userId.username}
        </p>
      )}

      {event.description && (
            <div style={{marginTop: '20px', padding: '15px', background: '#f9f9f9', borderRadius: '8px'}}>
                <h3 style={{fontSize: '1.1rem', marginBottom: '10px'}}>Про подію:</h3>
                <p style={{whiteSpace: 'pre-wrap', lineHeight: '1.5', color: '#444'}}>
                    {event.description}
                </p>
            </div>
        )}

      {/* +++ 2. ДОДАЙТЕ ЦЕЙ БЛОК ДЛЯ ВІДОБРАЖЕННЯ ТЕГІВ +++ */}
        {event.tags && event.tags.length > 0 && (
          // Вам потрібно буде створити стилі для .tagContainer та .tag
          <div className={styles.tagContainer}> 
            {event.tags.map((tag: string) => (
              <span key={tag} className={styles.tag}>
                #{tag}
              </span>
            ))}
          </div>
        )}
        {/* +++ КІНЕЦЬ БЛОКУ ТЕГІВ +++ */}
      <JoinEventButton eventId={String(event._id)} />

{isAuthor && (
  <div className={styles.actions}>
    <a
      href={`/frontend/events/${event._id}/edit`}
      className={styles.editButton}
    >
      Редагувати
    </a>
    <DeleteEventButton eventId={String(event._id)} />
  </div>
)}

    </main>
    </div>
  );
}
