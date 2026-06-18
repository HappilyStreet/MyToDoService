from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Автоматически добавляет эндпоинт /metrics
Instrumentator().instrument(app).expose(app)

todos = []

@app.get("/tasks")
def get_tasks():
    return todos

@app.post("/tasks")
def add_task(data: dict):
    todos.append(data)
    return data

@app.delete("/tasks/{index}")
def delete_task(index: int):
    if 0 <= index < len(todos):
        task = todos.pop(index)
        return task
    return {"error": "Not found"}, 404