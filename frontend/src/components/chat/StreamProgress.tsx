/**
 * SSE stream progress indicator — FE-011.
 */
import { Steps, Spin } from "antd";
import {
  LoadingOutlined,
  CheckCircleOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import type { SSEEvent } from "../../types/chat";
import "./StreamProgress.css";

interface Props {
  events: SSEEvent[];
}

export function StreamProgress({ events }: Props) {
  const steps = events
    .filter((e) => ["thinking", "tool_call", "progress"].includes(e.type))
    .map((e) => {
      if (e.type === "thinking") {
        return {
          title: "分析中",
          description: e.content,
          icon: <LoadingOutlined spin />,
        };
      }
      if (e.type === "tool_call") {
        return {
          title: `调用 ${e.tool}`,
          description: JSON.stringify(e.params),
          icon: <SearchOutlined />,
        };
      }
      if (e.type === "progress") {
        const isDone = e.status === "done";
        return {
          title: e.platform ?? "采集中",
          description: isDone ? `完成 (${e.items ?? 0} 条结果)` : "采集中...",
          icon: isDone ? (
            <CheckCircleOutlined style={{ color: "#52c41a" }} />
          ) : (
            <LoadingOutlined spin />
          ),
        };
      }
      return { title: `${e.type}`, description: "", icon: null };
    });

  if (steps.length === 0) {
    return (
      <div className="stream-progress">
        <Spin size="small" /> <span>正在处理...</span>
      </div>
    );
  }

  return (
    <div className="stream-progress">
      <Steps
        direction="vertical"
        size="small"
        current={steps.length - 1}
        items={steps}
      />
    </div>
  );
}
