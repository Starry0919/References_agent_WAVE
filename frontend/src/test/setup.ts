import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// vite.config.ts does not set test.globals, so @testing-library/react's
// own auto-cleanup (which only registers when `afterEach` is a global) never
// fires; without this, DOM from one test leaks into the next component test
// in the same file and getByRole() starts matching duplicates.
afterEach(() => {
  cleanup();
});
