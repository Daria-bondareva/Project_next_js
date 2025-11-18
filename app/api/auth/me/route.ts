import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import { connectDB } from "@/lib/mongodb";
import Event from "@/lib/models/Event";
import User from "@/lib/models/User";

export async function GET() {
  const token = (await cookies()).get("token")?.value;

  if (!token) {
    return NextResponse.json({ error: "Авторизуйтесь перед виконанням цієї дії " }, { status: 401 });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string, username: string, email: string };

    await connectDB();

    const user = await User.findById(decoded.userId).select("-passwordHash");
    if (!user) {
        return NextResponse.json({ error: "Користувача не знайдено" }, { status: 404 });
    }
    
    const events = await Event.find({ userId: decoded.userId }).sort({ date: -1 });

    return NextResponse.json({
      user: user,
      events,
    });

  } catch {
    return NextResponse.json({ error: "Недійсний токен" }, { status: 401 });
  }
}

export async function PATCH(req: Request) {
  const token = (await cookies()).get("token")?.value;

  if (!token) {
    return NextResponse.json({ error: "Авторизуйтесь" }, { status: 401 });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    
    // Отримуємо інтереси з тіла запиту
    const { interests } = await req.json();

    if (!Array.isArray(interests)) {
        return NextResponse.json({ error: "Інтереси мають бути масивом" }, { status: 400 });
    }

    await connectDB();

    // Знаходимо і оновлюємо користувача
    const updatedUser = await User.findByIdAndUpdate(
      decoded.userId,
      { $set: { interests: interests } }, // $set оновлює тільки це поле
      { new: true } // Повернути оновлений документ
    ).select("-passwordHash"); // Не повертати хеш пароля

    if (!updatedUser) {
        return NextResponse.json({ error: "Користувача не знайдено" }, { status: 404 });
    }

    return NextResponse.json({ user: updatedUser });

  } catch(err) {
    console.error(err);
    return NextResponse.json({ error: "Недійсний токен або помилка сервера" }, { status: 401 });
  }
}
