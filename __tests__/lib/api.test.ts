/**
 * Юніт-тести клієнтського шару API (lib/api.ts).
 *
 * Перевіряємо, що функції коректно формують запит, повертають дані
 * та пробрасують осмислену помилку, коли сервер відповідає невдало.
 * Мережа повністю замокана через global.fetch — тести ізольовані.
 */
import { createUser, fetchEvents } from "@/lib/api";

describe("lib/api — клієнтський шар звернень до бекенду", () => {
  // Підміняємо глобальний fetch перед кожним тестом, щоб не ходити в мережу
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe("createUser", () => {
    it("надсилає POST на /api/users з JSON-тілом і повертає створеного користувача", async () => {
      // Arrange
      const payload = { username: "dasha", email: "d@test.com", password: "secret" };
      const serverResponse = { message: "Користувач створений", user: { id: "1" } };
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => serverResponse,
      });

      // Act
      const result = await createUser(payload);

      // Assert
      expect(global.fetch).toHaveBeenCalledWith("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      expect(result).toEqual(serverResponse);
    });

    it("edge-case: при помилці сервера пробрасує саме текст помилки з відповіді", async () => {
      // Arrange — сервер повертає 400 з полем error (напр., дублікат імені)
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        json: async () => ({ error: "Користувач з таким іменем вже існує" }),
      });

      // Act + Assert
      await expect(
        createUser({ username: "dasha", email: "d@test.com", password: "x" })
      ).rejects.toThrow("Користувач з таким іменем вже існує");
    });

    it("edge-case: якщо сервер не дав поля error — кидає дефолтне повідомлення", async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        json: async () => ({}),
      });

      // Act + Assert
      await expect(
        createUser({ username: "x", email: "x@x.com", password: "x" })
      ).rejects.toThrow("Помилка при створенні користувача");
    });
  });

  describe("fetchEvents", () => {
    it("повертає список подій та підставляє query-рядок у URL", async () => {
      // Arrange
      const events = [{ _id: "1", title: "Подія" }];
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => events,
      });

      // Act
      const result = await fetchEvents("sort=date_asc");

      // Assert
      expect(global.fetch).toHaveBeenCalledWith("/api/events?sort=date_asc");
      expect(result).toEqual(events);
    });

    it("edge-case: при невдалій відповіді (ok=false) кидає помилку завантаження", async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false });

      // Act + Assert
      await expect(fetchEvents()).rejects.toThrow("Не вдалося завантажити події");
    });
  });
});
