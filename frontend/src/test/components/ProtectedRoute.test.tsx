/**
 * Unit tests for ProtectedRoute component.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../../components/auth/ProtectedRoute";

/* Mock useAuthStore */
vi.mock("../../stores/useAuthStore", () => ({
  useAuthStore: vi.fn(),
}));

import { useAuthStore } from "../../stores/useAuthStore";

const mockedUseAuthStore = vi.mocked(useAuthStore);

function renderWithRouter(isAuthenticated: boolean) {
  mockedUseAuthStore.mockImplementation((selector: unknown) => {
    const state = { isAuthenticated };
    return typeof selector === "function"
      ? (selector as (s: typeof state) => unknown)(state)
      : state;
  });

  return render(
    <MemoryRouter initialEntries={["/protected"]}>
      <Routes>
        <Route
          path="/login"
          element={<div data-testid="login-page">Login</div>}
        />
        <Route element={<ProtectedRoute />}>
          <Route
            path="/protected"
            element={<div data-testid="protected-content">Protected</div>}
          />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders child route when authenticated", () => {
    renderWithRouter(true);
    expect(screen.getByTestId("protected-content")).toBeInTheDocument();
    expect(screen.queryByTestId("login-page")).not.toBeInTheDocument();
  });

  it("redirects to /login when not authenticated", () => {
    renderWithRouter(false);
    expect(screen.getByTestId("login-page")).toBeInTheDocument();
    expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
  });
});
