"""GitHub agent — stub by default. Set GIA_ALLOW_NETWORK=1 to search GitHub."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from loguru import logger

from .base_agent import BaseAgent


class GitHubAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._client = None

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        query = task_input.get("query") or task_input.get("description") or ""
        language = task_input.get("language", "python")
        allow_network = os.getenv("GIA_ALLOW_NETWORK", "").lower() in (
            "1",
            "true",
            "yes",
        )

        if not allow_network:
            return {
                "status": "success",
                "mode": "stub",
                "repositories": [
                    {
                        "name": "demo/stub-repo",
                        "url": "https://github.com/example/stub-repo",
                        "description": f"[stub] Would search: {query[:120]}",
                        "stars": 0,
                        "language": language,
                    }
                ],
                "code_samples": [
                    {
                        "repository": "demo/stub-repo",
                        "file_name": "solution.py",
                        "code": "def demo():\n    return 'stub'\n",
                        "url": None,
                    }
                ],
            }

        try:
            from github import Github

            token = os.getenv("GITHUB_TOKEN")
            self._client = Github(token) if token else Github()
            repositories = self._search_repositories(query, language)
            code_samples = self._extract_code_samples(repositories)
            return {
                "status": "success",
                "mode": "live",
                "repositories": repositories,
                "code_samples": code_samples,
            }
        except Exception as e:
            logger.error(f"GitHub agent error: {e}")
            return {"status": "error", "error": str(e)}

    def _search_repositories(self, query: str, language: str) -> List[Dict[str, Any]]:
        search_query = f"{query} language:{language}"
        repositories = []
        results = self._client.search_repositories(
            query=search_query, sort="stars", order="desc"
        )
        for repo in results[:5]:
            repositories.append(
                {
                    "name": repo.full_name,
                    "url": repo.html_url,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "language": repo.language,
                }
            )
        return repositories

    def _extract_code_samples(
        self, repositories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        samples: List[Dict[str, Any]] = []
        for repo in repositories[:2]:
            try:
                repo_obj = self._client.get_repo(repo["name"])
                contents = repo_obj.get_contents("")
                if not isinstance(contents, list):
                    contents = [contents]
                for content in contents:
                    if content.type == "file" and content.name.endswith(".py"):
                        samples.append(
                            {
                                "repository": repo["name"],
                                "file_name": content.name,
                                "code": content.decoded_content.decode()[:2000],
                                "url": content.html_url,
                            }
                        )
                        break
            except Exception as e:
                logger.error(f"Error extracting code from {repo['name']}: {e}")
        return samples
