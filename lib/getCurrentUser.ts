import jwt from "jsonwebtoken";
import { cookies } from "next/headers";

export async function getCurrentUser() {
  const token = (await cookies()).get("token")?.value;
  if (!token) return null;

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
      userId: string;
      username: string;
      email: string;
    };

    return decoded;
  } catch {
    return null;
  }
}
