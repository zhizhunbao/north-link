/**
 * Dashboard page — REC-003/004 + V1.5 scraper stats.
 * Shows daily TOP5 recommendations + stats cards + AI usage.
 */
import { useEffect, useState } from "react";
import { Card, Col, Row, Statistic, Tag, Spin, Empty, Progress } from "antd";
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  ShoppingCartOutlined,
  CarOutlined,
  DollarOutlined,
  StarOutlined,
  RobotOutlined,
  BellOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { api } from "../../services/api";
import { scraperService } from "../../services/scraperService";
import { notificationService } from "../../services/notificationService";
import { subscriptionService } from "../../services/subscriptionService";
import type { ScraperUsage, Subscription } from "../../types/chat";

interface RecommendedProduct {
  product_id: string;
  product_name: string;
  sku: string;
  category_name: string;
  ca_price: number;
  cn_price: number;
  profit_rate: number;
  risk_level: string;
  score: number;
  merchant_count: number;
}

interface DailyRecommendation {
  date: string;
  recommendations: RecommendedProduct[];
  total_evaluated: number;
}

const RISK_COLORS: Record<string, string> = {
  low: "green",
  medium: "orange",
  high: "red",
};

export function DashboardPage() {
  const [data, setData] = useState<DailyRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [usage, setUsage] = useState<ScraperUsage | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [activeSubs, setActiveSubs] = useState(0);

  useEffect(() => {
    api
      .get<DailyRecommendation>("/api/v1/recommendations/daily?top_n=5")
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));

    // V1.5: fetch scraper stats
    scraperService
      .getUsage()
      .then(setUsage)
      .catch(() => {});
    notificationService
      .getUnreadCount()
      .then(setUnreadCount)
      .catch(() => {});
    subscriptionService
      .getAll()
      .then((subs: Subscription[]) =>
        setActiveSubs(subs.filter((s) => s.status === "active").length),
      )
      .catch(() => {});
  }, []);

  return (
    <div>
      <div className="content-header">
        <h1>Dashboard</h1>
      </div>

      {/* V1.0 Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="今日推荐"
              value={data?.recommendations.length ?? 0}
              prefix={<StarOutlined />}
              styles={{ content: { color: "var(--color-primary)" } }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="已评估商品"
              value={data?.total_evaluated ?? 0}
              prefix={<ShoppingCartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="在途物流"
              value={0}
              prefix={<CarOutlined />}
              styles={{ content: { color: "var(--color-warning)" } }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="今日利润"
              value={0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="CAD"
              styles={{ content: { color: "var(--color-success)" } }}
            />
          </Card>
        </Col>
      </Row>

      {/* V1.5 AI Usage Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="今日 AI 采集次数"
              value={usage?.today_count ?? 0}
              suffix={`/ ${usage?.today_limit ?? 100}`}
              prefix={<RobotOutlined />}
            />
            <Progress
              percent={
                usage
                  ? Math.round((usage.today_count / usage.today_limit) * 100)
                  : 0
              }
              size="small"
              style={{ marginTop: 8 }}
              strokeColor={
                usage && usage.today_count > usage.today_limit * 0.8
                  ? "#ff4d4f"
                  : "#1677ff"
              }
            />
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card>
            <Statistic
              title="活跃订阅"
              value={activeSubs}
              suffix="/ 20"
              prefix={<ThunderboltOutlined />}
              styles={{ content: { color: "var(--color-warning)" } }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card>
            <Statistic
              title="未读通知"
              value={unreadCount}
              prefix={<BellOutlined />}
              styles={{
                content: {
                  color: unreadCount > 0 ? "#ff4d4f" : "inherit",
                },
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* TOP5 Recommendations */}
      <Card
        title="🔥 今日 TOP5 推荐"
        extra={
          <span style={{ color: "var(--color-text-tertiary)" }}>
            {data?.date}
          </span>
        }
      >
        {loading ? (
          <div style={{ textAlign: "center", padding: 40 }}>
            <Spin size="large" />
          </div>
        ) : !data?.recommendations.length ? (
          <Empty description="暂无推荐数据" />
        ) : (
          <Row gutter={[16, 16]}>
            {data.recommendations.map((item, index) => (
              <Col xs={24} sm={12} lg={8} key={item.product_id}>
                <Card
                  size="small"
                  hoverable
                  style={{ borderLeft: `3px solid var(--color-primary)` }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          marginBottom: 8,
                        }}
                      >
                        <span
                          style={{
                            fontFamily: "var(--font-display)",
                            fontWeight: 700,
                            fontSize: "var(--text-lg)",
                            color: "var(--color-primary)",
                          }}
                        >
                          #{index + 1}
                        </span>
                        <span
                          style={{
                            fontWeight: 600,
                            fontSize: "var(--text-sm)",
                          }}
                        >
                          {item.product_name}
                        </span>
                      </div>
                      <div
                        style={{
                          fontSize: "var(--text-xs)",
                          color: "var(--color-text-secondary)",
                          marginBottom: 8,
                        }}
                      >
                        {item.category_name} · {item.sku}
                      </div>
                      <div style={{ display: "flex", gap: 12 }}>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "var(--text-sm)",
                          }}
                        >
                          🇨🇦 ${item.ca_price?.toFixed(2)}
                        </span>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "var(--text-sm)",
                          }}
                        >
                          🇨🇳 ¥{item.cn_price?.toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontWeight: 700,
                          fontSize: "var(--text-lg)",
                          color:
                            item.profit_rate >= 0.3
                              ? "var(--color-profit-high)"
                              : item.profit_rate >= 0.15
                                ? "var(--color-profit-medium)"
                                : "var(--color-profit-low)",
                        }}
                      >
                        {item.profit_rate >= 0 ? (
                          <ArrowUpOutlined />
                        ) : (
                          <ArrowDownOutlined />
                        )}{" "}
                        {(item.profit_rate * 100).toFixed(1)}%
                      </div>
                      <Tag
                        color={RISK_COLORS[item.risk_level]}
                        style={{ marginTop: 4 }}
                      >
                        {item.risk_level === "low"
                          ? "低风险"
                          : item.risk_level === "medium"
                            ? "中风险"
                            : "高风险"}
                      </Tag>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>
    </div>
  );
}
