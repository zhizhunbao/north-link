/**
 * V1.5 Chat type definitions — FE-012.
 */

export interface ChatSession {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  metadata_: ChatMessageMetadata;
  created_at: string;
}

export interface ChatMessageMetadata {
  type?: "price_compare" | "social_search" | "profit_calc";
  results?: {
    platforms: string[];
    items: ProductItem[];
    summary?: {
      lowest_price?: { platform: string; price: number };
      highest_price?: { platform: string; price: number };
    };
  };
  actions?: string[];
}

export interface ProductItem {
  platform: string;
  product_name: string;
  sku?: string;
  price: number;
  original_price?: number;
  currency: string;
  stock_status?: string;
  url?: string;
  image_url?: string;
  rating?: number;
  review_count?: number;
}

/** SSE event from backend */
export interface SSEEvent {
  type:
    | "thinking"
    | "tool_call"
    | "progress"
    | "result"
    | "content"
    | "done"
    | "error";
  content?: string;
  platform?: string;
  status?: string;
  items?: ProductItem[];
  metadata?: ChatMessageMetadata;
  message_id?: string;
  tool?: string;
  params?: Record<string, unknown>;
}

export interface Subscription {
  id: string;
  platform: string;
  target_type: "url" | "keyword";
  target_value: string;
  threshold: number;
  status: "active" | "paused" | "expired";
  last_price: number | null;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  type: "price_alert" | "scraper_error" | "system";
  title: string;
  content: string | null;
  metadata_: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface ScraperUsage {
  today_count: number;
  today_limit: number;
  month_count: number;
  by_platform: Record<string, number>;
}
