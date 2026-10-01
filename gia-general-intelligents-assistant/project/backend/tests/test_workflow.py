import pytest

from app.services.task_processor import DEFAULT_WORKFLOW, TaskProcessor
from app.services.workflow_engine import WorkflowEngine
from app.schemas.task import TaskCreate


@pytest.mark.asyncio
async def test_workflow_engine_runs_stub_pipeline():
    engine = WorkflowEngine()
    outcome = await engine.run(
        DEFAULT_WORKFLOW,
        inputs={"input_text": "Write a hello world function"},
    )
    assert outcome["result"]
    assert "understand_task" in outcome["context"]
    assert outcome["context"]["understand_task"]["status"] == "success"
    assert outcome["context"]["execute_code"]["status"] == "success"


@pytest.mark.asyncio
async def test_task_processor_create_and_process():
    processor = TaskProcessor()
    task = processor.create_task(TaskCreate(description="demo hello"))
    assert task.status == "pending"
    assert len(task.steps) == 7
    updated = await processor.process_task(task)
    assert updated.status == "completed"
    assert updated.result
    assert all(s.status == "completed" for s in updated.steps)
