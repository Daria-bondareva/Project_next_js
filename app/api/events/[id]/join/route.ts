import { NextResponse } from "next/server";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import jwt from "jsonwebtoken";

export async function POST(req: Request, { params }: { params: { id: string } }) {
  await connectDB();
  const token = req.headers.get("cookie")?.split("token=")[1]?.split(";")[0];

  if (!token) return NextResponse.json({ error: "Не авторизований" }, { status: 401 });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };

    const event = await Event.findById(params.id);
    if (!event) return NextResponse.json({ error: "Подію не знайдено" }, { status: 404 });

    if (event.participants?.includes(decoded.userId)) {
      return NextResponse.json({ message: "Ви вже приєдналися до цієї події." });
    }

    event.participants.push(decoded.userId);
    await event.save();

    return NextResponse.json({ message: "Успішно доєднано до події" });
  } catch {
    return NextResponse.json({ error: "Недійсний токен" }, { status: 401 });
  }
}
