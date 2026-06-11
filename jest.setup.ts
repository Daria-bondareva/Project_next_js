// Розширені матчери для роботи з DOM (toBeInTheDocument, toHaveTextContent ...)
import "@testing-library/jest-dom";

// Глушимо лише відоме хибнопозитивне попередження React/@testing-library
// "update ... was not wrapped in act(...)", яке зʼявляється через внутрішні
// таймери user-event v14 і не свідчить про реальну проблему в тестах.
// Решта помилок у консолі лишаються видимими.
const originalError = console.error;
beforeAll(() => {
  jest.spyOn(console, "error").mockImplementation((...args) => {
    if (typeof args[0] === "string" && args[0].includes("not wrapped in act")) {
      return;
    }
    originalError(...args);
  });
});

afterAll(() => {
  (console.error as jest.Mock).mockRestore();
});
