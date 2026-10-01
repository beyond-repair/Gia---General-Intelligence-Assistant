"""Scraper agent — stub by default (no network). Set GIA_ALLOW_NETWORK=1 to fetch."""
from __future__ import annotations

import os
from typing import Any, Dict, List

from loguru import logger

from .base_agent import BaseAgent


class ScraperAgent(BaseAgent):
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        description = task_input.get("description", "")
        urls = task_input.get("urls") or self._extract_urls(description)
        allow_network = os.getenv("GIA_ALLOW_NETWORK", "").lower() in (
            "1",
            "true",
            "yes",
        )

        if not urls:
            return {
                "status": "success",
                "results": [
                    {
                        "url": None,
                        "content": {
                            "title": "stub-info",
                            "content": (
                                f"[stub] No URLs in task. "
                                f"Would research: {description[:200]}"
                            ),
                        },
                        "status": "success",
                        "mode": "stub",
                    }
                ],
            }

        if not allow_network:
            return {
                "status": "success",
                "results": [
                    {
                        "url": url,
                        "content": {
                            "title": "stub-skip",
                            "content": f"[stub] Skipped fetch for {url} (GIA_ALLOW_NETWORK unset)",
                        },
                        "status": "success",
                        "mode": "stub",
                    }
                    for url in urls
                ],
            }

        results = []
        try:
            import aiohttp
            from bs4 import BeautifulSoup
        except ImportError as e:
            return {"status": "error", "error": f"Network deps missing: {e}", "results": []}

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=10) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        title = soup.title.string if soup.title else ""
                        main = soup.find("main") or soup.find("article") or soup.find("body")
                        text = main.get_text(strip=True)[:2000] if main else ""
                        results.append(
                            {
                                "url": url,
                                "content": {"title": title, "content": text},
                                "status": "success",
                                "mode": "live",
                            }
                        )
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    results.append({"url": url, "error": str(e), "status": "failed"})

        return {"status": "success", "results": results}

    def _extract_urls(self, description: str) -> List[str]:
        return [
            w
            for w in description.split()
            if w.startswith(("http://", "https://"))
        ]
