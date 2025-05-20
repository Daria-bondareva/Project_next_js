import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import User from "@/lib/models/User";
import { NextResponse } from "next/server";

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
    filter.title = { $regex: search, $options: "i" }; // Case-insensitive search
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
  await connectDB();
  const { title, date, userId } = await req.json();

  if (!title || !date || !userId) {
    return NextResponse.json(
      { error: "Title, date, and userId are required" },
      { status: 400 }
    );
  }

  const userExists = await User.findById(userId);
  if (!userExists) {
    return NextResponse.json({ error: "Invalid userId" }, { status: 400 });
  }

  const newEvent = new Event({
    title,
    date: new Date(date),
    userId });
  const savedEvent = await newEvent.save();
  await savedEvent.populate("userId", "username");
  return NextResponse.json(savedEvent);
}
