/**
 * @jest-environment node
 *
 * Юніт-тести route-handler'а рекомендацій (app/api/recommendations/route.ts).
 *
 * Цей ендпоінт — проксі між фронтендом і зовнішнім Python-сервісом (FastAPI).
 * Найважливіше тут — стійкість до збоїв: якщо рекомендаційний сервіс лежить
 * або повертає помилку, інтерфейс не повинен «падати». Перевіряємо:
 *   1) немає токена → 401;
 *   2) Python-сервіс недоступний (res.ok=false) → порожній масив, статус 200;
 *   3) успіх → проксіювання даних від сервісу.
 *
 * cookies, jwt і мережевий fetch до Python-сервісу замокані.
 */
import { GET } from "@/app/api/recommendations/route";
import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

jest.mock("next/headers", () => ({ cookies: jest.fn() }));
jest.mock("jsonwebtoken", () => ({ verify: jest.fn() }));

function mockToken(token: string | undefined) {
  (cookies as jest.Mock).mockResolvedValue({
    get: (name: string) =>
      name === "token" && token !== undefined ? { value: token } : undefined,
  });
}

describe("GET /api/recommendations — проксі до Python-сервісу рекомендацій", () => {
  beforeEach(() => {
    process.env.JWT_SECRET = "test-secret";
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("edge-case: повертає 401, якщо користувач не залогінений (немає cookie)", async () => {
    // Arrange
    mockToken(undefined);

    // Act
    const res = await GET();
    const body = await res.json();

    // Assert
    expect(res.status).toBe(401);
    expect(body.error).toBe("Unauthorized");
    // До зовнішнього сервісу не звертаємось
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("стійкість: якщо Python-сервіс відповів помилкою — повертає порожній масив (інтерфейс не падає)", async () => {
    // Arrange — токен валідний, але сервіс віддає 503
    mockToken("valid.token");
    (jwt.verify as jest.Mock).mockReturnValue({ userId: "u1" });
    (global.fetch as jest.Mock).mockResolvedValue({ ok: false, status: 503 });

    // Act
    const res = await GET();
    const body = await res.json();

    // Assert — деградація до порожнього списку без помилки
    expect(body).toEqual([]);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/recommendations/u1",
      { cache: "no-store" }
    );
  });

  it("за успішної відповіді проксіює список рекомендацій від сервісу", async () => {
    // Arrange
    const recommendations = [
      { _id: "e1", title: "Ранкова пробіжка" },
      { _id: "e2", title: "IT-лекція" },
    ];
    mockToken("valid.token");
    (jwt.verify as jest.Mock).mockReturnValue({ userId: "u1" });
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => recommendations,
    });

    // Act
    const res = await GET();
    const body = await res.json();

    // Assert
    expect(body).toEqual(recommendations);
  });
});
