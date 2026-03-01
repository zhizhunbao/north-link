/**
 * Chat API service + SSE client — FE-006.
 */
import { api } from "./api";
import type { ChatSession, ChatMessage } from "../types/chat";

export const chatService = {
  /** List all chat sessions */
  getSessions: () =>
    api.get<ChatSession[]>("/api/v1/chat/sessions").then((r) => r.data),

  /** Get session with full message history */
  getSession: (id: string) =>
    api
      .get<
        ChatSession & { messages: ChatMessage[] }
      >(`/api/v1/chat/sessions/${id}`)
      .then((r) => r.data),

  /** Delete a session */
  deleteSession: (id: string) =>
    api.delete(`/api/v1/chat/sessions/${id}`).then((r) => r.data),

  /**
   * Send a message and receive SSE stream.
   * Returns an EventSource-like reader for processing events.
   */
  sendMessage: (content: string, sessionId?: string) => {
    const token = localStorage.getItem("access_token") ?? "";
    const apiBase = import.meta.env.VITE_API_URL ?? "";

    return fetch(`${apiBase}/api/v1/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        content,
        session_id: sessionId ?? null,
      }),
    });
  },
};
