/**
 * Logistics management page — LOGI-006.
 * Agent cards + shipment timeline.
 */
import { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Tabs,
  Tag,
  Spin,
  Empty,
  Statistic,
  Timeline,
  Badge,
} from "antd";
import {
  CarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  ThunderboltOutlined,
  SafetyOutlined,
} from "@ant-design/icons";
import { logisticsService, type FreightAgent } from "../../services/logisticsService";

const RATING_COLORS: Record<string, string> = {
  S: "gold",
  A: "green",
  B: "blue",
  C: "default",
};

function AgentListTab() {
  const [agents, setAgents] = useState<FreightAgent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    logisticsService
      .getAgents({ page: 1, page_size: 50 })
      .then((res) => setAgents(res.data.items))
      .catch(() => setAgents([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 60 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (agents.length === 0) {
    return <Empty description="暂无货代数据" />;
  }

  return (
    <Row gutter={[16, 16]}>
      {agents.map((agent) => (
        <Col xs={24} sm={12} lg={8} key={agent.id}>
          <Card hoverable>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h3 style={{ margin: 0, fontWeight: 600 }}>
                  {agent.name}
                  <Tag color={RATING_COLORS[agent.rating]} style={{ marginLeft: 8 }}>
                    {agent.rating}级
                  </Tag>
                </h3>
                <div style={{ color: "var(--color-text-secondary)", marginTop: 4, fontSize: "var(--text-sm)" }}>
                  {agent.channel}
                </div>
              </div>
              {agent.tax_included && (
                <Tag color="green" icon={<SafetyOutlined />}>
                  包税
                </Tag>
              )}
            </div>

            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Statistic
                  title="单价"
                  value={agent.unit_price}
                  precision={2}
                  prefix={<DollarOutlined />}
                  suffix={`/${agent.currency}`}
                  valueStyle={{ fontSize: "var(--text-base)", fontFamily: "var(--font-mono)" }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="时效"
                  value={`${agent.est_days_min}-${agent.est_days_max}`}
                  suffix="天"
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ fontSize: "var(--text-base)" }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="推荐"
                  value={agent.rating === "S" ? "⭐" : agent.rating === "A" ? "推荐" : "-"}
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ fontSize: "var(--text-base)" }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      ))}
    </Row>
  );
}

function ShipmentTab() {
  return (
    <Card>
      <Timeline
        items={[
          {
            color: "green",
            dot: <CheckCircleOutlined />,
            children: "已签收 — 2026-02-28 14:00",
          },
          {
            color: "blue",
            dot: <CarOutlined />,
            children: "配送中 — 预计今天送达",
          },
          {
            color: "blue",
            children: "清关完成 — 2026-02-27 09:30",
          },
          {
            color: "gray",
            children: "已发货 — 2026-02-25 16:00",
          },
        ]}
      />
      <div style={{ textAlign: "center", color: "var(--color-text-tertiary)", marginTop: 16 }}>
        <Badge status="processing" text="物流跟踪功能开发中..." />
      </div>
    </Card>
  );
}

export function LogisticsPage() {
  return (
    <div>
      <div className="content-header">
        <h1>🚚 物流管理</h1>
      </div>
      <Tabs
        defaultActiveKey="agents"
        items={[
          { key: "agents", label: "货代列表", children: <AgentListTab /> },
          { key: "shipments", label: "在途物流", children: <ShipmentTab /> },
        ]}
      />
    </div>
  );
}
