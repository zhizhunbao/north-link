/**
 * Auth state management with Zustand — AUTH-007.
 * Handles login, logout, token persistence, and auth state.
 */
import { create } from "zustand";
import { api } from "../services/api";

interface User {
  id: string;
  username: string;
  role: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  restoreAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  isAuthenticated: !!localStorage.getItem("access_token"),
  loading: false,

  login: async (username: string, password: string) => {
    set({ loading: true });
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const { data } = await api.post("/api/v1/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }

      /* Fetch user profile */
      const { data: user } = await api.get("/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });

      set({
        token: data.access_token,
        user,
        isAuthenticated: true,
        loading: false,
      });
    } catch {
      set({ loading: false });
      throw new Error("登录失败，请检查用户名和密码");
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, token: null, isAuthenticated: false });
    window.location.href = "/login";
  },

  restoreAuth: async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      set({ isAuthenticated: false });
      return;
    }
    try {
      const { data: user } = await api.get("/api/v1/auth/me");
      set({ user, token, isAuthenticated: true });
    } catch {
      localStorage.removeItem("access_token");
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));
