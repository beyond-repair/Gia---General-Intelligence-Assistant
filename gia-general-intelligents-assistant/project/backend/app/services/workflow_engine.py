"""Workflow engine — runs YAML-described agent nodes in order."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from .agents.code_execution_agent import CodeExecutionAgent
from .agents.github_agent import GitHubAgent
from .agents.llm_agent import LLMAgent
from .agents.scraper_agent import ScraperAgent


_REF = re.compile(r"\$\{([^}]+)\}")


class WorkflowEngine:
    def __init__(self):
        self.agents = {
            "scraper": ScraperAgent(),
            "github": GitHubAgent(),
            "code_execution": CodeExecutionAgent(),
            "llm": LLMAgent(),
        }

    def load_workflow(self, workflow_yaml: str) -> Dict[str, Any]:
        return yaml.safe_load(workflow_yaml)

    def _resolve(self, value: Any, context: Dict[str, Any]) -> Any:
        if isinstance(value, str):

            def repl(match: re.Match) -> str:
                path = match.group(1).strip()
                parts = path.split(".")
                cur: Any = context
                for part in parts:
                    if isinstance(cur, dict) and part in cur:
                        cur = cur[part]
                    else:
                        return match.group(0)
                if cur is None:
                    return ""
                if isinstance(cur, (dict, list)):
                    return str(cur)
                return str(cur)

            return _REF.sub(repl, value)
        if isinstance(value, dict):
            return {k: self._resolve(v, context) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve(v, context) for v in value]
        return value

    def _summarize_output(self, result: Dict[str, Any]) -> str:
        if not result:
            return ""
        if result.get("response"):
            return str(result["response"])[:2000]
        if result.get("result"):
            r = result["result"]
            if isinstance(r, dict) and "output" in r:
                return str(r["output"])[:2000]
            return str(r)[:2000]
        if result.get("results"):
            return str(result["results"])[:2000]
        if result.get("code_samples"):
            return str(result["code_samples"])[:2000]
        if result.get("error"):
            return f"error: {result['error']}"
        return str(result)[:2000]

    async def run(
        self,
        workflow_yaml: str,
        inputs: Dict[str, Any],
        on_step: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute workflow nodes sequentially.

        on_step(name, status, output) may be an async callback for persistence.
        """
        workflow = self.load_workflow(workflow_yaml)
        nodes: List[Dict[str, Any]] = workflow.get("nodes", [])
        context: Dict[str, Any] = {"inputs": inputs}
        final_key = None
        outputs_cfg = workflow.get("outputs") or {}
        if isinstance(outputs_cfg, dict):
            final_key = outputs_cfg.get("reference")

        for node in nodes:
            name = node["name"]
            agent_type = node.get("agent_type") or node.get("type")
            raw_inputs = node.get("inputs") or {}
            resolved = self._resolve(raw_inputs, context)

            if on_step:
                await on_step(name, "processing", None)

            agent = self.agents.get(agent_type)
            if agent is None:
                err = f"Unknown agent_type: {agent_type}"
                logger.error(err)
                context[name] = {"status": "error", "error": err}
                if on_step:
                    await on_step(name, "failed", err)
                continue

            logger.info(f"Running node {name} via {agent_type}")
            try:
                result = await agent.execute(resolved)
            except Exception as e:
                logger.exception(f"Node {name} failed")
                result = {"status": "error", "error": str(e)}

            context[name] = result
            output_text = self._summarize_output(result)
            status = (
                "completed"
                if result.get("status", "success") != "error"
                else "failed"
            )
            if on_step:
                await on_step(name, status, output_text)

        final = context.get(final_key) if final_key else None
        summary = self._summarize_output(final) if final else self._summarize_output(
            context.get(nodes[-1]["name"], {}) if nodes else {}
        )
        return {"context": context, "result": summary, "final_node": final_key}
