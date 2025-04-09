from pydantic import BaseModel, Field
from typing import Optional, List

class FileNode(BaseModel):
    fileName: str
    filePath: str
    fileContent: str

class InternalComponent(BaseModel):
    path: str
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    useCase: Optional[str] = None
    codeSamples: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    inputProps: str
