// /app/api/events/[id]/isJoined/route.ts
import { NextResponse } from "next/server";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import jwt from "jsonwebtoken";

type EventType = {
  _id: string;
  userId: string;
  participants: string[];
};

export async function GET(req: Request, { params }: { params: { id: string } }) {
  await connectDB();

  const token = req.headers.get("cookie")?.split("token=")[1]?.split(";")[0];
  if (!token) return NextResponse.json({ joined: false, isAuthor: false });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };

    const event = await Event.findById(params.id).lean() as EventType | null;
    if (!event) return NextResponse.json({ joined: false, isAuthor: false });

    const joined = event.participants?.some(id => id.toString() === decoded.userId);
    const isAuthor = event.userId.toString() === decoded.userId;

    return NextResponse.json({ joined, isAuthor });
  } catch {
    return NextResponse.json({ joined: false, isAuthor: false });
  }
}
