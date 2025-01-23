import asyncio
from datetime import datetime
import uuid
import yaml
from typing import List, Optional, Dict, Any
from loguru import logger
from ..models.task import Task, TaskStep
from ..schemas.task import TaskCreate, TaskStepCreate
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

# ... rest of the file remains the same ...