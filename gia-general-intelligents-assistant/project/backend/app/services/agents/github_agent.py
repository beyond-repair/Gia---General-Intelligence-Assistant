from typing import Dict, Any, List
from github import Github
from loguru import logger
from .base_agent import BaseAgent

class GitHubAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.github = Github()  # For unauthenticated access

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        query = task_input.get("query") or task_input.get("description")
        language = task_input.get("language", "python")
        
        try:
            repositories = await self._search_repositories(query, language)
            code_samples = await self._extract_code_samples(repositories)
            return {
                "status": "success",
                "repositories": repositories,
                "code_samples": code_samples
            }
        except Exception as e:
            logger.error(f"GitHub agent error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _search_repositories(self, query: str, language: str) -> List[Dict[str, Any]]:
        search_query = f"{query} language:{language}"
        repositories = []
        
        try:
            results = self.github.search_repositories(
                query=search_query,
                sort="stars",
                order="desc"
            )
            
            for repo in results[:5]:  # Limit to top 5 results
                repositories.append({
                    "name": repo.name,
                    "url": repo.html_url,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "language": repo.language
                })
        except Exception as e:
            logger.error(f"Error searching repositories: {str(e)}")
            
        return repositories

    async def _extract_code_samples(self, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        code_samples = []
        
        for repo in repositories:
            try:
                repo_obj = self.github.get_repo(repo["name"])
                contents = repo_obj.get_contents("")
                
                for content in contents:
                    if content.type == "file" and content.name.endswith(".py"):
                        code_samples.append({
                            "repository": repo["name"],
                            "file_name": content.name,
                            "code": content.decoded_content.decode(),
                            "url": content.html_url
                        })
            except Exception as e:
                logger.error(f"Error extracting code from {repo['name']}: {str(e)}")
                
        return code_samples