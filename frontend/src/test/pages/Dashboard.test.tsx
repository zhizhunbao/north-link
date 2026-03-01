/**
 * Unit tests for DashboardPage component.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

/* Mock api module */
vi.mock("../../services/api", () => ({
  api: {
    get: vi.fn(),
  },
}));

import { api } from "../../services/api";
import { DashboardPage } from "../../pages/Dashboard/Dashboard";

const mockedApi = vi.mocked(api);

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page heading", async () => {
    mockedApi.get.mockResolvedValue({
      data: { date: "2026-02-28", recommendations: [], total_evaluated: 0 },
    });
    render(<DashboardPage />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("shows stat cards", async () => {
    mockedApi.get.mockResolvedValue({
      data: {
        date: "2026-02-28",
        recommendations: [
          {
            product_id: "1",
            product_name: "Test Product",
            sku: "SKU001",
            category_name: "Electronics",
            ca_price: 100,
            cn_price: 500,
            profit_rate: 0.35,
            risk_level: "low",
            score: 90,
            merchant_count: 3,
          },
        ],
        total_evaluated: 50,
      },
    });

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("今日推荐")).toBeInTheDocument();
      expect(screen.getByText("已评估商品")).toBeInTheDocument();
      expect(screen.getByText("在途物流")).toBeInTheDocument();
      expect(screen.getByText("今日利润")).toBeInTheDocument();
    });
  });

  it("displays recommendations when data is loaded", async () => {
    mockedApi.get.mockResolvedValue({
      data: {
        date: "2026-02-28",
        recommendations: [
          {
            product_id: "1",
            product_name: "iPhone 15 Pro",
            sku: "IPH15P",
            category_name: "手机",
            ca_price: 1299,
            cn_price: 8999,
            profit_rate: 0.42,
            risk_level: "low",
            score: 95,
            merchant_count: 5,
          },
        ],
        total_evaluated: 100,
      },
    });

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("iPhone 15 Pro")).toBeInTheDocument();
      expect(screen.getByText(/手机/)).toBeInTheDocument();
    });
  });

  it("shows empty state when no recommendations", async () => {
    mockedApi.get.mockResolvedValue({
      data: { date: "2026-02-28", recommendations: [], total_evaluated: 0 },
    });

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无推荐数据")).toBeInTheDocument();
    });
  });

  it("handles API error gracefully", async () => {
    mockedApi.get.mockRejectedValue(new Error("Network error"));

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无推荐数据")).toBeInTheDocument();
    });
  });

  it("shows risk level tag for recommendations", async () => {
    mockedApi.get.mockResolvedValue({
      data: {
        date: "2026-02-28",
        recommendations: [
          {
            product_id: "1",
            product_name: "Product A",
            sku: "SKU-A",
            category_name: "Cat",
            ca_price: 100,
            cn_price: 500,
            profit_rate: 0.25,
            risk_level: "medium",
            score: 80,
            merchant_count: 2,
          },
        ],
        total_evaluated: 10,
      },
    });

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText("中风险")).toBeInTheDocument();
    });
  });

  it("calls recommendations API on mount", () => {
    mockedApi.get.mockResolvedValue({
      data: { date: "2026-02-28", recommendations: [], total_evaluated: 0 },
    });
    render(<DashboardPage />);
    expect(mockedApi.get).toHaveBeenCalledWith(
      "/api/v1/recommendations/daily?top_n=5",
    );
  });
});
