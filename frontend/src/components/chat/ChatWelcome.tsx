/**
 * Chat welcome / empty state — FE-005.
 */
import {
  RobotOutlined,
  SearchOutlined,
  BellOutlined,
  BarChartOutlined,
} from "@ant-design/icons";
import "./ChatWelcome.css";

const SUGGESTIONS = [
  { icon: <SearchOutlined />, text: "RTX 4090 加拿大哪里最便宜？" },
  {
    icon: <BarChartOutlined />,
    text: "帮我比较京东和亚马逊上 AirPods Pro 的价格",
  },
  { icon: <BellOutlined />, text: "当 PS5 降到 500 加币以下时通知我" },
  { icon: <SearchOutlined />, text: "小红书上有什么代购热门商品推荐？" },
];

export function ChatWelcome() {
  return (
    <div className="chat-welcome">
      <div className="chat-welcome-icon">
        <RobotOutlined />
      </div>
      <h2>North Link AI 助手</h2>
      <p>
        我可以帮你搜索跨境电商价格、比较多平台商品、
        计算利润、追踪价格变动，以及浏览社交平台热门内容。
      </p>
      <div className="chat-welcome-suggestions">
        {SUGGESTIONS.map((s, i) => (
          <button key={i} className="chat-welcome-suggestion">
            <span className="suggestion-icon">{s.icon}</span>
            <span>{s.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
