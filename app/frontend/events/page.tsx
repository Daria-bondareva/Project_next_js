"use client";

import { useEffect, useState } from "react";
import { fetchEvents } from "@/lib/api";
import { Calendar, User, ArrowUp, ArrowDown } from "lucide-react";
import pageStyles from "@/app/frontend/css/PageEvents.module.css";
import cardStyles from "@/app/frontend/css/EventCard.module.css";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";

type Event = {
  _id: string;
  title: string;
  date: string;
  tags?: string[];
  participants?: string[];
  userId: {
    _id: string;
    username: string;
  };
};

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [query, setQuery] = useState("");
  const [sortField, setSortField] = useState<"title" | "date">("title");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const sortOrder = `${sortField}_${sortDirection}`;

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
          const data = await res.json();
          setCurrentUserId(data.user?._id ?? null);
        }
      } catch {
        setCurrentUserId(null);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await fetchEvents(`${query}${query ? "&" : ""}sort=${sortOrder}`);
        setEvents(data);
      } catch (error) {
        console.error("Помилка при завантаженні подій", error);
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, [query, sortOrder]);

  const handleSearch = () => {
    setQuery(`search=${searchTerm}`);
  };

  return (
    <main className={pageStyles.page}>
      <h1 className={pageStyles.pageTitle}>Список подій</h1>

      <div className={pageStyles.filterPanel}>
        <div className={pageStyles.searchWrapper}>
          <Input
            id="events-search"
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Пошук за назвою або тегом..."
          />
        </div>

        <Button variant="primary" size="md" onClick={handleSearch}>
          Пошук
        </Button>

        <Button
          variant="secondary"
          size="md"
          onClick={() => setSortField((prev) => (prev === "title" ? "date" : "title"))}
        >
          {sortField === "title" ? "За назвою" : "За датою"}
        </Button>

        <Button
          variant="ghost"
          size="md"
          onClick={() => setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"))}
        >
          {sortDirection === "asc"
            ? <><ArrowUp size={14} /> Зростання</>
            : <><ArrowDown size={14} /> Спадання</>}
        </Button>
      </div>

      {loading ? (
        <p className={pageStyles.stateText}>Завантаження...</p>
      ) : events.length === 0 ? (
        <p className={pageStyles.stateText}>Немає подій.</p>
      ) : (
        <ul className={cardStyles.cardList}>
          {events.map((event) => {
            const isParticipant =
              currentUserId != null &&
              (event.participants ?? []).some((p) => String(p) === String(currentUserId));

            const daysUntil = (new Date(event.date).getTime() - Date.now()) / 86_400_000;
            const isSoon = daysUntil >= 0 && daysUntil <= 7;
            const isPast = daysUntil < 0;

            return (
            <li key={event._id} className={cardStyles.card}>
              <div className={cardStyles.cardBody}>
                <h3 className={cardStyles.cardHeader}>{event.title}</h3>

                {(isParticipant || isSoon || isPast) && (
                  <div className={cardStyles.tagsContainer}>
                    {isParticipant && <Badge variant="success">Ви берете участь</Badge>}
                    {isSoon && <Badge variant="accent">Скоро</Badge>}
                    {isPast && <Badge variant="muted">Завершено</Badge>}
                  </div>
                )}

                {event.tags && event.tags.length > 0 && (
                  <div className={cardStyles.tagsContainer}>
                    {event.tags.map((t) => (
                      <Badge key={t} variant="filled">#{t}</Badge>
                    ))}
                  </div>
                )}

                <p className={cardStyles.cardContent}>
                  <Calendar size={14} />
                  {new Date(event.date).toLocaleDateString("uk-UA")}
                </p>
                <p className={cardStyles.cardUser}>
                  <User size={14} />
                  {event.userId?.username || "Невідомо"}
                </p>
              </div>

              <Button
                variant="secondary"
                size="sm"
                href={`/frontend/events/${event._id}`}
                style={{ width: "100%" }}
              >
                Детальніше
              </Button>
            </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
