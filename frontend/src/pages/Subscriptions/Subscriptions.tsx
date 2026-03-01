/**
 * Subscription management page — FE-016.
 */
import { useEffect, useState } from "react";
import { Card, Table, Tag, Button, Space, Popconfirm, Empty, App } from "antd";
import {
  PauseCircleOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  BellOutlined,
} from "@ant-design/icons";
import { subscriptionService } from "../../services/subscriptionService";
import type { Subscription } from "../../types/chat";

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  active: { color: "green", label: "追踪中" },
  paused: { color: "orange", label: "已暂停" },
  expired: { color: "default", label: "已过期" },
};

const PLATFORM_LABELS: Record<string, string> = {
  bestbuy_ca: "BestBuy",
  amazon_ca: "Amazon",
  walmart_ca: "Walmart",
  costco_ca: "Costco",
  jd: "京东",
  taobao: "淘宝",
  pinduoduo: "拼多多",
};

export function SubscriptionsPage() {
  const [data, setData] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(false);
  const { message } = App.useApp();

  const fetchData = async () => {
    setLoading(true);
    try {
      const subs = await subscriptionService.getAll();
      setData(subs);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggle = async (sub: Subscription) => {
    const newStatus = sub.status === "active" ? "paused" : "active";
    await subscriptionService.update(sub.id, { status: newStatus });
    message.success(newStatus === "active" ? "已恢复追踪" : "已暂停追踪");
    fetchData();
  };

  const handleDelete = async (id: string) => {
    await subscriptionService.delete(id);
    message.success("已删除订阅");
    fetchData();
  };

  const columns = [
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (p: string) => <Tag color="blue">{PLATFORM_LABELS[p] ?? p}</Tag>,
    },
    {
      title: "追踪内容",
      dataIndex: "target_value",
      key: "target_value",
      ellipsis: true,
    },
    {
      title: "类型",
      dataIndex: "target_type",
      key: "target_type",
      render: (t: string) => (t === "url" ? "链接" : "关键词"),
    },
    {
      title: "变动阈值",
      dataIndex: "threshold",
      key: "threshold",
      render: (v: number) => `${v}%`,
    },
    {
      title: "最近价格",
      dataIndex: "last_price",
      key: "last_price",
      render: (p: number | null) => (p ? `$${p.toFixed(2)}` : "-"),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (s: string) => {
        const info = STATUS_MAP[s] ?? { color: "default", label: s };
        return <Tag color={info.color}>{info.label}</Tag>;
      },
    },
    {
      title: "操作",
      key: "actions",
      render: (_: unknown, record: Subscription) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={
              record.status === "active" ? (
                <PauseCircleOutlined />
              ) : (
                <PlayCircleOutlined />
              )
            }
            onClick={() => handleToggle(record)}
            disabled={record.status === "expired"}
          />
          <Popconfirm
            title="确定删除此订阅？"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: "24px" }}>
      <Card
        title={
          <Space>
            <BellOutlined />
            <span>订阅追踪</span>
          </Space>
        }
        extra={
          <Tag>{data.filter((s) => s.status === "active").length} 个活跃</Tag>
        }
      >
        <Table
          dataSource={data}
          columns={columns}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: <Empty description="暂无订阅" /> }}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
