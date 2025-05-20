import { NextResponse } from "next/server";
import { connectDB } from "@/lib/mongodb";
import Report from "@/lib/models/Report";
import jwt from "jsonwebtoken";
import { cookies } from "next/headers";

export async function POST(req: Request) {
  await connectDB();

  const token = (await cookies()).get("token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Не авторизований" }, { status: 401 });
  }

  let decoded;
  try {
    decoded = jwt.verify(token, process.env.JWT_SECRET!);
  } catch {
    return NextResponse.json({ error: "Недійсний токен" }, { status: 401 });
  }

  const { targetType, targetId, reason } = await req.json();

  if (!["User", "Event"].includes(targetType) || !targetId || !reason) {
    return NextResponse.json({ error: "Невірні дані" }, { status: 400 });
  }

  const report = await Report.create({
    reporterId: (decoded as any).userId,
    targetType,
    targetId,
    reason,
  });

  return NextResponse.json({ message: "Скаргу подано", report }, { status: 201 });
}
