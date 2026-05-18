# 1. Импорты
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from prometheus_client import Counter

# 2. Определение модели данных
class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None  # Исправлено: Optional вместо None
    completed: bool = False

# 3. Инициализация метрик Prometheus
HTTP_REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

# 4. СОЗДАНИЕ ЭКЗЕМПЛЯРА ПРИЛОЖЕНИЯ
app = FastAPI(title="Todo Service", description="API for managing todos")

# 5. Временное хранилище данных
tasks = [
    Task(id=1, title="Learn FastAPI", completed=False),
    Task(id=2, title="Deploy to Kubernetes", completed=False)
]

# 6. Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy", "service": "todo-service"}

# 7. Root endpoint
@app.get("/")
def root():
    return {"message": "Todo Service is running", "tasks_count": len(tasks)}

# 8. GET все задачи
@app.get("/tasks")
def get_tasks():
    HTTP_REQUESTS.labels(method="GET", endpoint="/tasks", status="200").inc()
    return tasks

# 9. GET задача по ID (НОВЫЙ ЭНДПОИНТ - ЭТОГО НЕ ХВАТАЛО)
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            HTTP_REQUESTS.labels(method="GET", endpoint=f"/tasks/{task_id}", status="200").inc()
            return task
    
    # Если задача не найдена
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

# 10. POST создать задачу
@app.post("/tasks")
def create_task(task: Task):
    # Проверка на дубликат ID
    if any(t.id == task.id for t in tasks):
        raise HTTPException(status_code=409, detail=f"Task with id {task.id} already exists")
    
    tasks.append(task)
    HTTP_REQUESTS.labels(method="POST", endpoint="/tasks", status="201").inc()
    return task

# 11. DELETE удалить задачу
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    # Ищем задачу по ID
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            HTTP_REQUESTS.labels(method="DELETE", endpoint="/tasks", status="200").inc()
            return {"deleted": task_id, "status": "success"}
    
    # Если задача не найдена
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")