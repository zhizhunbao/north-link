/**
 * Unit tests for LogisticsPage component.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { LogisticsPage } from "../../pages/Logistics/Logistics";

vi.mock("../../services/logisticsService", () => ({
  logisticsService: {
    getAgents: vi.fn(),
    getShipments: vi.fn(),
    getRecommendations: vi.fn(),
  },
}));

import { logisticsService } from "../../services/logisticsService";

const mockedService = vi.mocked(logisticsService);

describe("LogisticsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page heading", () => {
    mockedService.getAgents.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<LogisticsPage />);
    expect(screen.getByText(/物流管理/)).toBeInTheDocument();
  });

  it("renders tab items", () => {
    mockedService.getAgents.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<LogisticsPage />);
    expect(screen.getByText("货代列表")).toBeInTheDocument();
    expect(screen.getByText("在途物流")).toBeInTheDocument();
  });

  it("shows empty state when no agents", async () => {
    mockedService.getAgents.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<LogisticsPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无货代数据")).toBeInTheDocument();
    });
  });

  it("displays agent cards when data loaded", async () => {
    mockedService.getAgents.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "顺丰速运",
            channel: "空运",
            rating: "S",
            unit_price: 45.0,
            currency: "CNY",
            est_days_min: 3,
            est_days_max: 5,
            tax_included: true,
            notes: null,
          },
        ],
        total: 1,
      },
    } as never);

    render(<LogisticsPage />);
    await waitFor(() => {
      expect(screen.getByText("顺丰速运")).toBeInTheDocument();
      expect(screen.getByText("空运")).toBeInTheDocument();
      expect(screen.getByText("包税")).toBeInTheDocument();
    });
  });

  it("displays rating tags on agent cards", async () => {
    mockedService.getAgents.mockResolvedValue({
      data: {
        items: [
          {
            id: "1",
            name: "Test Agent",
            channel: "海运",
            rating: "A",
            unit_price: 20.0,
            currency: "CNY",
            est_days_min: 15,
            est_days_max: 20,
            tax_included: false,
            notes: null,
          },
        ],
        total: 1,
      },
    } as never);

    render(<LogisticsPage />);
    await waitFor(() => {
      expect(screen.getByText("A级")).toBeInTheDocument();
    });
  });

  it("handles API error gracefully", async () => {
    mockedService.getAgents.mockRejectedValue(new Error("fail"));
    render(<LogisticsPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无货代数据")).toBeInTheDocument();
    });
  });

  it("calls getAgents on mount", () => {
    mockedService.getAgents.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<LogisticsPage />);
    expect(mockedService.getAgents).toHaveBeenCalledWith({
      page: 1,
      page_size: 50,
    });
  });
});
