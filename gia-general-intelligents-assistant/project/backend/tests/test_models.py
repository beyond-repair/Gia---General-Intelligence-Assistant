import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.database import Base, async_session, engine
from app.models.task import Task, TaskStep


@pytest.mark.asyncio
async def test_task_and_step_persist():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task_id = str(uuid.uuid4())
    step_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    async with async_session() as session:
        task = Task(
            id=task_id,
            description="demo task",
            status="pending",
            created_at=now,
            updated_at=now,
        )
        step = TaskStep(
            id=step_id,
            task_id=task_id,
            name="Understand Task",
            status="pending",
            type="understand_task",
            order_index=0,
        )
        task.steps = [step]
        session.add(task)
        await session.commit()

    async with async_session() as session:
        result = await session.execute(
            select(Task).options(selectinload(Task.steps)).where(Task.id == task_id)
        )
        loaded = result.scalar_one()
        assert loaded.description == "demo task"
        assert len(loaded.steps) == 1
        assert loaded.steps[0].name == "Understand Task"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
