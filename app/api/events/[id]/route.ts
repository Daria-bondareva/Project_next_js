import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import { NextResponse } from "next/server";
import User from "@/lib/models/User";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";


export async function GET(_: Request, { params }: { params: { id: string } }) {
  await connectDB();
  const event = await Event.findById(params.id).populate("userId", "username");
  if (!event) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(event);
}

export async function PUT(req: Request, { params }: { params: { id: string } }) {
  const token = (await cookies()).get("token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  try { jwt.verify(token, process.env.JWT_SECRET!); }
  catch { return NextResponse.json({ error: "Unauthorized" }, { status: 401 }); }

    await connectDB();
    const { title, date, userId, tags, description} = await req.json();
  
    const update: any = {};
  if (title) update.title = title;
  if (date) update.date = date;
  if (tags) update.tags = tags;
  if (description) update.description = description;
  if (userId) {
    const userExists = await User.findById(userId);
    if (!userExists) {
      return NextResponse.json({ error: "Invalid userId" }, { status: 400 });
    }
    update.userId = userId;
  }

  const updated = await Event.findByIdAndUpdate(params.id, update, { new: true });
  return NextResponse.json(updated);
  }
  

export async function DELETE(_: Request, { params }: { params: { id: string } }) {
  const token = (await cookies()).get("token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  try { jwt.verify(token, process.env.JWT_SECRET!); }
  catch { return NextResponse.json({ error: "Unauthorized" }, { status: 401 }); }

  await connectDB();
  await Event.findByIdAndDelete(params.id);
  return NextResponse.json({ message: "Event deleted" });
}
