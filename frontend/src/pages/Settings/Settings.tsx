/**
 * Settings page — SET-003.
 * System configuration + password change.
 */
import { useState } from "react";
import {
  Card,
  Tabs,
  Form,
  Input,
  Button,
  InputNumber,
  Switch,
  Space,
  Divider,
  message,
} from "antd";
import { SaveOutlined, LockOutlined, ExportOutlined } from "@ant-design/icons";
import { authService } from "../../services/authService";
import { useAuthStore } from "../../stores/useAuthStore";

function SystemTab() {
  return (
    <Form layout="vertical" initialValues={{ tariff_rate: 13, exchange_margin: 0.02 }}>
      <Card title="税率设置" size="small" style={{ marginBottom: 16 }}>
        <Form.Item name="tariff_rate" label="默认关税税率 (%)">
          <InputNumber min={0} max={100} precision={1} style={{ width: 200 }} />
        </Form.Item>
        <Form.Item name="consumption_tax" label="消费税 (%)">
          <InputNumber min={0} max={100} precision={1} style={{ width: 200 }} />
        </Form.Item>
      </Card>

      <Card title="汇率配置" size="small" style={{ marginBottom: 16 }}>
        <Form.Item name="exchange_margin" label="汇率溢价 (%)">
          <InputNumber min={0} max={10} precision={2} style={{ width: 200 }} />
        </Form.Item>
        <Form.Item name="auto_update" label="自动更新汇率" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Card>

      <Card title="运费模板" size="small" style={{ marginBottom: 16 }}>
        <Form.Item name="default_freight" label="默认运费 (CAD/kg)">
          <InputNumber min={0} precision={2} style={{ width: 200 }} />
        </Form.Item>
      </Card>

      <Space>
        <Button type="primary" icon={<SaveOutlined />}>
          保存设置
        </Button>
        <Button icon={<ExportOutlined />}>
          数据备份导出
        </Button>
      </Space>
    </Form>
  );
}

function PasswordTab() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const logout = useAuthStore((s) => s.logout);

  const handleSubmit = async (values: { old_password: string; new_password: string }) => {
    setLoading(true);
    try {
      await authService.changePassword(values);
      message.success("密码修改成功，请重新登录");
      logout();
    } catch {
      message.error("密码修改失败，请检查旧密码");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="修改密码" style={{ maxWidth: 480 }}>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item
          name="old_password"
          label="当前密码"
          rules={[{ required: true, message: "请输入当前密码" }]}
        >
          <Input.Password prefix={<LockOutlined />} />
        </Form.Item>

        <Divider />

        <Form.Item
          name="new_password"
          label="新密码"
          rules={[
            { required: true, message: "请输入新密码" },
            { min: 6, message: "密码至少 6 位" },
          ]}
        >
          <Input.Password prefix={<LockOutlined />} />
        </Form.Item>

        <Form.Item
          name="confirm_password"
          label="确认新密码"
          dependencies={["new_password"]}
          rules={[
            { required: true, message: "请确认新密码" },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("new_password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error("两次密码不一致"));
              },
            }),
          ]}
        >
          <Input.Password prefix={<LockOutlined />} />
        </Form.Item>

        <Button type="primary" htmlType="submit" loading={loading}>
          修改密码
        </Button>
      </Form>
    </Card>
  );
}

export function SettingsPage() {
  return (
    <div>
      <div className="content-header">
        <h1>⚙️ 系统设置</h1>
      </div>
      <Tabs
        defaultActiveKey="system"
        items={[
          { key: "system", label: "系统参数", children: <SystemTab /> },
          { key: "password", label: "密码修改", children: <PasswordTab /> },
        ]}
      />
    </div>
  );
}
