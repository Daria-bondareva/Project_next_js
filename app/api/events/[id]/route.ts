import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import { NextResponse } from "next/server";
import User from "@/lib/models/User";


export async function GET(_: Request, { params }: { params: { id: string } }) {
  await connectDB();
  const event = await Event.findById(params.id).populate("userId");
  if (!event) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(event);
}

export async function PUT(req: Request, { params }: { params: { id: string } }) {
    await connectDB();
    const { title, date, userId } = await req.json();
  
    const update: any = {};
  if (title) update.title = title;
  if (date) update.date = date;
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
  await connectDB();
  await Event.findByIdAndDelete(params.id);
  return NextResponse.json({ message: "Event deleted" });
}
