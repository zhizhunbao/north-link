/**
 * Chat session sidebar list — FE-002.
 */
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons";
import { Button, Popconfirm } from "antd";
import { useChatStore } from "../../stores/useChatStore";
import "./ChatSessionList.css";

export function ChatSessionList() {
  const {
    sessions,
    activeSessionId,
    selectSession,
    deleteSession,
    clearActiveSession,
  } = useChatStore();

  return (
    <aside className="chat-sessions">
      <div className="chat-sessions-header">
        <h3>对话记录</h3>
        <Button
          type="text"
          icon={<PlusOutlined />}
          onClick={clearActiveSession}
          title="新对话"
        />
      </div>

      <div className="chat-sessions-list">
        {sessions.length === 0 && (
          <div className="chat-sessions-empty">
            <p>暂无对话记录</p>
            <p>开始一个新对话吧</p>
          </div>
        )}
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`chat-session-item ${
              activeSessionId === session.id ? "active" : ""
            }`}
            onClick={() => selectSession(session.id)}
          >
            <span className="chat-session-title">
              {session.title ?? "新对话"}
            </span>
            <span className="chat-session-time">
              {new Date(session.updated_at).toLocaleDateString()}
            </span>
            <Popconfirm
              title="确定删除该对话？"
              onConfirm={(e) => {
                e?.stopPropagation();
                deleteSession(session.id);
              }}
              okText="删除"
              cancelText="取消"
            >
              <Button
                type="text"
                size="small"
                icon={<DeleteOutlined />}
                className="chat-session-delete"
                onClick={(e) => e.stopPropagation()}
              />
            </Popconfirm>
          </div>
        ))}
      </div>
    </aside>
  );
}
