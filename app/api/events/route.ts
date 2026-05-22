import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import User from "@/lib/models/User";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

export async function GET(req: Request) {
  await connectDB();
  const { searchParams } = new URL(req.url);

  const userId = searchParams.get("userId");
  const sort = searchParams.get("sort"); // date_asc | date_desc
  const search = searchParams.get("search"); // text in title

  const filter: any = {};

  if (userId) {
    filter.userId = userId;
  }

  if (search) {
    const safeSearch = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    filter.$or = [
      { title: { $regex: safeSearch, $options: "i" } }, // Шукаємо в назві
      { tags: { $in: [new RegExp(safeSearch, "i")] } }  // АБО в тегах
    ];
  }

  let sortOption = {};
if (sort === "date_asc") {
  sortOption = { date: 1 };
} else if (sort === "date_desc") {
  sortOption = { date: -1 };
} else if (sort === "title_asc") {
  sortOption = { title: 1 };
} else if (sort === "title_desc") {
  sortOption = { title: -1 };
}


  const events = await Event.find(filter).sort(sortOption).populate("userId", "username");
  return NextResponse.json(events);
}

export async function POST(req: Request) {
  const token = (await cookies()).get("token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  let decoded: { userId: string };
  try {
    decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
  } catch {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  await connectDB();
  const { title, date, tags, description } = await req.json();

  if (!title || !date) {
    return NextResponse.json(
      { error: "Title and date are required" },
      { status: 400 }
    );
  }

  const newEvent = new Event({
    title,
    date: new Date(date),
    userId: decoded.userId,
    tags: tags,
    description });
  const savedEvent = await newEvent.save();
  await savedEvent.populate("userId", "username");
  return NextResponse.json(savedEvent);
}
