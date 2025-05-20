import { connectDB } from "@/lib/mongodb";
import User from "@/lib/models/User";
import { NextResponse } from "next/server";
import bcrypt from "bcrypt";
import { SortOrder } from "mongoose";

export async function GET(req: Request) {
  await connectDB();
  const { searchParams } = new URL(req.url);
  const search = searchParams.get("search") || "";
  const sort = searchParams.get("sort") as SortOrder; // "asc" | "desc"

  const filter = {
    username: { $regex: search, $options: "i" },
  };

  const sortOption = sort ? { username: sort } : undefined;

  const users = await User.find(filter).sort(sortOption);
  return NextResponse.json(users);
}

export async function POST(req: Request) {
  await connectDB();
  const { username, email, password } = await req.json();

  if (!username || !email || !password) {
    return NextResponse.json(
      { error: "Username, email, and password are required" },
      { status: 400 }
    );
  }

  // Перевірка наявності користувача
  const existingUser = await User.findOne({ username });
  if (existingUser) {
    return NextResponse.json(
      { error: "Користувач з таким іменем вже існує" },
      { status: 400 }
    );
  }

  const passwordHash = await bcrypt.hash(password, 10);

  const newUser = new User({ username, email, passwordHash });
  const savedUser = await newUser.save();

  return NextResponse.json({
    message: "Користувач створений",
    user: {
      id: savedUser._id,
      username: savedUser.username,
      email: savedUser.email,
    },
  }, { status: 201 });
}
