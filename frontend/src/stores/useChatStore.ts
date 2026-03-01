/**
 * Chat state management using Zustand — FE-008.
 */
import { create } from "zustand";
import { chatService } from "../services/chatService";
import type { ChatSession, ChatMessage, SSEEvent } from "../types/chat";

interface ChatState {
  /* State */
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  streamEvents: SSEEvent[];

  /* Actions */
  fetchSessions: () => Promise<void>;
  selectSession: (id: string) => Promise<void>;
  deleteSession: (id: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  clearActiveSession: () => void;
  addStreamEvent: (event: SSEEvent) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isLoading: false,
  isStreaming: false,
  streamEvents: [],

  fetchSessions: async () => {
    set({ isLoading: true });
    try {
      const sessions = await chatService.getSessions();
      set({ sessions, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  selectSession: async (id: string) => {
    set({ isLoading: true, activeSessionId: id });
    try {
      const detail = await chatService.getSession(id);
      set({ messages: detail.messages, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  deleteSession: async (id: string) => {
    await chatService.deleteSession(id);
    const { activeSessionId } = get();
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
      ...(activeSessionId === id
        ? { activeSessionId: null, messages: [] }
        : {}),
    }));
  },

  sendMessage: async (content: string) => {
    const { activeSessionId } = get();

    // Optimistically add user message
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      metadata_: {},
      created_at: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamEvents: [],
    }));

    try {
      const response = await chatService.sendMessage(
        content,
        activeSessionId ?? undefined,
      );

      if (!response.ok || !response.body) {
        throw new Error("SSE connection failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let assistantContent = "";
      let assistantMetadata = {};
      const newSessionId = activeSessionId;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const event: SSEEvent = JSON.parse(line.slice(6));
              get().addStreamEvent(event);

              if (event.type === "content" && event.content) {
                assistantContent = event.content;
                if (event.metadata) {
                  assistantMetadata = event.metadata;
                }
              }
              if (event.type === "done" && event.message_id) {
                // Final assistant message
                const assistantMsg: ChatMessage = {
                  id: event.message_id,
                  role: "assistant",
                  content: assistantContent,
                  metadata_: assistantMetadata,
                  created_at: new Date().toISOString(),
                };
                set((state) => ({
                  messages: [...state.messages, assistantMsg],
                }));
              }
              if (event.type === "error") {
                const errorMsg: ChatMessage = {
                  id: `error-${Date.now()}`,
                  role: "assistant",
                  content: event.content ?? "处理出错，请重试。",
                  metadata_: {},
                  created_at: new Date().toISOString(),
                };
                set((state) => ({
                  messages: [...state.messages, errorMsg],
                }));
              }
            } catch {
              /* ignore parse errors */
            }
          }
        }
      }

      // If new session was created, refresh session list
      if (!activeSessionId && newSessionId) {
        set({ activeSessionId: newSessionId });
      }
      await get().fetchSessions();
    } catch {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "网络连接失败，请检查网络后重试。",
        metadata_: {},
        created_at: new Date().toISOString(),
      };
      set((state) => ({
        messages: [...state.messages, errorMsg],
      }));
    } finally {
      set({ isStreaming: false });
    }
  },

  clearActiveSession: () => {
    set({ activeSessionId: null, messages: [], streamEvents: [] });
  },

  addStreamEvent: (event: SSEEvent) => {
    set((state) => ({ streamEvents: [...state.streamEvents, event] }));
  },
}));
