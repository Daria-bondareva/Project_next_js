// lib/api.ts

const API_URL = "http://localhost:3000/api";

// Функція для отримання користувачів
// lib/api.ts

export const fetchUsers = async (query: string = "") => {
  const response = await fetch(`/api/users?${query}`);
  if (!response.ok) {
    throw new Error("Не вдалося завантажити користувачів");
  }
  return response.json();
};



// Функція для отримання подій з можливістю фільтрації/сортування
export async function fetchEvents(query = "") {
  const res = await fetch(`/api/events?${query}`);
  if (!res.ok) {
    throw new Error("Не вдалося завантажити події");
  }
  return res.json();
}

const fetchUserProfile = async (userId: string) => {
  const userRes = await fetch(`/api/users/${userId}`);
  const user = await userRes.json();

  const eventsRes = await fetch(`/api/events?userId=${userId}`);
  const events = await eventsRes.json();

  return { user, events };
};


// Функція для створення події
export async function createEvent(data: {
  title: string;
  date: string;
  userId: string;
}) {
  const res = await fetch(`${API_URL}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error("Помилка при створенні події");
  }

  return res.json();
}

// lib/api.ts
export async function createUser(data: { username: string; email: string; password: string }) {
  const res = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const responseData = await res.json();
  if (!res.ok) {
    // Повертаємо текст помилки з сервера (якщо є)
    const errorMessage = responseData.error || "Помилка при створенні користувача";
    throw new Error(errorMessage);
  }

  return responseData;
}

