from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TaskStepBase(BaseModel):
    name: str
    status: str
    type: str
    output: Optional[str] = None

class TaskStepCreate(TaskStepBase):
    pass

class TaskStep(TaskStepBase):
    id: str
    task_id: str

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    description: str
    status: str
    result: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime
    steps: List[TaskStep] = []

    class Config:
        from_attributes = True