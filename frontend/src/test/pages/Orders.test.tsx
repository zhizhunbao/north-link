/**
 * Unit tests for OrdersPage and OrderTable component.
 * Covers render, data loading, empty/loading states, column renderers,
 * and error handling.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { OrdersPage } from "../../pages/Orders/Orders";
import type { Order } from "../../services/orderService";

/* Mock orderService */
vi.mock("../../services/orderService", () => ({
  orderService: {
    getList: vi.fn(),
    getDetail: vi.fn(),
    create: vi.fn(),
    getReport: vi.fn(),
  },
}));

import { orderService } from "../../services/orderService";

const mockedOrderService = vi.mocked(orderService);

const MOCK_ORDERS: Order[] = [
  {
    id: "order-1",
    order_type: "purchase",
    product_id: "prod-1",
    merchant_id: "merch-1",
    quantity: 10,
    unit_cost: 25.5,
    cost_currency: "CAD",
    total_cost: 255.0,
    selling_price: 400.0,
    profit: 145.0,
    profit_rate: 0.35,
    status: "confirmed",
    created_at: "2026-02-28T10:00:00Z",
  },
  {
    id: "order-2",
    order_type: "sale",
    product_id: "prod-2",
    merchant_id: "merch-2",
    quantity: 5,
    unit_cost: 100.0,
    cost_currency: "CNY",
    total_cost: 500.0,
    selling_price: 450.0,
    profit: -50.0,
    profit_rate: -0.1,
    status: "shipped",
    created_at: "2026-02-27T08:00:00Z",
  },
  {
    id: "order-3",
    order_type: "purchase",
    product_id: "prod-3",
    merchant_id: "merch-3",
    quantity: 20,
    unit_cost: 50.0,
    cost_currency: "CAD",
    total_cost: 1000.0,
    selling_price: 1200.0,
    profit: 200.0,
    profit_rate: 0.2,
    status: "draft",
    created_at: "2026-02-26T15:00:00Z",
  },
  {
    id: "order-4",
    order_type: "sale",
    product_id: "prod-4",
    merchant_id: "merch-4",
    quantity: 3,
    unit_cost: 300.0,
    cost_currency: "CAD",
    total_cost: 900.0,
    selling_price: null,
    profit: null,
    profit_rate: null,
    status: "delivered",
    created_at: "2026-02-25T12:00:00Z",
  },
];

describe("OrdersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page heading", () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<OrdersPage />);
    expect(screen.getByText(/订单中心/)).toBeInTheDocument();
  });

  it("renders tab items", () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<OrdersPage />);
    expect(screen.getByText("全部订单")).toBeInTheDocument();
    expect(screen.getByText("采购订单")).toBeInTheDocument();
    expect(screen.getByText("销售订单")).toBeInTheDocument();
  });

  it("renders action buttons", () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<OrdersPage />);
    expect(screen.getByText("新建订单")).toBeInTheDocument();
    expect(screen.getByText("报表中心")).toBeInTheDocument();
  });

  it("shows empty state when no orders", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<OrdersPage />);
    await waitFor(() => {
      expect(screen.getByText("暂无订单")).toBeInTheDocument();
    });
  });

  it("calls getList on mount", () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [], total: 0 },
    } as never);
    render(<OrdersPage />);
    expect(mockedOrderService.getList).toHaveBeenCalled();
  });

  it("displays order data in table when loaded", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: MOCK_ORDERS, total: MOCK_ORDERS.length },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      /* Order type tags */
      expect(screen.getAllByText("采购").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("销售").length).toBeGreaterThanOrEqual(1);
    });

    /* Status tags */
    await waitFor(() => {
      expect(screen.getByText("已确认")).toBeInTheDocument();
      expect(screen.getByText("已发货")).toBeInTheDocument();
      expect(screen.getByText("草稿")).toBeInTheDocument();
      expect(screen.getByText("已签收")).toBeInTheDocument();
    });
  });

  it("renders profit values with correct formatting", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: MOCK_ORDERS, total: MOCK_ORDERS.length },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      /* Positive profit should show + prefix */
      expect(screen.getByText("+145.00")).toBeInTheDocument();
      /* Negative profit should show - prefix */
      expect(screen.getByText("-50.00")).toBeInTheDocument();
    });
  });

  it("renders profit rate percentages", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: MOCK_ORDERS, total: MOCK_ORDERS.length },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      /* 0.35 * 100 = 35.0% */
      expect(screen.getByText("35.0%")).toBeInTheDocument();
      /* 0.2 * 100 = 20.0% */
      expect(screen.getByText("20.0%")).toBeInTheDocument();
    });
  });

  it("renders dash for null profit/profit_rate", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: MOCK_ORDERS, total: MOCK_ORDERS.length },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      /* order-4 has null profit and profit_rate — should render "-" */
      const dashes = screen.getAllByText("-");
      expect(dashes.length).toBeGreaterThanOrEqual(2);
    });
  });

  it("shows error fallback when API fails", async () => {
    mockedOrderService.getList.mockRejectedValue(new Error("Network error"));
    render(<OrdersPage />);

    await waitFor(() => {
      /* Error catch should result in empty list → "暂无订单" */
      expect(screen.getByText("暂无订单")).toBeInTheDocument();
    });
  });

  it("renders unit cost with currency", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [MOCK_ORDERS[0]], total: 1 },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText(/25\.50/)).toBeInTheDocument();
      expect(screen.getByText(/CAD/)).toBeInTheDocument();
    });
  });

  it("renders total cost", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [MOCK_ORDERS[0]], total: 1 },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText("255.00")).toBeInTheDocument();
    });
  });

  it("renders created_at formatted date", async () => {
    mockedOrderService.getList.mockResolvedValue({
      data: { items: [MOCK_ORDERS[0]], total: 1 },
    } as never);
    render(<OrdersPage />);

    await waitFor(() => {
      /* Formatted in zh-CN locale */
      expect(screen.getByText(/2026/)).toBeInTheDocument();
    });
  });
});
