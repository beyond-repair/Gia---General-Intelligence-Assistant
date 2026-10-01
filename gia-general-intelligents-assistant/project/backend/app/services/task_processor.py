"""TaskProcessor — creates tasks and runs the default Gia workflow."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from ..models.task import Task, TaskStep
from ..schemas.task import TaskCreate
from .workflow_engine import WorkflowEngine

DEFAULT_WORKFLOW = """
desc: "Gia: General Intelligence Assistant Workflow"

outputs:
  reference: final_task_result

nodes:
  - name: understand_task
    type: agent
    agent_type: llm
    inputs:
      prompt: "Analyze this task and break it down into steps: ${inputs.input_text}"

  - name: gather_information
    type: agent
    agent_type: scraper
    inputs:
      description: ${understand_task.response}

  - name: search_github
    type: agent
    agent_type: github
    inputs:
      description: ${understand_task.response}
      language: python

  - name: generate_code
    type: agent
    agent_type: llm
    inputs:
      prompt: |
        Generate Python code to solve this task.
        Task description: ${understand_task.response}
        Available information: ${gather_information.results}
        GitHub examples: ${search_github.code_samples}

        Provide only the code, no explanations.

  - name: execute_code
    type: agent
    agent_type: code_execution
    inputs:
      code: ${generate_code.response}
      language: python

  - name: self_correct
    type: agent
    agent_type: llm
    inputs:
      prompt: |
        Review and optimize this code execution:
        Original task: ${inputs.input_text}
        Generated code: ${generate_code.response}
        Execution result: ${execute_code.result}

        If there are any errors or improvements needed, provide the corrected code.
        If the execution was successful, provide optimization suggestions.

  - name: final_task_result
    type: agent
    agent_type: llm
    inputs:
      prompt: |
        Summarize the task execution:
        Original task: ${inputs.input_text}
        Final code: ${self_correct.response}
        Execution results: ${execute_code.result}

        Provide a clear summary of what was accomplished and any notable results.
"""

STEP_DEFS = [
    ("understand_task", "Understand Task", "understand_task"),
    ("gather_information", "Gather Info", "gather_information"),
    ("search_github", "Search GitHub", "gather_information"),
    ("generate_code", "Generate Code", "generate_code"),
    ("execute_code", "Execute", "execute_code"),
    ("self_correct", "Optimize", "self_correct"),
    ("final_task_result", "Summarize", "self_correct"),
]


class TaskProcessor:
    def __init__(self, workflow_yaml: Optional[str] = None):
        self.workflow_yaml = workflow_yaml or DEFAULT_WORKFLOW
        self.engine = WorkflowEngine()

    def create_task(self, task_in: TaskCreate) -> Task:
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        task = Task(
            id=task_id,
            description=task_in.description,
            status="pending",
            result=None,
            created_at=now,
            updated_at=now,
        )
        steps: List[TaskStep] = []
        for idx, (node_name, display_name, step_type) in enumerate(STEP_DEFS):
            steps.append(
                TaskStep(
                    id=str(uuid.uuid4()),
                    task_id=task_id,
                    name=display_name,
                    status="pending",
                    type=step_type,
                    output=None,
                    order_index=idx,
                )
            )
        task.steps = steps
        # stash node name mapping for process_task
        task._node_names = [n[0] for n in STEP_DEFS]  # type: ignore[attr-defined]
        return task

    async def process_task(self, task: Task, session: Any = None) -> Task:
        """Run the workflow and update step statuses on the ORM task."""
        task.status = "processing"
        task.updated_at = datetime.now(timezone.utc)

        step_by_node: Dict[str, TaskStep] = {}
        for step, (node_name, _, _) in zip(task.steps, STEP_DEFS):
            step_by_node[node_name] = step

        async def on_step(name: str, status: str, output: Optional[str]) -> None:
            step = step_by_node.get(name)
            if step is None:
                return
            step.status = status
            if output is not None:
                step.output = output
            task.updated_at = datetime.now(timezone.utc)
            if session is not None:
                session.add(step)
                session.add(task)
                await session.commit()

        try:
            outcome = await self.engine.run(
                self.workflow_yaml,
                inputs={"input_text": task.description},
                on_step=on_step,
            )
            task.result = outcome.get("result") or ""
            failed = any(s.status == "failed" for s in task.steps)
            task.status = "failed" if failed else "completed"
        except Exception as e:
            logger.exception(f"Task {task.id} failed")
            task.status = "failed"
            task.result = f"error: {e}"

        task.updated_at = datetime.now(timezone.utc)
        return task
