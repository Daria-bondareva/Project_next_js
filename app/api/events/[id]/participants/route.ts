// /app/api/events/[id]/participants/route.ts
import { NextResponse } from "next/server";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import User from "@/lib/models/User";
import jwt from "jsonwebtoken";

type EventWithParticipants = {
  _id: string;
  participants: { username: string }[];
};

export async function GET(_: Request, { params }: { params: { id: string } }) {
  await connectDB();

  const event = await Event.findById(params.id)
    .populate("participants", "username")
    .lean() as EventWithParticipants | null;

  if (!event || !event.participants) {
    return NextResponse.json([]);
  }

  const usernames = event.participants.map((user) => user.username);
  return NextResponse.json(usernames);
}

export async function PATCH(req: Request, { params }: { params: { id: string } }) {
  await connectDB();
  const token = req.headers.get("cookie")?.split("token=")[1]?.split(";")[0];

  if (!token) return NextResponse.json({ error: "Не авторизований" }, { status: 401 });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };

    const event = await Event.findById(params.id);
    if (!event) return NextResponse.json({ error: "Подію не знайдено" }, { status: 404 });

    // Видаляємо користувача з масиву учасників
    event.participants = event.participants.filter(
      (id: any) => String(id) !== decoded.userId
    );

    await event.save();

    return NextResponse.json({ message: "Ви вийшли з події" });
  } catch {
    return NextResponse.json({ error: "Недійсний токен" }, { status: 401 });
  }
}
