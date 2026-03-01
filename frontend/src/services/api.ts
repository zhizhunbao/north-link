/**
 * Axios API client with JWT interceptors — INFRA-007.
 * - Auto-injects Authorization header
 * - 401 → redirect to /login
 * - Errors bubble up to components for display
 */
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});

/* Request interceptor — inject JWT */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/* Response interceptor — handle auth errors */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  },
);
