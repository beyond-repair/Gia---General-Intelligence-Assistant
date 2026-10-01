from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStepBase(BaseModel):
    name: str
    status: str
    type: str
    output: Optional[str] = None


class TaskStepCreate(TaskStepBase):
    pass


class TaskStep(TaskStepBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str


class TaskBase(BaseModel):
    description: str
    status: str = "pending"
    result: Optional[str] = None


class TaskCreate(BaseModel):
    description: str = Field(..., min_length=1)


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    steps: List[TaskStep] = []
