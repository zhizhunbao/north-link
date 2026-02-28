/**
 * Orders page — ORDER-006.
 * Purchase/sales tabs with order list.
 */
import { useEffect, useState } from "react";
import {
  Card,
  Table,
  Tabs,
  Tag,
  Button,
  Space,
  Spin,
  Empty,
} from "antd";
import { PlusOutlined, FileTextOutlined } from "@ant-design/icons";
import { orderService, type Order } from "../../services/orderService";
import type { ColumnsType } from "antd/es/table";

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  draft: { color: "default", label: "草稿" },
  confirmed: { color: "processing", label: "已确认" },
  shipped: { color: "blue", label: "已发货" },
  delivered: { color: "green", label: "已签收" },
  completed: { color: "success", label: "已完成" },
};

const columns: ColumnsType<Order> = [
  {
    title: "订单类型",
    dataIndex: "order_type",
    width: 100,
    render: (type: string) => (
      <Tag color={type === "purchase" ? "blue" : "green"}>
        {type === "purchase" ? "采购" : "销售"}
      </Tag>
    ),
  },
  {
    title: "数量",
    dataIndex: "quantity",
    width: 80,
    align: "right",
  },
  {
    title: "单价",
    dataIndex: "unit_cost",
    width: 100,
    align: "right",
    render: (cost: number, record) => (
      <span style={{ fontFamily: "var(--font-mono)" }}>
        {cost?.toFixed(2)} {record.cost_currency}
      </span>
    ),
  },
  {
    title: "总成本",
    dataIndex: "total_cost",
    width: 120,
    align: "right",
    render: (cost: number) => (
      <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600 }}>
        {cost?.toFixed(2)}
      </span>
    ),
  },
  {
    title: "利润",
    dataIndex: "profit",
    width: 120,
    align: "right",
    render: (profit: number | null) => {
      if (profit == null) return "-";
      const color = profit >= 0 ? "var(--color-profit-high)" : "var(--color-profit-low)";
      return (
        <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color }}>
          {profit >= 0 ? "+" : ""}
          {profit.toFixed(2)}
        </span>
      );
    },
  },
  {
    title: "利润率",
    dataIndex: "profit_rate",
    width: 100,
    align: "right",
    render: (rate: number | null) => {
      if (rate == null) return "-";
      const pct = (rate * 100).toFixed(1);
      const color =
        rate >= 0.3 ? "var(--color-profit-high)" :
        rate >= 0.15 ? "var(--color-profit-medium)" :
        "var(--color-profit-low)";
      return (
        <span style={{ fontFamily: "var(--font-mono)", color }}>
          {pct}%
        </span>
      );
    },
  },
  {
    title: "状态",
    dataIndex: "status",
    width: 100,
    render: (status: string) => (
      <Tag color={STATUS_MAP[status]?.color ?? "default"}>
        {STATUS_MAP[status]?.label ?? status}
      </Tag>
    ),
  },
  {
    title: "创建时间",
    dataIndex: "created_at",
    width: 160,
    render: (date: string) =>
      date ? new Date(date).toLocaleDateString("zh-CN") : "-",
  },
];

function OrderTable({ orderType }: { orderType?: string }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    orderService
      .getList({ page, page_size: 20, order_type: orderType })
      .then((res) => {
        setOrders(res.data.items);
        setTotal(res.data.total);
      })
      .catch(() => {
        setOrders([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [page, orderType]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <Spin />
      </div>
    );
  }

  if (orders.length === 0) {
    return <Empty description="暂无订单" />;
  }

  return (
    <Table
      columns={columns}
      dataSource={orders}
      rowKey="id"
      pagination={{
        current: page,
        total,
        pageSize: 20,
        onChange: setPage,
        showTotal: (t) => `共 ${t} 条订单`,
      }}
      scroll={{ x: 800 }}
      size="middle"
    />
  );
}

export function OrdersPage() {
  return (
    <div>
      <div className="content-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>📋 订单中心</h1>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            新建订单
          </Button>
          <Button icon={<FileTextOutlined />}>
            报表中心
          </Button>
        </Space>
      </div>

      <Card>
        <Tabs
          defaultActiveKey="all"
          items={[
            { key: "all", label: "全部订单", children: <OrderTable /> },
            { key: "purchase", label: "采购订单", children: <OrderTable orderType="purchase" /> },
            { key: "sale", label: "销售订单", children: <OrderTable orderType="sale" /> },
          ]}
        />
      </Card>
    </div>
  );
}
