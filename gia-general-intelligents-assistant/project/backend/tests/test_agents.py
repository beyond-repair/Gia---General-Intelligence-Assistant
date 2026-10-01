import pytest

from app.services.agents.code_execution_agent import CodeExecutionAgent
from app.services.agents.github_agent import GitHubAgent
from app.services.agents.llm_agent import LLMAgent
from app.services.agents.scraper_agent import ScraperAgent


@pytest.mark.asyncio
async def test_llm_stub_analyze():
    agent = LLMAgent()
    assert agent.mode == "stub"
    out = await agent.execute(
        {"prompt": "Analyze this task and break it down into steps: sort a list"}
    )
    assert out["status"] == "success"
    assert "Task analysis" in out["response"] or "stub" in out["response"].lower()


@pytest.mark.asyncio
async def test_llm_stub_codegen():
    agent = LLMAgent()
    out = await agent.execute(
        {
            "prompt": "Generate Python code to solve this task.\nProvide only the code, no explanations."
        }
    )
    assert out["status"] == "success"
    assert "def solve" in out["response"]


@pytest.mark.asyncio
async def test_scraper_stub_no_urls():
    agent = ScraperAgent()
    out = await agent.execute({"description": "research sorting algorithms"})
    assert out["status"] == "success"
    assert out["results"][0]["mode"] == "stub"


@pytest.mark.asyncio
async def test_github_stub():
    agent = GitHubAgent()
    out = await agent.execute({"description": "python sorting", "language": "python"})
    assert out["status"] == "success"
    assert out["mode"] == "stub"
    assert len(out["repositories"]) >= 1


@pytest.mark.asyncio
async def test_code_exec_stub():
    agent = CodeExecutionAgent()
    out = await agent.execute({"code": "print(1)", "language": "python"})
    assert out["status"] == "success"
    assert out["mode"] == "stub"
    assert out["result"]["exit_code"] == 0
