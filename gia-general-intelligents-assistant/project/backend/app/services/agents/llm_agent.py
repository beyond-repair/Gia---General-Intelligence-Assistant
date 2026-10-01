"""LLM agent.

Default path is a deterministic stub (no torch / no model download).
Set GIA_USE_REAL_LLM=1 to attempt loading a local transformers model
(requires optional extras: torch, transformers).
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from loguru import logger

from .base_agent import BaseAgent


class LLMAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mode = "stub"
        self.model_name = "stub-deterministic"
        self._model = None
        self._tokenizer = None

        if os.getenv("GIA_USE_REAL_LLM", "").lower() in ("1", "true", "yes"):
            self._try_load_real_model()

    def _try_load_real_model(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.model_name = os.getenv(
                "GIA_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading real LLM {self.model_name} on {device}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto",
            )
            self.mode = "real"
            self.device = device
        except Exception as e:
            logger.warning(f"Real LLM unavailable, using stub: {e}")
            self.mode = "stub"

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task_input.get("prompt", "")
        if not prompt:
            return {"status": "error", "error": "No prompt provided"}

        if self.mode == "real" and self._model is not None:
            return await self._execute_real(prompt)

        return self._execute_stub(prompt, task_input)

    def _execute_stub(
        self, prompt: str, task_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deterministic structured response for demo / tests."""
        lower = prompt.lower()
        context_bits = []
        for key in ("description", "input_text"):
            if key in task_input and task_input[key]:
                context_bits.append(str(task_input[key]))
        context = " ".join(context_bits) or prompt[:200]

        # Order matters: later workflow prompts may embed earlier stub text.
        if "summarize the task" in lower or lower.strip().startswith("summarize"):
            response = (
                f"[stub] Summary: completed demo pipeline for '{context[:100]}'. "
                "Agents ran in stub mode (no remote LLM)."
            )
        elif "break it down" in lower or "analyze this task" in lower:
            response = (
                f"[stub] Task analysis for: {context[:120]}\n"
                "1. Clarify goal\n"
                "2. Gather context\n"
                "3. Draft solution\n"
                "4. Validate output"
            )
        elif "generate python code" in lower or "provide only the code" in lower:
            response = (
                "# [stub] generated demo solution\n"
                f"def solve():\n"
                f'    """Demo solution for: {context[:80]}"""\n'
                f'    return {{"ok": True, "summary": "stub completed"}}\n'
                "\n"
                "if __name__ == '__main__':\n"
                "    print(solve())\n"
            )
        elif "review and optimize" in lower or "corrected code" in lower:
            response = (
                "[stub] Review: execution succeeded in demo mode. "
                "No corrections required. Suggestion: add unit tests."
            )
        else:
            response = f"[stub] Response to prompt ({len(prompt)} chars): {prompt[:240]}"

        return {
            "status": "success",
            "response": response,
            "model": self.model_name,
            "mode": self.mode,
        }

    async def _execute_real(self, prompt: str) -> Dict[str, Any]:
        import torch

        formatted = f"<s>[INST] {prompt} [/INST]"
        inputs = self._tokenizer(formatted, return_tensors="pt").to(self.device)
        outputs = self._model.generate(
            inputs["input_ids"],
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            pad_token_id=self._tokenizer.eos_token_id,
        )
        text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = text.split("[/INST]")[-1].strip()
        return {
            "status": "success",
            "response": response,
            "model": self.model_name,
            "mode": self.mode,
            "device": self.device,
        }

    async def cleanup(self):
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        logger.info("LLM Agent cleaned up")
