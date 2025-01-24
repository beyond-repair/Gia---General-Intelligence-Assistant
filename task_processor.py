import asyncio
from datetime import datetime
import uuid
import yaml
from typing import List, Optional, Dict, Any
from loguru import logger

from ..models.task import Task, TaskStep
from ..schemas.task import TaskCreate, TaskStepCreate
from .workflow_engine import WorkflowEngine
from .agents.llm_agent import LLMAgent
from .agents.scraper_agent import ScraperAgent
from .agents.github_agent import GitHubAgent
from .agents.code_execution_agent import CodeExecutionAgent


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


class TaskProcessor:
    def __init__(self):
        self.workflow_engine = WorkflowEngine() # Assuming WorkflowEngine is intended to be used
        self.workflow_config = yaml.safe_load(DEFAULT_WORKFLOW)
        self.agents = {
            "llm": LLMAgent(),
            "scraper": ScraperAgent(),
            "github": GitHubAgent(),
            "code_execution": CodeExecutionAgent(),
        }

    async def create_task(self, task_create: TaskCreate) -> Task:
        task_id = str(uuid.uuid4())
        steps = []
        for step_config in self.workflow_config['nodes']:
            step_id = str(uuid.uuid4())
            steps.append(TaskStep(
                id=step_id,
                task_id=task_id,
                step_type=step_config['type'], # Assuming 'type' in workflow config maps to step type
                name=step_config['name'],
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ))

        return Task(
            id=task_id,
            input_text=task_create.input_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="pending",
            steps=steps
        )

    async def process_task(self, task: Task) -> Task:
        logger.info(f"Processing task: {task.id}")
        task_context = {"inputs": {"input_text": task.input_text}}
        step_results = {}

        for step_config in self.workflow_config['nodes']:
            step_name = step_config['name']
            step_type = step_config['type']
            agent_type = step_config['agent_type']
            inputs = step_config['inputs']

            logger.info(f"Executing step: {step_name} (type: {step_type}, agent: {agent_type})")

            # Resolve inputs - very basic implementation, needs more robust templating
            resolved_inputs = {}
            for input_name, input_value_template in inputs.items():
                if isinstance(input_value_template, str) and "${" in input_value_template:
                    # Very basic template resolution - assumes format like ${node_name.output_name}
                    parts = input_value_template.strip("${}").split(".")
                    if len(parts) == 2:
                        source_node_name, output_name = parts
                        resolved_inputs[input_name] = step_results.get(source_node_name, {}).get(output_name)
                    else:
                        resolved_inputs[input_name] = input_value_template # Fallback if template is not resolved
                else:
                    resolved_inputs[input_name] = input_value_template

            agent = self.agents.get(agent_type)
            if agent:
                step_output = await agent.execute(resolved_inputs) # Execute agent
                step_results[step_name] = step_output # Store step results
                logger.info(f"Step '{step_name}' completed. Results: {step_output}")
            else:
                logger.warning(f"Agent type '{agent_type}' not found for step '{step_name}'. Skipping step.")

        final_result = step_results.get(self.workflow_config['outputs']['reference']) # Get final output
        task.status = "completed"
        task.updated_at = datetime.utcnow()
        # Assuming you want to store step results in TaskStep model, you'd need to add that logic here
        return task