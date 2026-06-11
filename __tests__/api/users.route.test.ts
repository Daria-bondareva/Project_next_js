/**
 * @jest-environment node
 *
 * Юніт-тести route-handler'а реєстрації (app/api/users/route.ts, метод POST).
 *
 * Перевіряємо вхідну валідацію, захист від дублікатів і «щасливий шлях»:
 *   1) відсутнє обовʼязкове поле → 400;
 *   2) username уже зайнятий → 400;
 *   3) коректні дані → 201, пароль хешується, а не зберігається у відкритому вигляді.
 *
 * Mongoose-модель User та bcrypt замокані.
 */
import { POST } from "@/app/api/users/route";
import User from "@/lib/models/User";
import bcrypt from "bcrypt";

jest.mock("@/lib/mongodb", () => ({ connectDB: jest.fn().mockResolvedValue(undefined) }));

// User мокаємо як конструктор зі статичним findOne і методом save в інстансі
jest.mock("@/lib/models/User", () => {
  const UserMock: any = jest.fn().mockImplementation((data: any) => ({
    ...data,
    save: jest.fn().mockResolvedValue({
      _id: "new-user-id",
      username: data.username,
      email: data.email,
    }),
  }));
  UserMock.findOne = jest.fn();
  return { __esModule: true, default: UserMock };
});

jest.mock("bcrypt", () => ({ hash: jest.fn() }));

function buildRequest(body: unknown) {
  return new Request("http://localhost/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

describe("POST /api/users — реєстрація нового користувача", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("edge-case: повертає 400, якщо не передано пароль (неповні дані)", async () => {
    // Arrange — username і email є, password відсутній
    const res = await POST(buildRequest({ username: "dasha", email: "d@test.com" }));
    const body = await res.json();

    // Assert
    expect(res.status).toBe(400);
    expect(body.error).toBe("Username, email, and password are required");
    // До перевірки БД не доходимо
    expect(User.findOne).not.toHaveBeenCalled();
  });

  it("повертає 400, якщо користувач із таким username уже існує", async () => {
    // Arrange
    (User.findOne as jest.Mock).mockResolvedValue({ _id: "existing", username: "dasha" });

    // Act
    const res = await POST(
      buildRequest({ username: "dasha", email: "d@test.com", password: "secret" })
    );
    const body = await res.json();

    // Assert
    expect(res.status).toBe(400);
    expect(body.error).toBe("Користувач з таким іменем вже існує");
    // Хешування й створення не виконуються
    expect(bcrypt.hash).not.toHaveBeenCalled();
  });

  it("за коректних даних повертає 201 і хешує пароль перед збереженням", async () => {
    // Arrange
    (User.findOne as jest.Mock).mockResolvedValue(null);
    (bcrypt.hash as jest.Mock).mockResolvedValue("hashed-password");

    // Act
    const res = await POST(
      buildRequest({ username: "dasha", email: "d@test.com", password: "secret" })
    );
    const body = await res.json();

    // Assert
    expect(res.status).toBe(201);
    expect(body.message).toBe("Користувач створений");
    expect(body.user).toEqual({
      id: "new-user-id",
      username: "dasha",
      email: "d@test.com",
    });

    // Пароль саме хешується (10 раундів), а у конструктор моделі
    // потрапляє passwordHash, а не сирий пароль
    expect(bcrypt.hash).toHaveBeenCalledWith("secret", 10);
    expect(User).toHaveBeenCalledWith({
      username: "dasha",
      email: "d@test.com",
      passwordHash: "hashed-password",
    });
  });
});
