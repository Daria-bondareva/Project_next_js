/**
 * Юніт-тести функції getCurrentUser (lib/getCurrentUser.ts).
 *
 * Це критичний для безпеки шматок: він визначає, чи вважається запит
 * автентифікованим. Перевіряємо три гілки: валідний токен, відсутній токен
 * та підроблений/протермінований токен (jwt.verify кидає виняток).
 *
 * Зовнішні залежності next/headers (cookies) і jsonwebtoken замокані.
 */
import { getCurrentUser } from "@/lib/getCurrentUser";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

jest.mock("next/headers", () => ({
  cookies: jest.fn(),
}));

jest.mock("jsonwebtoken", () => ({
  verify: jest.fn(),
}));

// Хелпер: імітує cookieStore з потрібним токеном (або без нього)
function mockCookieToken(token: string | undefined) {
  (cookies as jest.Mock).mockResolvedValue({
    get: (name: string) =>
      name === "token" && token !== undefined ? { value: token } : undefined,
  });
}

describe("getCurrentUser — визначення поточного користувача за JWT-cookie", () => {
  beforeEach(() => {
    process.env.JWT_SECRET = "test-secret";
    jest.clearAllMocks();
  });

  it("повертає розшифровані дані користувача для валідного токена", async () => {
    // Arrange
    const decoded = { userId: "u1", username: "dasha", email: "d@test.com" };
    mockCookieToken("valid.jwt.token");
    (jwt.verify as jest.Mock).mockReturnValue(decoded);

    // Act
    const user = await getCurrentUser();

    // Assert
    expect(jwt.verify).toHaveBeenCalledWith("valid.jwt.token", "test-secret");
    expect(user).toEqual(decoded);
  });

  it("edge-case: повертає null, якщо cookie з токеном відсутній (гість)", async () => {
    // Arrange — токена в cookie немає
    mockCookieToken(undefined);

    // Act
    const user = await getCurrentUser();

    // Assert — до перевірки підпису навіть не доходимо
    expect(user).toBeNull();
    expect(jwt.verify).not.toHaveBeenCalled();
  });

  it("edge-case: повертає null, якщо токен підроблений/протермінований (verify кидає виняток)", async () => {
    // Arrange
    mockCookieToken("tampered.token");
    (jwt.verify as jest.Mock).mockImplementation(() => {
      throw new Error("invalid signature");
    });

    // Act
    const user = await getCurrentUser();

    // Assert — виняток проковтнуто, користувач не автентифікований
    expect(user).toBeNull();
  });
});
