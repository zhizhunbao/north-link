/**
 * Axios API client with JWT interceptors — INFRA-007.
 * - Auto-injects Authorization header
 * - 401 → redirect to /login
 * - Unified error toast via Ant Design message
 */
import axios from "axios";
import { message } from "antd";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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

/* Response interceptor — handle errors */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail ?? "请求失败，请稍后重试";

    if (status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (status === 422) {
      message.warning(detail);
    } else if (status === 404) {
      message.error("资源未找到");
    } else if (status && status >= 500) {
      message.error("服务器错误，请稍后重试");
    } else {
      message.error(detail);
    }

    return Promise.reject(error);
  }
);
