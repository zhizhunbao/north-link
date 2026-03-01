/**
 * Unit tests for Axios API client — request/response interceptors.
 * Covers JWT injection, 401 redirect, 422/404/500/generic error branches.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

/* Mock antd message used by api.ts */
vi.mock("antd", async (importOriginal) => {
  const actual = await importOriginal<typeof import("antd")>();
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    },
  };
});

import { message } from "antd";

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("creates an axios instance with correct base config", async () => {
    const { api } = await import("../../services/api");
    expect(api.defaults.baseURL).toBeDefined();
    expect(api.defaults.timeout).toBe(15_000);
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("has request interceptor that injects token", async () => {
    localStorage.setItem("access_token", "test-jwt-token");
    const { api } = await import("../../services/api");

    const interceptors = api.interceptors.request as unknown as {
      handlers: Array<{
        fulfilled: (config: Record<string, unknown>) => Record<string, unknown>;
      }>;
    };

    const handler = interceptors.handlers.find((h) => h.fulfilled);
    expect(handler).toBeDefined();

    if (handler) {
      const config = {
        headers: {
          Authorization: undefined as string | undefined,
        },
      };
      const result = handler.fulfilled(config) as {
        headers: { Authorization: string };
      };
      expect(result.headers.Authorization).toBe("Bearer test-jwt-token");
    }
  });

  it("request interceptor does not inject token when absent", async () => {
    localStorage.removeItem("access_token");
    const { api } = await import("../../services/api");

    const interceptors = api.interceptors.request as unknown as {
      handlers: Array<{
        fulfilled: (config: Record<string, unknown>) => Record<string, unknown>;
      }>;
    };

    const handler = interceptors.handlers.find((h) => h.fulfilled);
    if (handler) {
      const config = {
        headers: {} as Record<string, string>,
      };
      const result = handler.fulfilled(config) as {
        headers: Record<string, string>;
      };
      expect(result.headers.Authorization).toBeUndefined();
    }
  });

  it("has response error interceptor", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => unknown }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);
    expect(handler).toBeDefined();
  });

  it("response interceptor handles 401 — clears tokens and redirects", async () => {
    localStorage.setItem("access_token", "old-token");
    localStorage.setItem("refresh_token", "old-refresh");
    const { api } = await import("../../services/api");

    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const error401 = {
      response: { status: 401, data: { detail: "Unauthorized" } },
    };

    await expect(handler!.rejected!(error401)).rejects.toBe(error401);

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(window.location.href).toBe("/login");
  });

  it("response interceptor handles 422 — shows warning", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const error422 = {
      response: { status: 422, data: { detail: "验证错误" } },
    };

    await expect(handler!.rejected!(error422)).rejects.toBe(error422);
    expect(message.warning).toHaveBeenCalledWith("验证错误");
  });

  it("response interceptor handles 404 — shows resource not found", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const error404 = {
      response: { status: 404, data: {} },
    };

    await expect(handler!.rejected!(error404)).rejects.toBe(error404);
    expect(message.error).toHaveBeenCalledWith("资源未找到");
  });

  it("response interceptor handles 500 — shows server error", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const error500 = {
      response: { status: 500, data: { detail: "Internal Server Error" } },
    };

    await expect(handler!.rejected!(error500)).rejects.toBe(error500);
    expect(message.error).toHaveBeenCalledWith("服务器错误，请稍后重试");
  });

  it("response interceptor handles generic error with detail", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const error403 = {
      response: { status: 403, data: { detail: "权限不足" } },
    };

    await expect(handler!.rejected!(error403)).rejects.toBe(error403);
    expect(message.error).toHaveBeenCalledWith("权限不足");
  });

  it("response interceptor handles error without detail — uses default message", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>;
    };
    const handler = interceptors.handlers.find((h) => h.rejected);

    const errorNoDetail = {
      response: { status: 400, data: {} },
    };

    await expect(handler!.rejected!(errorNoDetail)).rejects.toBe(errorNoDetail);
    expect(message.error).toHaveBeenCalledWith("请求失败，请稍后重试");
  });

  it("response interceptor passes through successful responses", async () => {
    const { api } = await import("../../services/api");
    const interceptors = api.interceptors.response as unknown as {
      handlers: Array<{
        fulfilled?: (response: unknown) => unknown;
        rejected?: (error: unknown) => unknown;
      }>;
    };
    const handler = interceptors.handlers.find((h) => h.fulfilled);
    expect(handler).toBeDefined();

    const mockResponse = { data: { success: true }, status: 200 };
    const result = handler!.fulfilled!(mockResponse);
    expect(result).toBe(mockResponse);
  });
});
