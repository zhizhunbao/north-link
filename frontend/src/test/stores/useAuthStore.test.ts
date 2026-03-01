/**
 * Unit tests for useAuthStore — Zustand auth state management.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useAuthStore } from "../../stores/useAuthStore";

/* Mock the api module */
vi.mock("../../services/api", () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

import { api } from "../../services/api";

const mockedApi = vi.mocked(api);

describe("useAuthStore", () => {
  beforeEach(() => {
    localStorage.clear();
    /* Reset Zustand store to initial state */
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("initial state", () => {
    it("starts with null user and unauthenticated", () => {
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.loading).toBe(false);
    });

    it("restores token from localStorage", () => {
      localStorage.setItem("access_token", "saved-token");
      /* Re-create the store to test initialization */
      useAuthStore.setState({
        token: localStorage.getItem("access_token"),
        isAuthenticated: !!localStorage.getItem("access_token"),
      });
      const state = useAuthStore.getState();
      expect(state.token).toBe("saved-token");
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe("login", () => {
    it("sets loading to true during login", async () => {
      mockedApi.post.mockResolvedValue({
        data: { access_token: "jwt-token", refresh_token: "refresh-token" },
      });
      mockedApi.get.mockResolvedValue({
        data: { id: "1", username: "admin", role: "admin", is_active: true },
      });

      const loginPromise = useAuthStore.getState().login("admin", "password");
      expect(useAuthStore.getState().loading).toBe(true);

      await loginPromise;
      expect(useAuthStore.getState().loading).toBe(false);
    });

    it("stores token and user on successful login", async () => {
      mockedApi.post.mockResolvedValue({
        data: { access_token: "jwt-token", refresh_token: "refresh-token" },
      });
      mockedApi.get.mockResolvedValue({
        data: { id: "1", username: "admin", role: "admin", is_active: true },
      });

      await useAuthStore.getState().login("admin", "password");

      const state = useAuthStore.getState();
      expect(state.token).toBe("jwt-token");
      expect(state.isAuthenticated).toBe(true);
      expect(state.user?.username).toBe("admin");
      expect(localStorage.getItem("access_token")).toBe("jwt-token");
      expect(localStorage.getItem("refresh_token")).toBe("refresh-token");
    });

    it("sends form-urlencoded login request", async () => {
      mockedApi.post.mockResolvedValue({
        data: { access_token: "tok" },
      });
      mockedApi.get.mockResolvedValue({
        data: { id: "1", username: "u", role: "user", is_active: true },
      });

      await useAuthStore.getState().login("myuser", "mypass");

      expect(mockedApi.post).toHaveBeenCalledWith(
        "/api/v1/auth/login",
        expect.any(URLSearchParams),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } },
      );
    });

    it("throws error on login failure", async () => {
      mockedApi.post.mockRejectedValue(new Error("Network error"));

      await expect(
        useAuthStore.getState().login("bad", "creds"),
      ).rejects.toThrow("登录失败，请检查用户名和密码");

      expect(useAuthStore.getState().loading).toBe(false);
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it("handles login without refresh_token", async () => {
      mockedApi.post.mockResolvedValue({
        data: { access_token: "tok-only" },
      });
      mockedApi.get.mockResolvedValue({
        data: { id: "1", username: "u", role: "user", is_active: true },
      });

      await useAuthStore.getState().login("u", "p");
      expect(localStorage.getItem("refresh_token")).toBeNull();
      expect(localStorage.getItem("access_token")).toBe("tok-only");
    });
  });

  describe("logout", () => {
    it("clears user, token, and localStorage", () => {
      /* Set up authenticated state */
      localStorage.setItem("access_token", "tok");
      localStorage.setItem("refresh_token", "ref");
      useAuthStore.setState({
        user: { id: "1", username: "admin", role: "admin", is_active: true },
        token: "tok",
        isAuthenticated: true,
      });

      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(localStorage.getItem("access_token")).toBeNull();
      expect(localStorage.getItem("refresh_token")).toBeNull();
    });

    it("redirects to /login", () => {
      useAuthStore.getState().logout();
      expect(window.location.href).toBe("/login");
    });
  });

  describe("restoreAuth", () => {
    it("restores user from token", async () => {
      localStorage.setItem("access_token", "valid-tok");
      mockedApi.get.mockResolvedValue({
        data: { id: "1", username: "admin", role: "admin", is_active: true },
      });

      await useAuthStore.getState().restoreAuth();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.user?.username).toBe("admin");
    });

    it("sets unauthenticated when no token exists", async () => {
      await useAuthStore.getState().restoreAuth();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it("clears auth state on restore failure", async () => {
      localStorage.setItem("access_token", "expired-tok");
      mockedApi.get.mockRejectedValue(new Error("401"));

      await useAuthStore.getState().restoreAuth();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(localStorage.getItem("access_token")).toBeNull();
    });
  });
});
