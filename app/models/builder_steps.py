from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class StepType(Enum):
    CreateFile = 0
    CreateFolder = 1
    EditFile = 2
    DeleteFile = 3

class StepStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class FileStep(BaseModel):
    id: int
    title: str
    description: str
    type: int
    content: str
    path: str

class ReactResponse(BaseModel):
    steps: List[FileStep]
    error: str
    success: bool
