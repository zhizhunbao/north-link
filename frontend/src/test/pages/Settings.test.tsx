/**
 * Unit tests for SettingsPage component.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { SettingsPage } from "../../pages/Settings/Settings";

/* Mock authService */
vi.mock("../../services/authService", () => ({
  authService: {
    changePassword: vi.fn(),
    getProfile: vi.fn(),
  },
}));

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
    },
  };
});

import { useAuthStore } from "../../stores/useAuthStore";

const mockedUseAuthStore = vi.mocked(useAuthStore);

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAuthStore.mockImplementation((selector: unknown) => {
      const state = { logout: vi.fn() };
      return typeof selector === "function"
        ? (selector as (s: typeof state) => unknown)(state)
        : state;
    });
  });

  it("renders page heading", () => {
    render(<SettingsPage />);
    expect(screen.getByText(/系统设置/)).toBeInTheDocument();
  });

  it("renders system params tab", () => {
    render(<SettingsPage />);
    expect(screen.getByText("系统参数")).toBeInTheDocument();
  });

  it("renders password change tab", () => {
    render(<SettingsPage />);
    expect(screen.getByText("密码修改")).toBeInTheDocument();
  });

  it("renders tariff settings card", () => {
    render(<SettingsPage />);
    expect(screen.getByText("税率设置")).toBeInTheDocument();
  });

  it("renders exchange rate card", () => {
    render(<SettingsPage />);
    expect(screen.getByText("汇率配置")).toBeInTheDocument();
  });

  it("renders freight template card", () => {
    render(<SettingsPage />);
    expect(screen.getByText("运费模板")).toBeInTheDocument();
  });

  it("renders save button", () => {
    render(<SettingsPage />);
    expect(screen.getByText("保存设置")).toBeInTheDocument();
  });

  it("renders data export button", () => {
    render(<SettingsPage />);
    expect(screen.getByText("数据备份导出")).toBeInTheDocument();
  });
});
