/**
 * Юніт-тести компонента TagSelectionModal (components/TagSelectionModal.tsx).
 *
 * Компонент містить нетривіальну логіку стану: перенесення тегів між
 * списками "Вибрані" / "Доступні", порожній стан і збереження результату.
 * Тестуємо саме поведінку, а не верстку.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TagSelectionModal from "@/components/TagSelectionModal";

const ALL_TAGS = ["СПОРТ", "IT", "МУЗИКА"];

// Базові пропси; у конкретному тесті перевизначаємо потрібні
function setup(overrides: Partial<React.ComponentProps<typeof TagSelectionModal>> = {}) {
  const onSave = jest.fn();
  const onClose = jest.fn();
  const props = {
    isOpen: true,
    onClose,
    onSave,
    initialSelected: [],
    allTags: ALL_TAGS,
    ...overrides,
  };
  render(<TagSelectionModal {...props} />);
  return { onSave, onClose };
}

describe("TagSelectionModal — модальне вікно вибору тегів", () => {
  it("edge-case: не рендериться нічого, коли isOpen=false", () => {
    // Arrange + Act
    const { onSave } = setup({ isOpen: false });

    // Assert — заголовок модалки відсутній у DOM
    expect(screen.queryByText("Вибір тегів")).not.toBeInTheDocument();
    expect(onSave).not.toHaveBeenCalled();
  });

  it("edge-case: за порожнього початкового вибору показує плейсхолдер «Пусто...»", () => {
    // Arrange + Act
    setup({ initialSelected: [] });

    // Assert
    expect(screen.getByText("Пусто...")).toBeInTheDocument();
  });

  it("переносить тег із «Доступні» у «Вибрані» при кліку (toggle on)", async () => {
    // Arrange
    // delay: null — прибирає внутрішні таймери user-event, які інакше
    // спричиняють попередження "update was not wrapped in act(...)"
    const user = userEvent.setup({ delay: null });
    setup({ initialSelected: [] });

    // Act — клікаємо доступний тег "IT"
    await user.click(screen.getByText("IT"));

    // Assert — серед вибраних з'явився бейдж "IT ✕"
    expect(screen.getByText("IT ✕")).toBeInTheDocument();
    // і плейсхолдера порожнечі вже немає
    expect(screen.queryByText("Пусто...")).not.toBeInTheDocument();
  });

  it("прибирає тег із «Вибрані» при повторному кліку (toggle off)", async () => {
    // Arrange — IT вже вибраний
    // delay: null — прибирає внутрішні таймери user-event, які інакше
    // спричиняють попередження "update was not wrapped in act(...)"
    const user = userEvent.setup({ delay: null });
    setup({ initialSelected: ["IT"] });
    expect(screen.getByText("IT ✕")).toBeInTheDocument();

    // Act — клік по вибраному бейджу знімає вибір
    await user.click(screen.getByText("IT ✕"));

    // Assert — список вибраних знову порожній
    expect(screen.queryByText("IT ✕")).not.toBeInTheDocument();
    expect(screen.getByText("Пусто...")).toBeInTheDocument();
  });

  it("при «Зберегти» передає актуальний вибір у onSave і закриває вікно", async () => {
    // Arrange
    // delay: null — прибирає внутрішні таймери user-event, які інакше
    // спричиняють попередження "update was not wrapped in act(...)"
    const user = userEvent.setup({ delay: null });
    const { onSave, onClose } = setup({ initialSelected: ["СПОРТ"] });

    // Act — додаємо ще "МУЗИКА" і зберігаємо
    await user.click(screen.getByText("МУЗИКА"));
    await user.click(screen.getByRole("button", { name: "Зберегти" }));

    // Assert — onSave отримав обидва теги, вікно закрилось
    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onSave).toHaveBeenCalledWith(["СПОРТ", "МУЗИКА"]);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("edge-case: «Відмінити» закриває вікно без виклику onSave", async () => {
    // Arrange
    // delay: null — прибирає внутрішні таймери user-event, які інакше
    // спричиняють попередження "update was not wrapped in act(...)"
    const user = userEvent.setup({ delay: null });
    const { onSave, onClose } = setup({ initialSelected: ["IT"] });

    // Act
    await user.click(screen.getByRole("button", { name: "Відмінити" }));

    // Assert — зміни не зберігаються
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(onSave).not.toHaveBeenCalled();
  });
});
