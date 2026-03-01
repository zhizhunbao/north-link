/**
 * Vitest test setup — global mocks and testing-library matchers.
 */
import "@testing-library/jest-dom";

/* Mock localStorage */
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = String(value);
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

/* Mock window.location */
Object.defineProperty(window, "location", {
  writable: true,
  value: { href: "", pathname: "/" },
});

/* Mock import.meta.env */
(import.meta as Record<string, unknown>).env = {
  VITE_API_URL: "http://localhost:8000",
};

/* Mock matchMedia for Ant Design */
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

/* Mock ResizeObserver for Ant Design Table/Charts */
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock;

/* Mock getComputedStyle for Ant Design */
const originalGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = (element: Element, pseudoElt?: string | null) => {
  const style = originalGetComputedStyle(element, pseudoElt);
  return {
    ...style,
    getPropertyValue: (prop: string) => style.getPropertyValue(prop) || "",
  };
};
