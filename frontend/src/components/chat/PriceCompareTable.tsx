/**
 * Price comparison table for chat results — FE-009.
 */
import { Table, Tag } from "antd";
import type { ProductItem } from "../../types/chat";

interface Props {
  items: ProductItem[];
}

const PLATFORM_LABELS: Record<string, string> = {
  bestbuy_ca: "BestBuy",
  amazon_ca: "Amazon",
  walmart_ca: "Walmart",
  costco_ca: "Costco",
  jd: "京东",
  taobao: "淘宝",
  pinduoduo: "拼多多",
  alibaba_1688: "1688",
};

const STOCK_COLORS: Record<string, string> = {
  in_stock: "green",
  out_of_stock: "red",
  limited: "orange",
  unknown: "default",
};

export function PriceCompareTable({ items }: Props) {
  const columns = [
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (p: string) => <Tag color="blue">{PLATFORM_LABELS[p] ?? p}</Tag>,
    },
    {
      title: "商品名称",
      dataIndex: "product_name",
      key: "product_name",
      ellipsis: true,
    },
    {
      title: "价格",
      dataIndex: "price",
      key: "price",
      sorter: (a: ProductItem, b: ProductItem) => a.price - b.price,
      render: (price: number, record: ProductItem) => (
        <span style={{ fontWeight: 600 }}>
          {record.currency === "CNY" ? "¥" : "C$"}
          {price?.toFixed(2)}
        </span>
      ),
    },
    {
      title: "评分",
      dataIndex: "rating",
      key: "rating",
      render: (r: number | undefined) => (r ? `${r}/5` : "-"),
    },
    {
      title: "库存",
      dataIndex: "stock_status",
      key: "stock_status",
      render: (s: string | undefined) =>
        s ? (
          <Tag color={STOCK_COLORS[s] ?? "default"}>
            {s === "in_stock" ? "有货" : s === "out_of_stock" ? "缺货" : s}
          </Tag>
        ) : (
          "-"
        ),
    },
    {
      title: "链接",
      dataIndex: "url",
      key: "url",
      render: (url: string | undefined) =>
        url ? (
          <a href={url} target="_blank" rel="noopener noreferrer">
            查看
          </a>
        ) : (
          "-"
        ),
    },
  ];

  return (
    <div className="price-compare-table">
      <Table
        dataSource={items}
        columns={columns}
        rowKey="product_name"
        pagination={false}
        size="small"
        scroll={{ x: 600 }}
      />
    </div>
  );
}
