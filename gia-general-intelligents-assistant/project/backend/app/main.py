from __future__ import annotations

from typing import List

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models.database import Base, async_session, engine
from .models.task import Task, TaskStep
from .schemas.task import TaskCreate, Task as TaskSchema
from .services.task_processor import TaskProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Gia - General Intelligence Assistant API",
    description=(
        "Claim-0 runnable prototype. Default agents are stubs "
        "(no torch / no remote LLM). Product AGI claims remain UNSUPPORTED."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_processor = TaskProcessor()


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "stub-default"}


@app.post("/tasks/", response_model=TaskSchema)
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    async with async_session() as session:
        db_task = task_processor.create_task(task)
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task, attribute_names=["steps"])

        background_tasks.add_task(process_task_background, db_task.id)
        return db_task


@app.get("/tasks/", response_model=List[TaskSchema])
async def get_tasks():
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.steps))
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())


@app.get("/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.steps))
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


async def process_task_background(task_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.steps))
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            return
        updated = await task_processor.process_task(task, session=session)
        session.add(updated)
        await session.commit()
