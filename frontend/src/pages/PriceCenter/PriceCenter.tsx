/**
 * Price Center page — PRICE-008.
 * Product card list with filters, search, and sorting.
 */
import { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Input,
  Select,
  Tag,
  Pagination,
  Spin,
  Empty,
  Space,
  Badge,
} from "antd";
import { SearchOutlined, HeartOutlined, HeartFilled } from "@ant-design/icons";
import { priceService, type Product, type ProductListParams } from "../../services/priceService";
import "./PriceCenter.css";

const CONDITIONS: Record<string, { label: string; color: string }> = {
  new: { label: "全新", color: "green" },
  used: { label: "二手", color: "orange" },
  refurbished: { label: "翻新", color: "blue" },
  clearance: { label: "清仓", color: "red" },
};

const SORT_OPTIONS = [
  { value: "price_asc", label: "价格 ↑" },
  { value: "price_desc", label: "价格 ↓" },
  { value: "profit_rate", label: "利润率" },
  { value: "newest", label: "最新" },
];

export function PriceCenterPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [params, setParams] = useState<ProductListParams>({
    page: 1,
    page_size: 20,
  });

  useEffect(() => {
    let cancelled = false;
    priceService
      .getProducts(params)
      .then((res) => {
        if (!cancelled) { setProducts(res.data.items); setTotal(res.data.total); setLoading(false); }
      })
      .catch(() => {
        if (!cancelled) { setProducts([]); setTotal(0); setLoading(false); }
      });
    return () => { cancelled = true; };
  }, [params]);

  const toggleFavorite = (productId: string) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(productId)) next.delete(productId);
      else next.add(productId);
      return next;
    });
  };

  const updateParams = (update: Partial<ProductListParams>) => {
    setParams((prev) => ({ ...prev, ...update, page: 1 }));
  };

  return (
    <div>
      <div className="content-header">
        <h1>📊 比价中心</h1>
      </div>

      {/* Filter Bar */}
      <Card className="filter-bar" size="small">
        <Space wrap size="middle">
          <Input
            placeholder="搜索商品名/SKU"
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: 240 }}
            onChange={(e) => updateParams({ search: e.target.value || undefined })}
            data-testid="price-search"
          />
          <Select
            placeholder="商品状态"
            allowClear
            style={{ width: 120 }}
            onChange={(val) => updateParams({ condition: val })}
            options={Object.entries(CONDITIONS).map(([k, v]) => ({
              value: k,
              label: v.label,
            }))}
          />
          <Select
            placeholder="排序"
            style={{ width: 120 }}
            defaultValue="newest"
            onChange={(val) => updateParams({ sort_by: val })}
            options={SORT_OPTIONS}
          />
        </Space>
      </Card>

      {/* Product Grid */}
      {loading ? (
        <div className="loading-center">
          <Spin size="large" />
        </div>
      ) : products.length === 0 ? (
        <Card style={{ marginTop: 16 }}>
          <Empty description="暂无商品数据" />
        </Card>
      ) : (
        <>
          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            {products.map((product) => (
              <Col xs={24} sm={12} lg={8} xl={6} key={product.id}>
                <Card hoverable className="product-card">
                  <div className="product-card-header">
                    <Tag color={CONDITIONS[product.condition]?.color ?? "default"}>
                      {CONDITIONS[product.condition]?.label ?? product.condition}
                    </Tag>
                    <button
                      className="favorite-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavorite(product.id);
                      }}
                    >
                      {favorites.has(product.id) ? (
                        <HeartFilled style={{ color: "var(--color-danger)" }} />
                      ) : (
                        <HeartOutlined />
                      )}
                    </button>
                  </div>

                  <h3 className="product-name">{product.name}</h3>
                  <div className="product-meta">
                    <span>{product.sku}</span>
                    {product.brand && (
                      <Badge
                        color="var(--color-primary)"
                        text={product.brand}
                        style={{ fontSize: "var(--text-xs)" }}
                      />
                    )}
                  </div>

                  <div className="product-prices">
                    <div className="price-item">
                      <span className="price-label">🇨🇦 加拿大</span>
                      <span className="price-value mono">-</span>
                    </div>
                    <div className="price-item">
                      <span className="price-label">🇨🇳 国内</span>
                      <span className="price-value mono">-</span>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>

          <div className="pagination-container">
            <Pagination
              current={params.page}
              pageSize={params.page_size}
              total={total}
              showSizeChanger
              showTotal={(t) => `共 ${t} 件商品`}
              onChange={(page, pageSize) =>
                setParams((prev) => ({ ...prev, page, page_size: pageSize }))
              }
            />
          </div>
        </>
      )}
    </div>
  );
}
