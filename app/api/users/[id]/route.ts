import { connectDB } from "@/lib/mongodb";
import User from "@/lib/models/User";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

export async function GET(_: Request, { params }: { params: { id: string } }) {
  await connectDB();
  const user = await User.findById(params.id).select("-passwordHash");
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(user);
}

export async function PUT(req: Request, { params }: { params: { id: string } }) {
  const token = (await cookies()).get("token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  try { jwt.verify(token, process.env.JWT_SECRET!); }
  catch { return NextResponse.json({ error: "Unauthorized" }, { status: 401 }); }

    await connectDB();
  const { username, email, interests } = await req.json();

  const update: any = {};
  if (username) update.username = username;
  if (email) update.email = email;
  if (interests) update.interests = interests;

  const updated = await User.findByIdAndUpdate(params.id, update, { new: true }).select("-passwordHash");
  return NextResponse.json(updated);
  }
  

export async function DELETE(_: Request, { params }: { params: { id: string } }) {
  const token = (await cookies()).get("token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  try { jwt.verify(token, process.env.JWT_SECRET!); }
  catch { return NextResponse.json({ error: "Unauthorized" }, { status: 401 }); }

  await connectDB();
  await User.findByIdAndDelete(params.id);
  return NextResponse.json({ message: "User deleted" });
}
