import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ message: "Вихід успішний" });
  response.cookies.set("token", "", {
    httpOnly: true,
    expires: new Date(0), // Видаляє кукі
    path: "/",
  });
  return response;
}
