/**
 * Subscription API service — FE-018.
 */
import { api } from "./api";
import type { Subscription } from "../types/chat";

export const subscriptionService = {
  getAll: () =>
    api.get<Subscription[]>("/api/v1/subscriptions").then((r) => r.data),

  create: (data: {
    platform: string;
    target_type: "url" | "keyword";
    target_value: string;
    threshold?: number;
    product_id?: string;
  }) =>
    api.post<Subscription>("/api/v1/subscriptions", data).then((r) => r.data),

  update: (id: string, data: { threshold?: number; status?: string }) =>
    api
      .put<Subscription>(`/api/v1/subscriptions/${id}`, data)
      .then((r) => r.data),

  delete: (id: string) =>
    api.delete(`/api/v1/subscriptions/${id}`).then((r) => r.data),
};
