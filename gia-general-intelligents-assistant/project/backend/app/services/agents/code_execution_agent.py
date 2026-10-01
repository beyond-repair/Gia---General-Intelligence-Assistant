"""Code execution agent.

Default: runs a safe stub that does NOT eval untrusted code.
Set GIA_ALLOW_CODE_EXEC=1 to run Python via subprocess with a timeout
(still no Docker required for the default Claim-0 path).
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

from loguru import logger

from .base_agent import BaseAgent


class CodeExecutionAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.timeout = (config or {}).get("timeout", 10)

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        code = task_input.get("code") or ""
        language = task_input.get("language", "python")

        if not code:
            return {"status": "error", "error": "No code provided"}

        allow = os.getenv("GIA_ALLOW_CODE_EXEC", "").lower() in ("1", "true", "yes")
        if not allow:
            return {
                "status": "success",
                "mode": "stub",
                "language": language,
                "result": {
                    "output": (
                        "[stub] Code execution skipped "
                        "(set GIA_ALLOW_CODE_EXEC=1 to run locally).\n"
                        f"Would run {len(code)} chars of {language}."
                    ),
                    "exit_code": 0,
                    "execution_time": 0,
                },
            }

        if language != "python":
            return {"status": "error", "error": f"Unsupported language: {language}"}

        try:
            result = await self._run_python(code)
            return {"status": "success", "mode": "local", "language": language, "result": result}
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {"status": "error", "error": str(e)}

    async def _run_python(self, code: str) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "source.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            def _run():
                return subprocess.run(
                    [sys.executable, path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir,
                )

            completed = await asyncio.to_thread(_run)
            return {
                "output": (completed.stdout or "") + (completed.stderr or ""),
                "exit_code": completed.returncode,
                "execution_time": self.timeout,
            }
