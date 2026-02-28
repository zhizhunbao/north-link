/**
 * Logistics API service — LOGI-006.
 */
import { api } from "./api";
import type { PaginatedResponse } from "./priceService";

export interface FreightAgent {
  id: string;
  name: string;
  channel: string;
  rating: string;
  unit_price: number;
  currency: string;
  est_days_min: number;
  est_days_max: number;
  tax_included: boolean;
  notes: string | null;
}

export interface Shipment {
  id: string;
  order_id: string;
  agent_id: string;
  tracking_number: string | null;
  status: string;
  shipped_at: string | null;
  delivered_at: string | null;
}

export const logisticsService = {
  getAgents: (params: { page?: number; page_size?: number; rating?: string }) =>
    api.get<PaginatedResponse<FreightAgent>>("/api/v1/logistics/agents", { params }),

  getShipments: (params: { page?: number; page_size?: number; status?: string }) =>
    api.get<PaginatedResponse<Shipment>>("/api/v1/logistics/shipments", { params }),

  getRecommendations: (categoryId: string, weight?: number) =>
    api.get(`/api/v1/logistics/recommend/${categoryId}`, { params: { weight_kg: weight } }),
};
