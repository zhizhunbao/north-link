/**
 * Chat message list with rich content — FE-003.
 */
import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types/chat";
import { PriceCompareTable } from "./PriceCompareTable";
import { RobotOutlined, UserOutlined } from "@ant-design/icons";
import "./ChatMessageList.css";

interface Props {
  messages: ChatMessage[];
}

export function ChatMessageList({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-messages">
      {messages.map((msg) => (
        <div key={msg.id} className={`chat-message chat-message-${msg.role}`}>
          <div className="chat-message-avatar">
            {msg.role === "user" ? <UserOutlined /> : <RobotOutlined />}
          </div>
          <div className="chat-message-body">
            <div className="chat-message-content">{msg.content}</div>
            {/* Rich content: price comparison table */}
            {msg.metadata_?.type === "price_compare" &&
              msg.metadata_.results?.items && (
                <PriceCompareTable items={msg.metadata_.results.items} />
              )}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
