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
    dummy_component = '''
    import React, { useState } from 'react';
import { TodoItem } from './TodoItem';
import { TodoList } from './TodoList';
import { Button } from '../ui/internal/Button';

export const TodoApp = () => {
  const [items, setItems] = useState<{ id: number; text: string; completed: boolean; }[]>([]);
  const [inputValue, setInputValue] = useState<string>('');

  const handleAddTodo = () => {
    if (!inputValue.trim()) return;
    const newTodo = { id: Date.now(), text: inputValue, completed: false };
    setItems([...items, newTodo]);
    setInputValue('');
  };

  const handleToggleTodo = (id: number) => {
    setItems(items.map(item => item.id === id ? { ...item, completed: !item.completed } : item));
  };

  const handleDeleteTodo = (id: number) => {
    setItems(items.filter(item => item.id !== id));
  };

  return (
    <div className="p-4">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Add a new task"
        className="border rounded p-2 mr-2"
      />
      <Button onClick={handleAddTodo} label="Add Todo" />
      <TodoList items={items} onToggle={handleToggleTodo} onDelete={handleDeleteTodo} />
    </div>
  );
};'''

    dummy_step = FileStep(
        id=1,
        title="Creating File src/components/DummyComponent.tsx",
        type=StepType.CreateFile.value,
        content=dummy_component,
        path="src/components/DummyComponent.tsx"
    )

    return ReactResponse(steps=[dummy_step])
