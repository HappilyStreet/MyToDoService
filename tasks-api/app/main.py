from fastapi import FastAPI
from typing import List
from app.models import Task
import os

app = FastAPI(title="Task API")

tasks: List[Task] = []

SERVICE_NAME = os.getenv("SERVICE_NAME", "task-api")
VERSION = os.getenv("VERSION", "1.0")

@app.get("/")
def root():
    return {
        "service": SERVICE_NAME,
        "version": VERSION
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    return {"deleted": task_id}