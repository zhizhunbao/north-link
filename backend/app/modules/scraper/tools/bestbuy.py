"""BestBuy.ca Developer API scraper tool - BE-006.

Uses the official BestBuy Developer API for product search.
This is the simplest platform (no anti-scraping) and serves as
the reference implementation for the Tool pattern.
"""

import logging
from typing import Any

import httpx

from app.config import settings
from app.modules.scraper.cache import get_cached_result, set_cached_result
from app.modules.scraper.tools.base import BaseTool, ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

BESTBUY_API_BASE = "https://api.bestbuy.com/v1"


class BestBuyTool(BaseTool):
    """Search products on BestBuy.ca via official Developer API."""

    name = "search_bestbuy"
    description = (
        "Search for products on BestBuy.ca (Canada). "
        "Returns product name, price in CAD, SKU, rating, stock status, "
        "and product URL. Best for electronics and appliances."
    )
    parameters = {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "Product search keywords, e.g. 'RTX 4090'",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (1-10)",
                "default": 5,
            },
        },
        "required": ["keywords"],
    }
    platform_id = "bestbuy_ca"

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Search BestBuy API for products matching keywords."""
        keywords = kwargs.get("keywords", "")
        max_results = min(kwargs.get("max_results", 5), 10)

        if not keywords:
            return ToolResult(
                success=False,
                error="Keywords are required",
                platform=self.platform_id,
            )

        # Check cache first
        cached = await get_cached_result(self.platform_id, keywords)
        if cached:
            return ToolResult(
                success=True,
                data=cached,
                platform=self.platform_id,
                cached=True,
                items_count=len(cached),
            )

        api_key = getattr(settings, "bestbuy_api_key", "")
        if not api_key:
            return ToolResult(
                success=False,
                error="BestBuy API key not configured",
                platform=self.platform_id,
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{BESTBUY_API_BASE}/products(search={keywords})",
                    params={
                        "apiKey": api_key,
                        "format": "json",
                        "show": (
                            "name,sku,salePrice,regularPrice,"
                            "customerRating,customerRatingCount,"
                            "url,image,inStockOnline"
                        ),
                        "pageSize": max_results,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            products = data.get("products", [])
            items = [
                {
                    "platform": self.platform_id,
                    "product_name": p.get("name", ""),
                    "sku": str(p.get("sku", "")),
                    "price": p.get("salePrice") or p.get("regularPrice"),
                    "original_price": p.get("regularPrice"),
                    "currency": "CAD",
                    "stock_status": (
                        "in_stock" if p.get("inStockOnline") else "out_of_stock"
                    ),
                    "url": p.get("url", ""),
                    "image_url": p.get("image", ""),
                    "rating": p.get("customerRating"),
                    "review_count": p.get("customerRatingCount"),
                }
                for p in products
            ]

            # Cache results
            if items:
                await set_cached_result(self.platform_id, keywords, items)

            return ToolResult(
                success=True,
                data=items,
                platform=self.platform_id,
                cached=False,
                items_count=len(items),
            )

        except httpx.HTTPStatusError as exc:
            logger.warning("BestBuy API error: %s", exc.response.status_code)
            return ToolResult(
                success=False,
                error=f"BestBuy API error: {exc.response.status_code}",
                platform=self.platform_id,
            )
        except Exception as exc:
            logger.exception("BestBuy tool execution error")
            return ToolResult(
                success=False,
                error=str(exc),
                platform=self.platform_id,
            )


# Auto-register on import
ToolRegistry.register(BestBuyTool())
