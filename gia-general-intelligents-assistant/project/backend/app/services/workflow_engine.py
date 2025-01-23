from typing import Dict, Any, List
import yaml
from loguru import logger
from .agents.scraper_agent import ScraperAgent
from .agents.github_agent import GitHubAgent
from .agents.code_execution_agent import CodeExecutionAgent
from .agents.llm_agent import LLMAgent

class WorkflowEngine:
    def __init__(self):
        self.agents = {
            "scraper": ScraperAgent(),
            "github": GitHubAgent(),
            "code_execution": CodeExecutionAgent(),
            "llm": LLMAgent()  # Add the LLM agent
        }

    # ... rest of the file remains the same ...