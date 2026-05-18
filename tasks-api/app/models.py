from pydantic import BaseModel, Field

class Task(BaseModel):
    id: int = Field(..., gt=0, description="Task ID must be positive")
    title: str = Field(..., min_length=1, max_length=200)
    completed: bool = False