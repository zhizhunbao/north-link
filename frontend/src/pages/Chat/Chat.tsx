/**
 * AI Chat page — FE-001.
 * Main chat interface with session sidebar + message area.
 */
import { useEffect } from "react";
import { useChatStore } from "../../stores/useChatStore";
import { ChatSessionList } from "../../components/chat/ChatSessionList";
import { ChatMessageList } from "../../components/chat/ChatMessageList";
import { ChatInput } from "../../components/chat/ChatInput";
import { ChatWelcome } from "../../components/chat/ChatWelcome";
import { StreamProgress } from "../../components/chat/StreamProgress";
import "./Chat.css";

export function ChatPage() {
  const {
    activeSessionId,
    messages,
    isStreaming,
    streamEvents,
    fetchSessions,
    sendMessage,
  } = useChatStore();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-page">
      <ChatSessionList />
      <div className="chat-main">
        {hasMessages ? (
          <>
            <ChatMessageList messages={messages} />
            {isStreaming && <StreamProgress events={streamEvents} />}
          </>
        ) : (
          <ChatWelcome />
        )}
        <ChatInput
          onSend={sendMessage}
          disabled={isStreaming}
          placeholder={
            activeSessionId
              ? "继续对话..."
              : "输入您的问题，例如：RTX 4090 加拿大哪里最便宜？"
          }
        />
      </div>
    </div>
  );
}
