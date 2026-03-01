/**
 * Notification bell with dropdown panel — FE-020.
 * Shows unread count badge + click to expand notification list.
 */
import { useEffect, useState } from "react";
import { Badge, Drawer, List, Button, Tag, Empty, App } from "antd";
import { BellOutlined, CheckOutlined } from "@ant-design/icons";
import { notificationService } from "../../services/notificationService";
import type { Notification } from "../../types/chat";
import "./NotificationBell.css";

const TYPE_CONFIG: Record<string, { color: string; label: string }> = {
  price_alert: { color: "orange", label: "价格变动" },
  scraper_error: { color: "red", label: "采集错误" },
  system: { color: "blue", label: "系统" },
};

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const { message } = App.useApp();

  const fetchUnreadCount = () => {
    notificationService
      .getUnreadCount()
      .then(setUnreadCount)
      .catch(() => {});
  };

  useEffect(() => {
    fetchUnreadCount();
    // Poll every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30_000);
    return () => clearInterval(interval);
  }, []);

  const handleOpen = async () => {
    setOpen(true);
    setLoading(true);
    try {
      const data = await notificationService.getAll();
      setNotifications(data);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id: string) => {
    await notificationService.markRead(id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
    );
    setUnreadCount((c) => Math.max(0, c - 1));
  };

  const handleMarkAllRead = async () => {
    await notificationService.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
    message.success("已全部标记为已读");
  };

  return (
    <>
      <Badge count={unreadCount} size="small" offset={[-2, 2]}>
        <button className="notification-bell" onClick={handleOpen}>
          <BellOutlined />
        </button>
      </Badge>

      <Drawer
        title="通知中心"
        placement="right"
        open={open}
        onClose={() => setOpen(false)}
        width={380}
        extra={
          unreadCount > 0 && (
            <Button
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={handleMarkAllRead}
            >
              全部已读
            </Button>
          )
        }
      >
        <List
          loading={loading}
          dataSource={notifications}
          locale={{ emptyText: <Empty description="暂无通知" /> }}
          renderItem={(item) => {
            const typeConf = TYPE_CONFIG[item.type] ?? {
              color: "default",
              label: item.type,
            };
            return (
              <List.Item
                className={`notification-item ${item.is_read ? "read" : "unread"}`}
                actions={
                  !item.is_read
                    ? [
                        <Button
                          key="read"
                          type="link"
                          size="small"
                          onClick={() => handleMarkRead(item.id)}
                        >
                          标记已读
                        </Button>,
                      ]
                    : undefined
                }
              >
                <List.Item.Meta
                  title={
                    <span>
                      <Tag color={typeConf.color} style={{ marginRight: 8 }}>
                        {typeConf.label}
                      </Tag>
                      {item.title}
                    </span>
                  }
                  description={
                    <>
                      {item.content && (
                        <div className="notification-content">
                          {item.content}
                        </div>
                      )}
                      <span className="notification-time">
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </>
                  }
                />
              </List.Item>
            );
          }}
        />
      </Drawer>
    </>
  );
}
