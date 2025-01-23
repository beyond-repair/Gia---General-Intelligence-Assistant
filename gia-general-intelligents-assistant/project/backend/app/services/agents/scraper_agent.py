from typing import Dict, Any, List
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from .base_agent import BaseAgent

class ScraperAgent(BaseAgent):
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        urls = task_input.get("urls", [])
        if not urls:
            urls = await self._extract_urls_from_task(task_input.get("description", ""))
        
        results = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    result = await self._scrape_url(session, url)
                    results.append({"url": url, "content": result, "status": "success"})
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    results.append({"url": url, "error": str(e), "status": "failed"})
        
        return {"results": results}

    async def _extract_urls_from_task(self, description: str) -> List[str]:
        # Implement URL extraction from task description
        # This could be enhanced with NLP or regex patterns
        words = description.split()
        urls = [word for word in words if word.startswith(("http://", "https://"))]
        return urls

    async def _scrape_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract relevant information
            title = soup.title.string if soup.title else ""
            main_content = soup.find("main") or soup.find("article") or soup.find("body")
            text_content = main_content.get_text(strip=True) if main_content else ""
            
            return {
                "title": title,
                "content": text_content,
                "metadata": {
                    "status_code": response.status,
                    "headers": dict(response.headers)
                }
            }