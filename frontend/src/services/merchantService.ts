/**
 * Merchant API service — MERCH-006.
 */
import { api } from "./api";
import type { PaginatedResponse } from "./priceService";

export interface Merchant {
  id: string;
  name: string;
  contact_person: string;
  phone: string;
  wechat: string;
  address: string;
  rating: string;
  notes: string | null;
  created_at: string;
}

export interface MerchantQuote {
  id: string;
  merchant_id: string;
  product_id: string;
  price: number;
  currency: string;
  quoted_at: string;
}

export const merchantService = {
  getList: (params: { page?: number; page_size?: number; category_id?: string }) =>
    api.get<PaginatedResponse<Merchant>>("/api/v1/merchants", { params }),

  getDetail: (id: string) =>
    api.get<Merchant>(`/api/v1/merchants/${id}`),

  create: (data: Partial<Merchant>) =>
    api.post<Merchant>("/api/v1/merchants", data),

  update: (id: string, data: Partial<Merchant>) =>
    api.put<Merchant>(`/api/v1/merchants/${id}`, data),

  delete: (id: string) =>
    api.delete(`/api/v1/merchants/${id}`),
};
