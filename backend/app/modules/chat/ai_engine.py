"""AI Engine - Ollama LLM integration with Function Calling - BE-004."""

import json
import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.chat.service import ChatService
from app.modules.scraper.tools.base import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

# System prompt defining AI assistant capabilities
SYSTEM_PROMPT = """You are North Link AI Assistant, a cross-border e-commerce data analysis expert.

Your capabilities:
1. Search product prices on Canadian e-commerce platforms (Amazon.ca, BestBuy.ca, Walmart.ca, Costco.ca)
2. Search product prices on Chinese e-commerce platforms (JD, Taobao, Pinduoduo, 1688)
3. Search social media platforms (Xiaohongshu, Douyin, Xianyu)
4. Calculate cross-border profit margins
5. Create price tracking subscriptions

When a user asks about product prices, use the appropriate search tools.
When comparing prices across platforms, call multiple tools in parallel.
Always respond in the same language the user uses (Chinese or English).
Present results in a structured, easy-to-read format.

If you cannot find results, explain why and suggest alternatives."""


class AIEngine:
    """Orchestrates LLM inference and tool calling for chat interactions.

    Uses the OpenAI-compatible API provided by Ollama for local LLM inference.
    Falls back to a simplified mode when Ollama is unavailable.
    """

    def __init__(self) -> None:
        self._client = None
        self._model = getattr(settings, "ollama_model", "qwen2.5:72b")
        self._base_url = getattr(
            settings, "ollama_url", "http://localhost:11434/v1"
        )

    async def _get_client(self):
        """Lazily initialize the OpenAI-compatible async client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(
                    base_url=self._base_url,
                    api_key="ollama",
                )
            except ImportError:
                logger.warning(
                    "openai package not installed; AI features disabled"
                )
        return self._client

    async def check_health(self) -> bool:
        """Check if the Ollama LLM service is reachable."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                ollama_base = self._base_url.replace("/v1", "")
                resp = await client.get(f"{ollama_base}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def chat_stream(
        self,
        session_id: uuid.UUID,
        user_message: str,
        db: AsyncSession,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream AI response with tool calling support.

        Yields SSE-compatible event dicts:
          {type: "thinking", content: "..."}
          {type: "tool_call", tool: "...", params: {...}}
          {type: "progress", platform: "...", status: "running|done"}
          {type: "result", platform: "...", items: [...]}
          {type: "content", content: "...", metadata: {...}}
          {type: "done", message_id: "uuid"}
        """
        # Check LLM availability
        is_healthy = await self.check_health()
        if not is_healthy:
            yield {
                "type": "error",
                "content": "AI 助手暂时不可用，请使用手动查询模式。",
            }
            return

        yield {"type": "thinking", "content": "正在分析您的需求..."}

        client = await self._get_client()
        if client is None:
            yield {"type": "error", "content": "AI client not available"}
            return

        # Build message history
        chat_service = ChatService(db)
        session = await chat_service.get_session_detail(
            session_id, user_id=uuid.UUID(int=0)  # internal call, skip check
        )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if session and session.messages:
            for msg in session.messages:
                messages.append({"role": msg.role, "content": msg.content})

        # Get available tools
        tools = ToolRegistry.get_openai_functions()

        try:
            # First LLM call: intent parsing + tool selection
            response = await client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools if tools else None,
                stream=False,
            )

            choice = response.choices[0]
            tool_calls = getattr(choice.message, "tool_calls", None)

            if tool_calls:
                # Execute each tool call
                all_results: list[ToolResult] = []
                for tc in tool_calls:
                    tool_name = tc.function.name
                    tool_args = json.loads(tc.function.arguments)

                    yield {
                        "type": "tool_call",
                        "tool": tool_name,
                        "params": tool_args,
                    }

                    tool = ToolRegistry.get_tool_by_name(tool_name)
                    if tool is None:
                        yield {
                            "type": "progress",
                            "platform": tool_name,
                            "status": "error",
                        }
                        continue

                    platform = getattr(tool, "platform_id", tool_name)
                    yield {
                        "type": "progress",
                        "platform": platform,
                        "status": "running",
                    }

                    result = await tool.execute(**tool_args)
                    all_results.append(result)

                    yield {
                        "type": "progress",
                        "platform": platform,
                        "status": "done",
                        "items": result.items_count,
                    }

                    if result.data:
                        yield {
                            "type": "result",
                            "platform": platform,
                            "items": result.data,
                        }

                # Second LLM call: summarize results
                results_text = json.dumps(
                    [
                        {"platform": r.platform, "data": r.data}
                        for r in all_results
                        if r.success
                    ],
                    ensure_ascii=False,
                )
                messages.append(choice.message.model_dump())
                messages.append(
                    {
                        "role": "tool",
                        "content": results_text,
                        "tool_call_id": tool_calls[0].id,
                    }
                )

                summary_resp = await client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    stream=False,
                )
                summary = summary_resp.choices[0].message.content or ""

                # Build metadata for structured display
                metadata = _build_metadata(all_results)

                # Save assistant message
                msg = await chat_service.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=summary,
                    metadata=metadata,
                )

                yield {
                    "type": "content",
                    "content": summary,
                    "metadata": metadata,
                }
                yield {"type": "done", "message_id": str(msg.id)}
            else:
                # Pure text response (no tool needed)
                content = choice.message.content or ""
                msg = await chat_service.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=content,
                )
                yield {"type": "content", "content": content}
                yield {"type": "done", "message_id": str(msg.id)}

            await db.commit()

        except Exception as exc:
            logger.exception("AI Engine error during chat_stream")
            yield {
                "type": "error",
                "content": f"处理出错: {exc!s}",
            }


def _build_metadata(results: list[ToolResult]) -> dict:
    """Build structured metadata from tool results for frontend display."""
    all_items = []
    platforms = []
    for r in results:
        if r.success and r.data:
            platforms.append(r.platform)
            all_items.extend(r.data)

    if not all_items:
        return {}

    # Find price extremes
    priced_items = [i for i in all_items if i.get("price")]
    summary = {}
    if priced_items:
        lowest = min(priced_items, key=lambda x: x["price"])
        highest = max(priced_items, key=lambda x: x["price"])
        summary = {
            "lowest_price": {
                "platform": lowest.get("platform", ""),
                "price": lowest["price"],
            },
            "highest_price": {
                "platform": highest.get("platform", ""),
                "price": highest["price"],
            },
        }

    return {
        "type": "price_compare",
        "results": {
            "platforms": platforms,
            "items": all_items,
            "summary": summary,
        },
        "actions": ["subscribe", "favorite", "compare"],
    }
