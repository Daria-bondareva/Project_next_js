import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";

export async function GET() {
  const token = (await cookies()).get("token")?.value;

  if (!token) {
    return NextResponse.json({ error: "Авторизуйтесь перед виконанням цієї дії " }, { status: 401 });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string, username: string, email: string };

    await connectDB();
    
    const events = await Event.find({ userId: decoded.userId }).sort({ date: -1 });

    return NextResponse.json({
      user: { userId: decoded.userId, username: decoded.username, email: decoded.email },
      events,
    });

  } catch {
    return NextResponse.json({ error: "Недійсний токен" }, { status: 401 });
  }
}
