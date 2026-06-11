/**
 * @jest-environment node
 *
 * Юніт-тести route-handler'а автентифікації (app/api/auth/login/route.ts).
 *
 * Перевіряємо три ключові сценарії входу:
 *   1) користувача не знайдено → 401;
 *   2) невірний пароль → 401;
 *   3) успіх → 200 + httpOnly-cookie з JWT.
 *
 * БД (Mongoose-модель User), bcrypt і jsonwebtoken замокані —
 * жодних реальних звернень до бази чи криптографії.
 */
import { POST } from "@/app/api/auth/login/route";
import User from "@/lib/models/User";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

jest.mock("@/lib/mongodb", () => ({ connectDB: jest.fn().mockResolvedValue(undefined) }));
jest.mock("@/lib/models/User", () => ({ __esModule: true, default: { findOne: jest.fn() } }));
jest.mock("bcrypt", () => ({ compare: jest.fn() }));
jest.mock("jsonwebtoken", () => ({ sign: jest.fn() }));

// Хелпер: будує Request з JSON-тілом, як його отримує route
function buildRequest(body: unknown) {
  return new Request("http://localhost/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

describe("POST /api/auth/login — автентифікація користувача", () => {
  beforeEach(() => {
    process.env.JWT_SECRET = "test-secret";
    jest.clearAllMocks();
  });

  it("повертає 401, якщо користувача з таким username не існує", async () => {
    // Arrange
    (User.findOne as jest.Mock).mockResolvedValue(null);

    // Act
    const res = await POST(buildRequest({ username: "ghost", password: "x" }));
    const body = await res.json();

    // Assert
    expect(res.status).toBe(401);
    expect(body.error).toBe("Користувача не знайдено");
    // Пароль навіть не звіряємо, якщо юзера нема
    expect(bcrypt.compare).not.toHaveBeenCalled();
  });

  it("edge-case: повертає 401 при невірному паролі (bcrypt.compare → false)", async () => {
    // Arrange
    (User.findOne as jest.Mock).mockResolvedValue({
      _id: "u1",
      username: "dasha",
      passwordHash: "hash",
    });
    (bcrypt.compare as jest.Mock).mockResolvedValue(false);

    // Act
    const res = await POST(buildRequest({ username: "dasha", password: "wrong" }));
    const body = await res.json();

    // Assert
    expect(res.status).toBe(401);
    expect(body.error).toBe("Невірний пароль");
    // Токен не видається
    expect(jwt.sign).not.toHaveBeenCalled();
  });

  it("за коректних даних повертає 200 і встановлює httpOnly-cookie token", async () => {
    // Arrange
    (User.findOne as jest.Mock).mockResolvedValue({
      _id: "u1",
      username: "dasha",
      email: "d@test.com",
      passwordHash: "hash",
    });
    (bcrypt.compare as jest.Mock).mockResolvedValue(true);
    (jwt.sign as jest.Mock).mockReturnValue("signed.jwt.token");

    // Act
    const res = await POST(buildRequest({ username: "dasha", password: "correct" }));
    const body = await res.json();

    // Assert
    expect(res.status).toBe(200);
    expect(body.message).toBe("Успішний вхід");

    // Перевіряємо, що cookie token виставлено з прапорцем httpOnly
    const tokenCookie = res.cookies.get("token");
    expect(tokenCookie?.value).toBe("signed.jwt.token");
    expect(tokenCookie?.httpOnly).toBe(true);

    // JWT підписано із правильним payload та секретом
    expect(jwt.sign).toHaveBeenCalledWith(
      { userId: "u1", username: "dasha", email: "d@test.com" },
      "test-secret",
      { expiresIn: "1d" }
    );
  });
});
