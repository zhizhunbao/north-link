/**
 * Order API service — ORDER-006.
 */
import { api } from "./api";
import type { PaginatedResponse } from "./priceService";

export interface Order {
  id: string;
  order_type: string;
  product_id: string;
  merchant_id: string;
  quantity: number;
  unit_cost: number;
  cost_currency: string;
  total_cost: number;
  selling_price: number | null;
  profit: number | null;
  profit_rate: number | null;
  status: string;
  created_at: string;
}

export const orderService = {
  getList: (params: { page?: number; page_size?: number; order_type?: string; status?: string }) =>
    api.get<PaginatedResponse<Order>>("/api/v1/orders", { params }),

  getDetail: (id: string) =>
    api.get<Order>(`/api/v1/orders/${id}`),

  create: (data: Partial<Order>) =>
    api.post<Order>("/api/v1/orders", data),

  getReport: (params: { period?: string; start_date?: string; end_date?: string }) =>
    api.get("/api/v1/orders/reports", { params }),
};
