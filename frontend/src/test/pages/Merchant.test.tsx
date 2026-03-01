/**
 * Unit tests for Merchant page.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MerchantPage } from "../../pages/Merchant/Merchant";

vi.mock("../../services/merchantService", () => ({
  merchantService: {
    getList: vi.fn(),
    getDetail: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

import { merchantService } from "../../services/merchantService";

const mockedService = vi.mocked(merchantService);

describe("MerchantPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page heading", () => {
    mockedService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<MerchantPage />);
    expect(screen.getByText(/商户管理/)).toBeInTheDocument();
  });

  it("renders add button", () => {
    mockedService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<MerchantPage />);
    expect(screen.getByText("添加商户")).toBeInTheDocument();
  });

  it("shows empty state when no merchants", async () => {
    mockedService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<MerchantPage />);
    await waitFor(() => {
      expect(screen.getByText(/暂无商户/)).toBeInTheDocument();
    });
  });

  it("displays merchant cards when data loaded", async () => {
    mockedService.getList.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "华强北电子",
            contact_person: "张三",
            phone: "13800138000",
            wechat: "zhangsan",
            address: "深圳市",
            rating: "A",
            notes: null,
            created_at: "2026-01-01",
          },
        ],
        total: 1,
      },
    } as never);

    render(<MerchantPage />);
    await waitFor(() => {
      expect(screen.getByText("华强北电子")).toBeInTheDocument();
      expect(screen.getByText("张三")).toBeInTheDocument();
    });
  });

  it("displays rating tags correctly", async () => {
    mockedService.getList.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "Test",
            contact_person: "P",
            phone: "123",
            wechat: "w",
            address: "a",
            rating: "S",
            notes: null,
            created_at: "2026-01-01",
          },
        ],
        total: 1,
      },
    } as never);

    render(<MerchantPage />);
    await waitFor(() => {
      expect(screen.getByText("S 级")).toBeInTheDocument();
    });
  });

  it("calls getList on mount", () => {
    mockedService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<MerchantPage />);
    expect(mockedService.getList).toHaveBeenCalledWith({
      page: 1,
      page_size: 100,
    });
  });

  it("handles API error gracefully", async () => {
    mockedService.getList.mockRejectedValue(new Error("Network error"));
    render(<MerchantPage />);
    await waitFor(() => {
      expect(screen.getByText(/暂无商户/)).toBeInTheDocument();
    });
  });
});
