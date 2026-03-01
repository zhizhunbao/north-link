/**
 * Unit tests for PriceCenterPage component.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { PriceCenterPage } from "../../pages/PriceCenter/PriceCenter";

vi.mock("../../services/priceService", () => ({
  priceService: {
    getProducts: vi.fn(),
    getProduct: vi.fn(),
    getCategories: vi.fn(),
  },
}));

import { priceService } from "../../services/priceService";

const mockedService = vi.mocked(priceService);

describe("PriceCenterPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page heading", () => {
    mockedService.getProducts.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<PriceCenterPage />);
    expect(screen.getByText(/比价中心/)).toBeInTheDocument();
  });

  it("renders search input", () => {
    mockedService.getProducts.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<PriceCenterPage />);
    expect(screen.getByTestId("price-search")).toBeInTheDocument();
  });

  it("shows empty state when no products", async () => {
    mockedService.getProducts.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<PriceCenterPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无商品数据")).toBeInTheDocument();
    });
  });

  it("displays product cards when data loaded", async () => {
    mockedService.getProducts.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "iPhone 15",
            sku: "IPH15",
            brand: "Apple",
            condition: "new",
            category_id: "cat1",
            category_name: "手机",
            attributes: {},
            created_at: "2026-01-01",
          },
        ],
        total: 1,
      },
    } as never);

    render(<PriceCenterPage />);
    await waitFor(() => {
      expect(screen.getByText("iPhone 15")).toBeInTheDocument();
      expect(screen.getByText("IPH15")).toBeInTheDocument();
      expect(screen.getByText("全新")).toBeInTheDocument();
    });
  });

  it("displays condition tags correctly", async () => {
    mockedService.getProducts.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "Used Laptop",
            sku: "LAP001",
            brand: null,
            condition: "used",
            category_id: "cat2",
            attributes: {},
            created_at: "2026-01-01",
          },
        ],
        total: 1,
      },
    } as never);

    render(<PriceCenterPage />);
    await waitFor(() => {
      expect(screen.getByText("二手")).toBeInTheDocument();
    });
  });

  it("calls getProducts on mount", () => {
    mockedService.getProducts.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<PriceCenterPage />);
    expect(mockedService.getProducts).toHaveBeenCalledWith({
      page: 1,
      page_size: 20,
    });
  });

  it("handles API error gracefully", async () => {
    mockedService.getProducts.mockRejectedValue(new Error("fail"));
    render(<PriceCenterPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无商品数据")).toBeInTheDocument();
    });
  });
});
