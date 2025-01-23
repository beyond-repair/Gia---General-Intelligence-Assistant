from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from datetime import datetime

from .models.database import engine, async_session, Base
from .models.task import Task, TaskStep
from .schemas.task import TaskCreate, Task as TaskSchema
from .services.task_processor import TaskProcessor

app = FastAPI(title="Gia - General Intelligence Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TaskProcessor
task_processor = TaskProcessor()

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/tasks/", response_model=TaskSchema)
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    async with async_session() as session:
        # Create task
        db_task = await task_processor.create_task(task)
        
        # Add to session
        session.add(db_task)
        for step in db_task.steps:
            session.add(step)
        
        await session.commit()
        await session.refresh(db_task)
        
        # Process task in background
        background_tasks.add_task(process_task_background, db_task.id)
        
        return db_task

@app.get("/tasks/", response_model=List[TaskSchema])
async def get_tasks():
    async with async_session() as session:
        result = await session.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC"
        )
        tasks = result.all()
        
        # Fetch steps for each task
        for task in tasks:
            steps_result = await session.execute(
                "SELECT * FROM task_steps WHERE task_id = :task_id",
                {"task_id": task.id}
            )
            task.steps = steps_result.all()
        
        return tasks

@app.get("/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: str):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

async def process_task_background(task_id: str):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if task:
            updated_task = await task_processor.process_task(task)
            session.add(updated_task)
            await session.commit()