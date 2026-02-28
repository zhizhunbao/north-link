/**
 * Merchant management page — MERCH-006.
 * Card list with category grouping and CRUD.
 */
import { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Button,
  Tag,
  Spin,
  Empty,
  Avatar,
  Modal,
  Form,
  Input,
  Select,
  message,
} from "antd";
import {
  PlusOutlined,
  PhoneOutlined,
  WechatOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { merchantService, type Merchant } from "../../services/merchantService";

const RATINGS: Record<string, { color: string; label: string }> = {
  S: { color: "gold", label: "S 级" },
  A: { color: "green", label: "A 级" },
  B: { color: "blue", label: "B 级" },
  C: { color: "default", label: "C 级" },
};

export function MerchantPage() {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Merchant | null>(null);
  const [form] = Form.useForm();

  const fetchMerchants = () => {
    setLoading(true);
    merchantService
      .getList({ page: 1, page_size: 100 })
      .then((res) => setMerchants(res.data.items))
      .catch(() => setMerchants([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMerchants();
  }, []);

  const handleSave = async (values: Partial<Merchant>) => {
    try {
      if (editing) {
        await merchantService.update(editing.id, values);
        message.success("商户更新成功");
      } else {
        await merchantService.create(values);
        message.success("商户添加成功");
      }
      setModalOpen(false);
      setEditing(null);
      form.resetFields();
      fetchMerchants();
    } catch {
      message.error("操作失败");
    }
  };

  const handleDelete = (id: string) => {
    Modal.confirm({
      title: "确认删除?",
      content: "删除后不可恢复",
      okText: "删除",
      okType: "danger",
      cancelText: "取消",
      onOk: async () => {
        await merchantService.delete(id);
        message.success("删除成功");
        fetchMerchants();
      },
    });
  };

  const openEdit = (merchant: Merchant) => {
    setEditing(merchant);
    form.setFieldsValue(merchant);
    setModalOpen(true);
  };

  return (
    <div>
      <div className="content-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>👥 商户管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditing(null);
            form.resetFields();
            setModalOpen(true);
          }}
        >
          添加商户
        </Button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <Spin size="large" />
        </div>
      ) : merchants.length === 0 ? (
        <Card>
          <Empty description={'暂无商户，点击"添加商户"开始'} />
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {merchants.map((m) => (
            <Col xs={24} sm={12} lg={8} key={m.id}>
              <Card
                hoverable
                actions={[
                  <EditOutlined key="edit" onClick={() => openEdit(m)} />,
                  <DeleteOutlined key="delete" onClick={() => handleDelete(m.id)} />,
                ]}
              >
                <Card.Meta
                  avatar={
                    <Avatar
                      size={48}
                      icon={<UserOutlined />}
                      style={{ background: "var(--color-primary)" }}
                    />
                  }
                  title={
                    <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      {m.name}
                      <Tag color={RATINGS[m.rating]?.color ?? "default"}>
                        {RATINGS[m.rating]?.label ?? m.rating}
                      </Tag>
                    </span>
                  }
                  description={
                    <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: 8 }}>
                      <span>
                        <UserOutlined /> {m.contact_person}
                      </span>
                      <span>
                        <PhoneOutlined /> {m.phone || "***"}
                      </span>
                      <span>
                        <WechatOutlined /> {m.wechat || "***"}
                      </span>
                    </div>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* Add/Edit Modal */}
      <Modal
        title={editing ? "编辑商户" : "添加商户"}
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        onOk={() => form.submit()}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item name="name" label="商户名称" rules={[{ required: true }]}>
            <Input placeholder="请输入商户名称" />
          </Form.Item>
          <Form.Item name="contact_person" label="联系人" rules={[{ required: true }]}>
            <Input placeholder="请输入联系人" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="phone" label="手机号">
                <Input placeholder="手机号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="wechat" label="微信">
                <Input placeholder="微信号" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="address" label="地址">
            <Input.TextArea placeholder="地址" rows={2} />
          </Form.Item>
          <Form.Item name="rating" label="评级" initialValue="B">
            <Select
              options={Object.entries(RATINGS).map(([k, v]) => ({
                value: k,
                label: v.label,
              }))}
            />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} placeholder="备注" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
