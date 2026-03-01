/**
 * Unit tests for LoginPage component.
 * Covers render, form submission success and error paths.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LoginPage } from "../../pages/Login/Login";

const mockNavigate = vi.fn();

/* Mock react-router-dom navigate */
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

/* Mock useAuthStore */
vi.mock("../../stores/useAuthStore", () => ({
  useAuthStore: vi.fn(),
}));

/* Mock antd message */
vi.mock("antd", async (importOriginal) => {
  const actual = await importOriginal<typeof import("antd")>();
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
    },
  };
});

import { useAuthStore } from "../../stores/useAuthStore";
import { message } from "antd";

const mockedUseAuthStore = vi.mocked(useAuthStore);

function renderLogin(mockLogin = vi.fn()) {
  mockedUseAuthStore.mockImplementation((selector: unknown) => {
    const state = { login: mockLogin };
    return typeof selector === "function"
      ? (selector as (s: typeof state) => unknown)(state)
      : state;
  });

  const result = render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );

  return { ...result, mockLogin };
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders login form with brand", () => {
    renderLogin();
    expect(screen.getByText("North Link")).toBeInTheDocument();
    expect(screen.getByText(/跨境货源通/)).toBeInTheDocument();
  });

  it("renders username input", () => {
    renderLogin();
    const input = screen.getByTestId("login-username");
    expect(input).toBeInTheDocument();
  });

  it("renders password input", () => {
    renderLogin();
    const input = screen.getByTestId("login-password");
    expect(input).toBeInTheDocument();
  });

  it("renders submit button", () => {
    renderLogin();
    const button = screen.getByTestId("login-submit");
    expect(button).toBeInTheDocument();
    expect(button.textContent).toMatch(/登.*录/);
  });

  it("renders logo 'N'", () => {
    renderLogin();
    const logo = screen.getByText("N");
    expect(logo).toBeInTheDocument();
    expect(logo.className).toContain("login-logo");
  });

  it("calls login and navigates on successful submit", async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined);
    renderLogin(mockLogin);

    fireEvent.change(screen.getByTestId("login-username"), {
      target: { value: "admin" },
    });
    fireEvent.change(screen.getByTestId("login-password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("admin", "password123");
    });

    await waitFor(() => {
      expect(message.success).toHaveBeenCalledWith("登录成功");
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/", { replace: true });
    });
  });

  it("shows error message on login failure", async () => {
    const mockLogin = vi
      .fn()
      .mockRejectedValue(new Error("Invalid credentials"));
    renderLogin(mockLogin);

    fireEvent.change(screen.getByTestId("login-username"), {
      target: { value: "wrong" },
    });
    fireEvent.change(screen.getByTestId("login-password"), {
      target: { value: "bad" },
    });
    fireEvent.click(screen.getByTestId("login-submit"));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("wrong", "bad");
    });

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith(
        "登录失败，请检查用户名和密码",
      );
    });

    /* Should NOT navigate on failure */
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
