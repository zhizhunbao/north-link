/**
 * Chat input with send button — FE-004.
 */
import { useState, type KeyboardEvent } from "react";
import { SendOutlined } from "@ant-design/icons";
import { Button, Input } from "antd";
import "./ChatInput.css";

const { TextArea } = Input;

interface Props {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: Props) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <div className="chat-input-container">
        <TextArea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? "输入消息..."}
          disabled={disabled}
          autoSize={{ minRows: 1, maxRows: 4 }}
          className="chat-input-textarea"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          loading={disabled}
          className="chat-input-send"
        />
      </div>
      <p className="chat-input-hint">按 Enter 发送，Shift+Enter 换行</p>
    </div>
  );
}
