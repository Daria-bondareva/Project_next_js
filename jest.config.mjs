import nextJest from "next/jest.js";

// Конфігурація Jest через офіційний хелпер Next.js.
// next/jest сам підхоплює next.config, .env, аляс "@/*" з tsconfig
// та трансформує TS/JSX через SWC.
const createJestConfig = nextJest({
  dir: "./",
});

/** @type {import('jest').Config} */
const customJestConfig = {
  // Підключаємо матчери @testing-library/jest-dom (toBeInTheDocument тощо)
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  // jsdom потрібен для тестування React-компонентів;
  // окремі тести route-handler'ів перемикаються на "node" через докблок.
  testEnvironment: "jest-environment-jsdom",
  // Шукаємо тести лише в каталозі __tests__
  testMatch: ["<rootDir>/__tests__/**/*.test.{ts,tsx}"],
  // Явно дублюємо аляс "@/*" із tsconfig, щоб його бачив і jest.mock(),
  // а не лише статичні import (next/jest у цій версії не додає його сам).
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
};

export default createJestConfig(customJestConfig);
