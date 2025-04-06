from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StepType(Enum):
    CreateFile = 0
    CreateFolder = 1
    EditFile = 2
    DeleteFile = 3
    TextDisplay = 4

class StepStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class FileStep(BaseModel):
    id: int = Field(..., description="Unique identifier for the file step.")
    title: str = Field(..., description="Title of the file step. Example Creating File src/App.tsx")
    type: int = Field(..., description="Type of the step, represented as an integer.")
    content: str = Field(..., description="Code associated with the file.")
    path: str = Field(..., description="Full file path")

class ReactResponse(BaseModel):
    steps: list[FileStep] = Field(..., description="List of file steps involved in the response.")
    # error: str = Field(..., description="Error message if the response failed.")
    # success: bool = Field(..., description="Indicates if the response was successful.")

def get_dummy_response() -> ReactResponse:
    """Generate a dummy ReactResponse for testing purposes."""
    dummy_component = '''import React from 'react';

const DummyComponent = () => {
    return (
        <div className="dummy-container">
            <h1>Hello from Dummy Component</h1>
            <p>This is a sample component for testing purposes.</p>
            <button className="dummy-button">Click Me!</button>
        </div>
    );
};

export default DummyComponent;'''

    dummy_step = FileStep(
        id=1,
        title="Creating File src/components/DummyComponent.tsx",
        type=StepType.CreateFile.value,
        content=dummy_component,
        path="src/components/DummyComponent.tsx"
    )

    return ReactResponse(steps=[dummy_step])
