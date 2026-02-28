/**
 * Price Center API service — PRICE-008.
 */
import { api } from "./api";

export interface Product {
  id: string;
  name: string;
  sku: string;
  brand: string | null;
  condition: string;
  category_id: string;
  category_name?: string;
  attributes: Record<string, unknown>;
  created_at: string;
}

export interface PriceRecord {
  id: string;
  product_id: string;
  price: number;
  currency: string;
  region: string;
  source: string;
  recorded_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProductListParams {
  page?: number;
  page_size?: number;
  category_id?: string;
  condition?: string;
  search?: string;
  sort_by?: string;
}

export const priceService = {
  getProducts: (params: ProductListParams) =>
    api.get<PaginatedResponse<Product>>("/api/v1/prices/products", { params }),

  getProduct: (id: string) =>
    api.get<Product>(`/api/v1/prices/products/${id}`),

  getCategories: () =>
    api.get<{ id: string; name: string; icon: string }[]>("/api/v1/prices/categories"),
};
