import { NextResponse } from "next/server";
import User from "@/lib/models/User";
import {connectDB} from "@/lib/mongodb";
import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";

export async function POST(req: Request) {
  await connectDB();
  const { username, password } = await req.json();

  const user = await User.findOne({ username });
  if (!user) {
    return NextResponse.json({ error: "Користувача не знайдено" }, { status: 401 });
  }

  const isMatch = await bcrypt.compare(password, user.passwordHash);
  if (!isMatch) {
    return NextResponse.json({ error: "Невірний пароль" }, { status: 401 });
  }

  const token = jwt.sign(
    { userId: user._id, username: user.username, email: user.email },
    process.env.JWT_SECRET!,
    { expiresIn: "1d" }
  );

  const response = NextResponse.json({ message: "Успішний вхід" });
  response.cookies.set("token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24, // 1 день
    path: "/",
  });

  return response;
}
