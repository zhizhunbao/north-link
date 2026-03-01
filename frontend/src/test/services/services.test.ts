/**
 * Unit tests for service modules — verifying API call patterns.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../services/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import { api } from "../../services/api";
import { merchantService } from "../../services/merchantService";
import { priceService } from "../../services/priceService";
import { logisticsService } from "../../services/logisticsService";
import { orderService } from "../../services/orderService";
import { authService } from "../../services/authService";

const mockedApi = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("merchantService", () => {
  it("getList calls correct endpoint with params", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });
    await merchantService.getList({ page: 1, page_size: 10 });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/merchants", {
      params: { page: 1, page_size: 10 },
    });
  });

  it("getDetail calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: {} });
    await merchantService.getDetail("abc-123");
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/merchants/abc-123");
  });

  it("create sends POST with data", async () => {
    mockedApi.post.mockResolvedValue({ data: {} });
    const payload = { name: "Test", contact_person: "John" };
    await merchantService.create(payload);
    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/merchants", payload);
  });

  it("update sends PUT with id and data", async () => {
    mockedApi.put.mockResolvedValue({ data: {} });
    const payload = { name: "Updated" };
    await merchantService.update("abc-123", payload);
    expect(mockedApi.put).toHaveBeenCalledWith(
      "/api/v1/merchants/abc-123",
      payload,
    );
  });

  it("delete sends DELETE with id", async () => {
    mockedApi.delete.mockResolvedValue({ data: {} });
    await merchantService.delete("abc-123");
    expect(mockedApi.delete).toHaveBeenCalledWith("/api/v1/merchants/abc-123");
  });
});

describe("priceService", () => {
  it("getProducts calls correct endpoint with all params", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });
    await priceService.getProducts({
      page: 2,
      page_size: 10,
      category_id: "cat1",
      condition: "new",
      search: "iphone",
      sort_by: "price_asc",
    });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/prices/products", {
      params: {
        page: 2,
        page_size: 10,
        category_id: "cat1",
        condition: "new",
        search: "iphone",
        sort_by: "price_asc",
      },
    });
  });

  it("getProduct calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: {} });
    await priceService.getProduct("prod-1");
    expect(mockedApi.get).toHaveBeenCalledWith(
      "/api/v1/prices/products/prod-1",
    );
  });

  it("getCategories calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: [] });
    await priceService.getCategories();
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/prices/categories");
  });
});

describe("logisticsService", () => {
  it("getAgents calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });
    await logisticsService.getAgents({ page: 1, page_size: 50, rating: "A" });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/logistics/agents", {
      params: { page: 1, page_size: 50, rating: "A" },
    });
  });

  it("getShipments calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });
    await logisticsService.getShipments({ page: 1, status: "in_transit" });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/logistics/shipments", {
      params: { page: 1, status: "in_transit" },
    });
  });

  it("getRecommendations calls with category and weight", async () => {
    mockedApi.get.mockResolvedValue({ data: [] });
    await logisticsService.getRecommendations("electronics", 5.0);
    expect(mockedApi.get).toHaveBeenCalledWith(
      "/api/v1/logistics/recommend/electronics",
      { params: { weight_kg: 5.0 } },
    );
  });

  it("getRecommendations works without optional weight", async () => {
    mockedApi.get.mockResolvedValue({ data: [] });
    await logisticsService.getRecommendations("beauty");
    expect(mockedApi.get).toHaveBeenCalledWith(
      "/api/v1/logistics/recommend/beauty",
      { params: { weight_kg: undefined } },
    );
  });
});

describe("orderService", () => {
  it("getList calls correct endpoint with filters", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });
    await orderService.getList({
      page: 1,
      page_size: 20,
      order_type: "purchase",
      status: "confirmed",
    });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/orders", {
      params: {
        page: 1,
        page_size: 20,
        order_type: "purchase",
        status: "confirmed",
      },
    });
  });

  it("getDetail calls correct endpoint", async () => {
    mockedApi.get.mockResolvedValue({ data: {} });
    await orderService.getDetail("order-1");
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/orders/order-1");
  });

  it("create sends POST request", async () => {
    mockedApi.post.mockResolvedValue({ data: {} });
    const payload = { order_type: "purchase", quantity: 10 };
    await orderService.create(payload);
    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/orders", payload);
  });

  it("getReport sends correct params", async () => {
    mockedApi.get.mockResolvedValue({ data: {} });
    await orderService.getReport({
      period: "monthly",
      start_date: "2026-01-01",
    });
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/orders/reports", {
      params: { period: "monthly", start_date: "2026-01-01" },
    });
  });
});

describe("authService", () => {
  it("changePassword sends PUT request", async () => {
    mockedApi.put.mockResolvedValue({ data: {} });
    await authService.changePassword({
      old_password: "old",
      new_password: "new",
    });
    expect(mockedApi.put).toHaveBeenCalledWith("/api/v1/auth/password", {
      old_password: "old",
      new_password: "new",
    });
  });

  it("getProfile sends GET request", async () => {
    mockedApi.get.mockResolvedValue({
      data: { id: "1", username: "admin" },
    });
    await authService.getProfile();
    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/auth/me");
  });
});
