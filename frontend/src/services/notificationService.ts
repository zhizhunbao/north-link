/**
 * Notification API service — FE-020.
 */
import { api } from "./api";
import type { Notification } from "../types/chat";

export const notificationService = {
  getAll: (unreadOnly = false) =>
    api
      .get<Notification[]>("/api/v1/notifications", {
        params: { unread_only: unreadOnly },
      })
      .then((r) => r.data),

  getUnreadCount: () =>
    api
      .get<{ count: number }>("/api/v1/notifications/unread-count")
      .then((r) => r.data.count),

  markRead: (id: string) =>
    api.put(`/api/v1/notifications/${id}/read`).then((r) => r.data),

  markAllRead: () =>
    api.put("/api/v1/notifications/read-all").then((r) => r.data),
};
