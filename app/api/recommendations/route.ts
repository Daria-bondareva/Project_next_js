import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

export async function GET() {
  // 1. Перевіряємо, чи користувач залогінений
  const token = (await cookies()).get("token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    // 2. Розшифровуємо токен, щоб дістати ID користувача
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    
    // 3. Звертаємося до Python-сервісу
    // використовуємо адресу 127.0.0.1:8000(для першої) і 127.0.0.1:8002 (для другої)
    const pythonServiceUrl = "http://127.0.0.1:8000"; 
    
    const res = await fetch(`${pythonServiceUrl}/recommendations/${decoded.userId}`, {
        cache: 'no-store' // Не кешуємо, щоб час доби (ранок/вечір) завжди був актуальний
    });
    
    if (!res.ok) {
        console.error("Python service error:", res.status);
        // Якщо Python мовчить, повертаємо пустий список (щоб сайт не впав)
        return NextResponse.json([]); 
    }

    const recommendations = await res.json();
    
    // 4. Віддаємо дані на фронтенд
    return NextResponse.json(recommendations);

  } catch (error) {
    console.error("Recommendation Error:", error);
    // У разі будь-якої помилки повертаємо пустий масив, щоб інтерфейс не зламався
    return NextResponse.json([], { status: 500 });
  }
}